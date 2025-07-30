from pg_mcp_server_beta.core import documents
from pg_mcp_server_beta.core.document_repository import HectoDocumentRepository


def test_repository_creation_and_loading():
    repo = HectoDocumentRepository(documents)
    assert repo is not None
    assert hasattr(repo, "documents")
    assert hasattr(repo, "search_engine")
    assert len(repo.documents) > 0
    for doc in repo.documents:
        assert "filename" in doc
        assert "title" in doc
        assert "category" in doc
        assert "tags" in doc
        assert "id" in doc

def test_list_documents():
    repo = HectoDocumentRepository(documents)
    docs = repo.list_documents()
    assert isinstance(docs, list)
    assert len(docs) > 0
    assert docs == repo.documents

def test_get_document_by_id():
    repo = HectoDocumentRepository(documents)
    if repo.documents:
        content = repo.get_document_by_id(0)
        assert content is None or isinstance(content, str)
    assert repo.get_document_by_id(-1) is None
    assert repo.get_document_by_id(999) is None

def test_search_documents():
    repo = HectoDocumentRepository(documents)
    result = repo.search_documents(["결제"])
    assert isinstance(result, dict)
    assert "검색결과" in result or "안내" in result or "카테고리별검색결과" in result
    result = repo.search_documents([])
    assert isinstance(result, dict)
    assert "안내" in result
    result = repo.search_documents(["결제", "연동"])
    assert isinstance(result, dict)
    assert "검색결과" in result or "안내" in result or "카테고리별검색결과" in result

def test_repository_integration_and_error():
    repo = HectoDocumentRepository(documents)
    docs = repo.list_documents()
    assert len(docs) > 0
    if docs:
        content = repo.get_document_by_id(0)
        assert content is None or isinstance(content, str)
    search_result = repo.search_documents(["테스트"])
    assert isinstance(search_result, dict)
    assert "검색결과" in search_result or "안내" in search_result or "카테고리별검색결과" in search_result
    assert repo.get_document_by_id(-1) is None
    assert "안내" in repo.search_documents([])
