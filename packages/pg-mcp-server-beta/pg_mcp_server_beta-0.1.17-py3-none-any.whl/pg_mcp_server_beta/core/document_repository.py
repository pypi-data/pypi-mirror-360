import re
from typing import Any

from .search_engine import DocumentChunk, HectoSearchEngine
from .utils.category_utils import extract_category
from .utils.markdown_utils import (
    _extract_text_from_ast,
    _list_ast_to_markdown,
    _table_ast_to_markdown,
    convert_numbered_headings,
    parse_markdown_to_ast,
)


def extract_tags(content: str) -> list[str]:
    tag_patterns = [r"#([\w가-힣]+)", r"\[([\w가-힣]+)\]"]
    tags = set()
    for pattern in tag_patterns:
        tags.update(re.findall(pattern, content))
    return list(tags)

def build_context(ctx_stack, last_level2):
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

class HectoDocumentRepository:
    def __init__(self, documents: dict[str, str]):
        self._documents_raw = documents
        self.documents = self._build_metadata(documents)
        self.chunks = self._build_chunks(documents)
        self.search_engine = HectoSearchEngine(self.chunks)

    def _build_metadata(self, documents: dict[str, str]) -> list[dict[str, Any]]:
        doc_list = []
        for i, (filename, content) in enumerate(documents.items()):
            if not (filename.endswith(".md") or filename.endswith(".js")):
                continue
            title = next((line.strip() for line in content.splitlines() if line.strip()), filename)
            doc_list.append({
                "id": i,
                "filename": filename,
                "title": title,
                "category": extract_category(filename),
                "tags": extract_tags(content),
            })
        return doc_list

    def _build_chunks(self, documents: dict[str, str]) -> list[DocumentChunk]:
        chunks = []
        for rel_path, content in documents.items():
            if not rel_path.endswith('.md'):
                continue
            category = extract_category(rel_path)
            sections = self._split_into_sections(content)
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
                if buffer:
                    context = build_context(context_stack, None)
                    sections.append(f"[{ ' > '.join(context) }]\n" + "\n".join(buffer))
                    buffer = []
                heading_text = "".join([c.get('raw', '') for c in node.get('children', []) if isinstance(c, dict)])
                level = node.get('attrs', {}).get('level')
                if level is not None:
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
        if buffer:
            context = build_context(context_stack, None)
            sections.append(f"[{ ' > '.join(context) }]\n" + "\n".join(buffer))
        return sections

    def list_documents(self) -> list[dict[str, Any]]:
        return self.documents

    def get_document_by_id(self, doc_id: int) -> str | None:
        if 0 <= doc_id < len(self.documents):
            return self._load_document_content(self.documents[doc_id]["filename"])
        return None

    def _load_document_content(self, filename: str) -> str | None:
        return self._documents_raw.get(filename)

    def search_documents(self, keywords: list[str], top_n: int = 20, window: int = 3, category=None) -> dict[str, Any]:
        if not keywords:
            return {"안내": "검색 키워드를 입력해 주세요."}

        query = " ".join(keywords)
        self.search_engine.window_size = window
        scored_results = self.search_engine.calculate(query)

        if not scored_results:
            return {"안내": f"'{', '.join(keywords)}'에 대한 검색 결과가 없습니다."}

        highlight_keywords = sorted(keywords, key=len, reverse=True)

        # 카테고리 필터링
        def normalize_cat(cat):
            return cat.lower().replace(' ', '') if isinstance(cat, str) else cat
        if category is not None:
            if isinstance(category, str):
                categories = [category]
            else:
                categories = list(category)
            categories = [normalize_cat(c) for c in categories]
        else:
            categories = None

        result_list = []
        seen_contents = set()
        for result in scored_results:
            chunk = self.search_engine.get_chunk_by_id(result.id)
            if not chunk:
                continue
            doc_meta = next((d for d in self.documents if d["filename"] == chunk.filename), {})
            cat = normalize_cat(chunk.category)
            if categories is not None and cat not in categories:
                continue
            category_val = chunk.category
            meta_info = f"### 문서 제목: {doc_meta.get('title', chunk.filename)}\n* 문서 ID: {chunk.filename}\n* 카테고리: {category_val}\n"
            content = self.search_engine.highlight_terms(chunk.text, highlight_keywords)
            content_body = "\n".join(content.splitlines()[1:]).strip()
            if content_body in seen_contents:
                continue
            seen_contents.add(content_body)
            entry = f"{meta_info}\n{content}"
            result_list.append(entry)
            if len(result_list) >= top_n:
                break

        if not result_list:
            return {"안내": f"'{', '.join(keywords)}'에 대한 검색 결과가 없습니다."}

        # 카테고리 우선 노출 로직: 검색어에 카테고리명이 포함되어 있으면 해당 카테고리 결과를 먼저 배치
        def normalize(text):
            return text.lower().replace(' ', '')
        # 모든 카테고리명 추출 및 정규화
        all_categories = {d['category'] for d in self.documents}
        category_map = {normalize(cat): cat for cat in all_categories}
        norm_query = normalize(query)
        matched_category = None
        for norm_cat, orig_cat in category_map.items():
            if norm_cat and norm_cat in norm_query:
                matched_category = orig_cat
                break
        if matched_category:
            # 해당 카테고리 결과 먼저, 나머지 뒤에
            cat_results = [entry for entry in result_list if f'* 카테고리: {matched_category}\n' in entry]
            other_results = [entry for entry in result_list if f'* 카테고리: {matched_category}\n' not in entry]
            result_list = cat_results + other_results

        return {"검색결과": result_list}

_repository: HectoDocumentRepository | None = None

def initialize_repository(documents: dict[str, str]) -> None:
    global _repository
    _repository = HectoDocumentRepository(documents)

def get_repository() -> HectoDocumentRepository:
    if _repository is None:
        raise RuntimeError("문서 저장소가 초기화되지 않았습니다. initialize_repository(documents)를 먼저 호출하세요.")
    return _repository
