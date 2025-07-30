from ..core.document_repository import get_repository


def list_docs(sort_by: str = "id", order: str = "asc", category: str | None = None, page: int = 1, page_size: int = 20) -> dict[str, object]:
    """
    문서 목록을 정렬/필터/페이징하여 반환.

    Returns:
        dict: {
            "문서목록": [
                {
                    "문서ID": int,         # 문서 고유 ID
                    "제목": str,           # 문서 제목
                    "카테고리": str,       # 자동 분류된 카테고리
                    "파일명": str,         # 문서 파일 경로
                    "태그": list[str],     # 문서 내 추출된 태그 목록
                },
                ...
            ],
            "안내": str  # 전체 문서 안내 메시지
        }

        ※ 오류 발생 시 {"오류": "..."} 형태로 반환됩니다.
    """
    try:
        repository = get_repository()
        documents = repository.list_documents(
            sort_by=sort_by,
            order=order,
            category=category,
            page=page,
            page_size=page_size,
        )
        docs_list = list(documents)
        return {
            "문서목록": docs_list,
            "안내": "문서 ID를 참고해 get_docs로 상세 내용을 확인할 수 있습니다.",
        }
    except Exception as e:
        return {
            "오류": f"문서 목록 처리 중 문제가 발생했습니다: {e}"
        }
