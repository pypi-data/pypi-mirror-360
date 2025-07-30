import re

import mistune


def parse_markdown_to_ast(markdown_text: str):
    """
    마크다운 텍스트를 mistune의 AST(구문 트리)로 파싱합니다.
    """
    markdown = mistune.create_markdown(renderer="ast")
    return markdown(markdown_text)


def convert_numbered_headings(markdown_text: str) -> str:
    r"""
    숫자. 또는 숫자.숫자.숫자 ... 형태의 제목을 마크다운 heading(##, ###, ...)으로 변환합니다.
    이미 #이 붙은 줄은 변환하지 않습니다.
    이스케이프된 점(6\.)도 인식합니다.
    번호형 헤딩 아래에 언더라인(---, ===)이 있으면 자동으로 제거합니다.
    """
    lines = markdown_text.splitlines()
    new_lines = []
    i = 0
    pattern = re.compile(r"^(?!#)((?:\d+(?:\.|\\\.)*)+)\s+(.+)")
    while i < len(lines):
        line = lines[i]
        m = pattern.match(line)
        if m:
            numbers = m.group(1).replace('\\.', '.')
            title = m.group(2)
            # 점 개수와 패턴(6. vs 6.1 등)로 heading level 결정
            num_parts = [p for p in numbers.strip('.').split('.') if p]
            if len(num_parts) == 1:
                level = 2  # 6. → ##
            else:
                level = min(len(num_parts) + 1, 6)  # 6.1 → ###, 6.1.1 → ####
            new_lines.append(f"{'#' * level} {numbers.strip()} {title.strip()}")
            # 바로 아래줄이 언더라인(---, === 등)이면 스킵
            if i + 1 < len(lines) and re.match(r"^\s*[-=]{3,}\s*$", lines[i+1]):
                i += 2
                continue
        else:
            new_lines.append(line)
        i += 1
    return "\n".join(new_lines)
