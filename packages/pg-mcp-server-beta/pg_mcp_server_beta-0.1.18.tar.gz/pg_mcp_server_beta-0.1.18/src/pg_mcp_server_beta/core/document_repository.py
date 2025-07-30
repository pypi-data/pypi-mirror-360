import re
from typing import Any

from .search_engine import DocumentChunk, HectoSearchEngine
from .utils.category_utils import extract_category
from .utils.markdown_utils import (
    md_split_to_sections,
)


def extract_tags(content: str) -> list[str]:
    tag_patterns = [r"#([\w가-힣]+)", r"\[([\w가-힣]+)\]"]
    tags = set()
    for pattern in tag_patterns:
        tags.update(re.findall(pattern, content))
    return list(tags)

def format_doc_meta(doc: dict[str, Any]) -> dict[str, Any]:
    """
    문서 메타 정보를 일관된 dict로 반환하는 헬퍼 함수.
    '문서ID'는 항상 str로 반환.
    """
    return {
        "문서ID": str(doc.get("id")) if doc.get("id") is not None else None,
        "제목": doc.get("title"),
        "카테고리": doc.get("category"),
        "파일명": doc.get("filename"),
        "태그": doc.get("tags", []),
    }

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
            sections = md_split_to_sections(content)
            for section in sections:
                # 기존과 동일하게 context를 [헤딩 > ...]로 조합
                context_str = f"[{ ' > '.join(section.context) }]" if section.context else "[]"
                section_text = context_str + "\n" + section.body
                word_count = len(section_text.split())
                if word_count > 0:
                    chunks.append(DocumentChunk(
                        id=len(chunks),
                        text=section_text,
                        word_count=word_count,
                        origin_title=rel_path,
                        filename=rel_path,
                        category=category
                    ))
        return chunks

    def list_documents(
        self,
        sort_by: str = "id",
        order: str = "asc",
        category: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """
        문서 목록을 정렬/필터/페이징하여 반환.
        """
        docs = self.documents
        # 카테고리 필터
        if category:
            docs = [doc for doc in docs if doc.get("category") == category]
        # 정렬
        reverse = order == "desc"
        docs = sorted(docs, key=lambda d: d.get(sort_by, ""), reverse=reverse)
        # 페이징
        start = (page - 1) * page_size
        end = start + page_size
        docs = docs[start:end]
        return [format_doc_meta(doc) for doc in docs]

    def get_document_by_id(self, doc_id: int) -> str | None:
        if 0 <= doc_id < len(self.documents):
            return self._load_document_content(self.documents[doc_id]["filename"])
        return None

    def _load_document_content(self, filename: str) -> str | None:
        return self._documents_raw.get(filename)

    def search_documents(self, keywords: list[str], category: str | None = None) -> dict[str, Any]:
        """
        검색어와 카테고리로 문서 검색. 결과는 {'meta': 문서 메타, 'content': 본문} 구조로 반환.
        """
        query = " ".join(keywords)
        scored_results = self.search_engine.calculate(query)
        entries = []
        for result in scored_results:
            chunk = self.search_engine.get_chunk_by_id(result.id)
            if not chunk:
                continue
            doc_meta = next((doc for doc in self.documents if doc["filename"] == chunk.filename), {})
            # 카테고리 필터
            if category and chunk.category != category:
                continue
            content = chunk.text
            entries.append({
                "meta": doc_meta,
                "content": content
            })
        return {
            "검색어": keywords,
            "검색결과": entries,
            "안내": "관련성이 높은 문서 섹션을 정렬하여 제공합니다.",
        }

_repository: HectoDocumentRepository | None = None

def initialize_repository(documents: dict[str, str]) -> None:
    global _repository
    _repository = HectoDocumentRepository(documents)

def get_repository() -> HectoDocumentRepository:
    if _repository is None:
        raise RuntimeError("문서 저장소가 초기화되지 않았습니다. initialize_repository(documents)를 먼저 호출하세요.")
    return _repository
