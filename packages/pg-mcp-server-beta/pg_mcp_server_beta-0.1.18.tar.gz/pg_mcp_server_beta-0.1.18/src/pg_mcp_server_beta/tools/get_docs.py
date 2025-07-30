from typing import Any

from ..core.document_repository import format_doc_meta, get_repository


def get_docs(doc_id: str = "1") -> dict[str, Any]:
    """
    문서 ID(정수 문자열) 또는 파일 경로(문자열)로
    헥토파이낸셜 연동 문서의 원문 전체를 반환합니다.

    Args:
        doc_id (str): 문서 ID (예: "1", "2") 또는 파일 경로 (예: "pg/hecto_financial_pg.md")

    Returns:
        dict: {
            "문서ID": str,       # 요청한 문서 식별자
            "내용": str,         # 마크다운 원문 전체
            "안내": str          # 안내 메시지
        }

        ※ 유효하지 않은 ID/경로일 경우 {"안내": "..."} 또는 {"오류": "..."} 형태로 반환
    """
    try:
        repository = get_repository()

        # doc_id가 int로 들어와도 str로 변환
        doc_id = str(doc_id)

        # 1. 숫자 ID로 조회 시도
        if doc_id.isdigit():
            content = repository.get_document_by_id(int(doc_id))
        else:
            # 2. 파일 경로로 직접 검색
            doc_meta = next((doc for doc in repository.documents if doc["filename"] == doc_id), None)
            content = repository._load_document_content(doc_id) if doc_meta else None

        if not content:
            return {
                "안내": f"문서 ID 또는 경로 '{doc_id}'에 해당하는 문서를 찾을 수 없습니다."
            }

        # 문서 메타 정보도 함께 반환 (문서ID, 제목, 카테고리 등)
        doc_meta = next((doc for doc in repository.documents if str(doc.get("id")) == doc_id or doc.get("filename") == doc_id), None)
        meta_info = format_doc_meta(doc_meta) if doc_meta else {"문서ID": doc_id}
        meta_info["내용"] = content
        meta_info["안내"] = "해당 문서의 전체 내용을 반환합니다."
        return meta_info

    except Exception as e:
        return {
            "오류": f"문서 조회 중 오류가 발생했습니다: {e}"
        }
