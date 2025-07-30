import itertools
import re
from dataclasses import dataclass

from .utils.bm25_utils import BM25Params, bm25_score
from .utils.category_utils import extract_category
from .utils.markdown_utils import (
    _extract_text_from_ast,
    _list_ast_to_markdown,
    _table_ast_to_markdown,
    convert_numbered_headings,
    parse_markdown_to_ast,
)


@dataclass
class DocumentChunk:
    id: int
    text: str
    word_count: int
    origin_title: str
    filename: str
    category: str

@dataclass
class SearchResult:
    id: int
    score: float
    total_tf: int

def build_context(ctx_stack, last_level2):
    # 계층을 그대로 반환 (중복 제거는 유지)
    # ['A', 'A'] → ['A']
    if len(ctx_stack) == 2 and ctx_stack[0] == ctx_stack[1]:
        return [ctx_stack[0]]
    if len(ctx_stack) == 2 and ctx_stack[0] in ctx_stack[1]:
        return [ctx_stack[1]]
    if len(ctx_stack) == 1 and last_level2:
        if last_level2 == ctx_stack[0]:
            return [ctx_stack[0]]
        if last_level2 in ctx_stack[0]:
            return [ctx_stack[0]]
        return [last_level2, ctx_stack[0]]
    return ctx_stack.copy()

class HectoSearchEngine:
    def __init__(self, documents, k1=1.2, b=0.75, min_words=10, window_size=5):
        self.k1 = k1
        self.b = b
        self.min_words = min_words
        self.window_size = window_size
        self.all_chunks = self._create_chunks_from_docs(documents)
        self.total_count = sum(chunk.word_count for chunk in self.all_chunks)
        self.average_doc_length = self.total_count / len(self.all_chunks) if self.all_chunks else 0
        self.N = len(self.all_chunks)

    def _create_chunks_from_docs(self, documents) -> list[DocumentChunk]:
        chunks = []
        for rel_path, content in documents.items():
            if not rel_path.endswith('.md'):
                continue
            category = extract_category(rel_path)
            sections = self._split_into_sections(content, self.min_words, self.window_size)
            for section in sections:
                word_count = len(section.split())
                if word_count > 0:
                    chunks.append(DocumentChunk(
                        id=len(chunks),
                        text=section,
                        word_count=word_count,
                        origin_title=rel_path,
                        filename=rel_path,
                        category=category
                    ))
        return chunks

    def _split_into_sections(self, content: str, min_words: int = 30, window_size: int = 1) -> list[str]:
        content = convert_numbered_headings(content)
        ast = parse_markdown_to_ast(content)
        sections = []
        context_stack = []
        buffer = []
        for node in ast:
            if not isinstance(node, dict):
                continue
            if node.get("type") == "heading":
                # 청크 flush
                if buffer:
                    context = build_context(context_stack, None)
                    sections.append(f"[{ ' > '.join(context) }]\n" + "\n".join(buffer))
                    buffer = []
                # 헤딩 텍스트 추출
                heading_text = "".join([c.get('raw', '') for c in node.get('children', []) if isinstance(c, dict)])
                level = node.get('attrs', {}).get('level')
                # 계층적으로 context_stack 쌓기 (h1~h6)
                if level is not None:
                    # level: 1(h1)~6(h6)
                    # context_stack 길이 맞추기
                    context_stack = context_stack[:level-1] + [heading_text]
            elif node.get("type") == "table":
                buffer.append(_table_ast_to_markdown(node))
            elif node.get("type") == "list":
                buffer.append(_list_ast_to_markdown(node))
            elif node.get("type") == "block_code":
                info = node.get("info")
                code = node.get("text", "")
                buffer.append(f"```{info}\n{code}\n```" if info else f"```\n{code}\n```")
            elif node.get("type") == "paragraph":
                buffer.append(_extract_text_from_ast(node.get("children", [])))
            elif node.get("type") == "text":
                buffer.append(node.get("text", ""))
        # 마지막 flush
        if buffer:
            context = build_context(context_stack, None)
            sections.append(f"[{ ' > '.join(context) }]\n" + "\n".join(buffer))
        return sections

    def calculate(self, query: str) -> list[SearchResult]:
        if not self.all_chunks:
            return []

        raw_keywords = [k for k in re.split(r'[ ,|]+', query) if k]
        keywords = set(raw_keywords)
        for k in raw_keywords:
            if re.match(r'[가-힣 ]+', k):
                keywords.add(k.replace(' ', ''))
                keywords.update(k.split())
        max_comb_length = 3
        for r in range(2, min(len(raw_keywords), max_comb_length) + 1):
            for comb in itertools.combinations(raw_keywords, r):
                keywords.add(''.join(comb))

        keywords = list(keywords)
        term_frequencies, doc_frequencies = self._calculate_frequencies(keywords)
        scores = self._calculate_score(term_frequencies, doc_frequencies, keywords)
        filtered_scores = [s for s in scores if s.total_tf > 0]
        filtered_scores.sort(key=lambda x: (-x.score, -x.total_tf))
        return filtered_scores

    def _calculate_frequencies(self, keywords: list[str]) -> tuple[dict[int, dict[str, int]], dict[str, int]]:
        term_frequencies = {}
        doc_frequencies = {}
        for chunk in self.all_chunks:
            term_counts = {}
            for keyword in keywords:
                if re.match(r'[가-힣]+', keyword):
                    text = chunk.text.replace(' ', '').lower()
                    k = keyword.replace(' ', '').lower()
                else:
                    text = chunk.text.lower()
                    k = keyword.lower()
                count = text.count(k)
                if count > 0:
                    term_counts[keyword] = count
            if term_counts:
                term_frequencies[chunk.id] = term_counts
                for term in term_counts:
                    doc_frequencies[term] = doc_frequencies.get(term, 0) + 1
        return term_frequencies, doc_frequencies

    def _calculate_score(self, term_frequencies: dict[int, dict[str, int]], doc_frequencies: dict[str, int], keywords: list[str] | None = None) -> list[SearchResult]:
        params = BM25Params(
            k1=self.k1,
            b=self.b,
            average_doc_length=self.average_doc_length,
            n=self.N
        )
        if keywords is None:
            keywords = []
        bm25_results = bm25_score(term_frequencies, doc_frequencies, self.all_chunks, params, keywords)
        # BM25Result -> SearchResult 변환
        return [SearchResult(id=r.id, score=r.score, total_tf=r.total_tf) for r in bm25_results]

    def get_chunk_by_id(self, chunk_id: int) -> DocumentChunk | None:
        if 0 <= chunk_id < len(self.all_chunks):
            return self.all_chunks[chunk_id]
        return None

    def highlight_terms(self, chunk_text: str, keywords: list[str]) -> str:
        def replacer(match):
            word = match.group(0)
            return word if word.startswith('**') and word.endswith('**') else f'**{word}**'

        for keyword in sorted(keywords, key=len, reverse=True):
            if re.match(r'[가-힣]+', keyword):
                pattern = re.compile(rf'(?<!\*){re.escape(keyword)}(?!\*)', re.IGNORECASE)
            else:
                pattern = re.compile(rf'(?<!\*)\b{re.escape(keyword)}\b(?!\*)', re.IGNORECASE)
            chunk_text = pattern.sub(replacer, chunk_text)
        return chunk_text
