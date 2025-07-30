import re

from ..core.document_repository import get_repository


def search_docs(query: str) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서에서 키워드 기반 검색을 수행합니다.

    Args:
        query (str): 쉼표 또는 공백으로 구분된 키워드 문자열

    Returns:
        dict:
            {
                "검색어": list[str],     # 분리된 키워드 목록
                "검색결과": list[str],   # 관련 문서 청크(마크다운)
                "안내": str              # 검색 결과 요약 또는 안내 메시지
            }

        ※ 검색 실패 시 {"안내": "..."} 또는 {"오류": "..."} 형식으로 반환
    """
    if not query:
        return {
            "안내": "검색어를 입력해 주세요. 예: '내통장 결제', '신용카드', '계좌이체' 등",
        }

    try:
        # 키워드 분리: 쉼표 또는 공백 기준
        keywords = [kw.strip() for kw in re.split(r"[,\s]+", query) if kw.strip()]
        if not keywords:
            return {
                "안내": "유효한 검색어를 입력해 주세요. 예: '내통장 결제', '신용카드', '계좌이체' 등"
            }

        repository = get_repository()
        results = repository.search_documents(keywords)


        if "안내" in results or "오류" in results:
            return results

        return {
            "검색어": keywords,
            "검색결과": results.get("검색결과", []),
            "안내": "BM25 알고리즘을 기반으로 관련성이 높은 문서 섹션을 정렬하여 제공합니다.",
        }

    except Exception as e:
        return {
            "오류": f"검색 중 문제가 발생했습니다: {e}",
            "안내": "다시 시도해 주세요. 문제가 지속되면 관리자에게 문의하세요.",
        }
