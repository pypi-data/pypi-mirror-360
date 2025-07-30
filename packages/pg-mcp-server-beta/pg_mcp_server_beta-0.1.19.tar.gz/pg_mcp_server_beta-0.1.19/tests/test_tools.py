from typing import Any, cast

import pytest

from pg_mcp_server_beta.core import documents

# 문서 저장소 초기화용 import
from pg_mcp_server_beta.core.document_repository import initialize_repository
from pg_mcp_server_beta.core.utils.markdown_utils import (
    HeadingContextTracker,
    MarkdownChunkFormatter,
    Section,
    SectionSplitter,
)
from pg_mcp_server_beta.tools.get_docs import get_docs
from pg_mcp_server_beta.tools.list_docs import list_docs
from pg_mcp_server_beta.tools.search_docs import search_docs


@pytest.fixture(autouse=True, scope="module")
def setup_docs_repository():
    initialize_repository(documents)

def test_list_docs_basic():
    result = cast(dict[str, Any], list_docs())
    assert isinstance(result, dict)
    assert "문서목록" in result
    assert len(result["문서목록"]) > 0


def test_get_docs_valid_and_invalid():
    docs = cast(dict[str, Any], list_docs())["문서목록"]
    if docs:
        valid_id = docs[0]["문서ID"]
        result = get_docs(doc_id=valid_id)
        assert "문서ID" in result
        assert result["문서ID"] == str(valid_id)
    result = get_docs(doc_id="999999")
    assert "안내" in result or "오류" in result


@pytest.mark.parametrize("query", [
    "결제", "내통장 결제", "내통장!@# 결제$", "ezauth", "EZAUTH", "없는키워드123", "내통", ""
])
def test_search_docs_various(query):
    result = search_docs(query)
    assert isinstance(result, dict)
    assert "검색결과" in result or "안내" in result or "오류" in result


def test_search_docs_case_insensitive():
    lower = search_docs("ezauth")
    upper = search_docs("EZAUTH")
    if "검색결과" in lower and "검색결과" in upper:
        assert lower["검색결과"] == upper["검색결과"]
    else:
        assert lower.get("안내") == upper.get("안내")


def test_tools_return_json_and_handle_exceptions():
    assert isinstance(list_docs(), dict)
    assert isinstance(get_docs("1"), dict)
    assert isinstance(search_docs("테스트"), dict)
    assert isinstance(get_docs("999"), dict)
    assert isinstance(search_docs(""), dict)


def test_section_splitter_basic():
    md = """
# 제목1
본문1
## 1.1 소제목
본문2
- 리스트1
- 리스트2
| 헤더 | 값 |
| --- | --- |
| a | b |
"""
    splitter = SectionSplitter()
    sections = splitter.split(md)
    assert isinstance(sections, list)
    assert all(isinstance(s, Section) for s in sections)
    assert any("제목1" in " ".join(s.context) for s in sections)
    assert any("소제목" in " ".join(s.context) for s in sections)
    assert any("본문1" in s.body or "본문2" in s.body for s in sections)

def test_heading_context_tracker():
    tracker = HeadingContextTracker()
    tracker.update("제목1", 1)
    assert tracker.get_context() == ["제목1"]
    tracker.update("소제목", 2)
    assert tracker.get_context()[-1] == "소제목"
    tracker.update("소제목2", 2)
    assert tracker.get_context()[-1] == "소제목2"

def test_markdown_chunk_formatter():
    formatter = MarkdownChunkFormatter()
    ast = [
        {"type": "paragraph", "children": [{"type": "text", "text": "문단1"}]},
        {"type": "list", "children": [
            {"type": "list_item", "children": [{"type": "text", "text": "항목1"}]},
            {"type": "list_item", "children": [{"type": "text", "text": "항목2"}]}
        ], "ordered": False}
    ]
    para = formatter.extract_text(ast[0]["children"])
    assert "문단1" in para
    lst = formatter.list_to_markdown(ast[1])
    assert "항목1" in lst and "항목2" in lst

if __name__ == "__main__":
    # 간단한 테스트 실행
    print("=== 헥토파이낸셜 MCP 도구 테스트 ===")

    # 문서 목록 테스트
    print("\n1. 문서 목록 조회 테스트")
    list_result = list_docs()
    print(f"결과: {str(list_result)[:200]}...")

    # 문서 조회 테스트
    print("\n2. 문서 조회 테스트")
    fetch_result = get_docs(doc_id="1")
    print(f"결과: {str(fetch_result)[:200]}...")

    # 검색 테스트
    print("\n3. 검색 테스트")
    search_result = search_docs(query="결제")
    print(f"결과: {str(search_result)[:200]}...")

    print("\n=== 테스트 완료 ===")
