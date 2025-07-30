def extract_category(filename: str) -> str:
    # 경로 구분자 통일
    norm = filename.replace("\\", "/")
    if norm.endswith('.js'):
        # 상위 폴더명 추출
        parts = norm.split('/')
        if len(parts) > 1:
            parent = parts[-2]
            if parent == 'pg':
                return 'PG-연동스크립트'
            elif parent == 'ezauth':
                return '내통장결제-연동스크립트'
            else:
                return f'{parent}-연동스크립트'
        return '연동스크립트'
    if "pg" in norm:
        return "PG"
    elif "ezauth" in norm:
        return "내통장결제"
    elif "ezcp" in norm:
        return "간편현금결제"
    elif "instructions.md" in norm:
        return "instructions"
    return "기타"
