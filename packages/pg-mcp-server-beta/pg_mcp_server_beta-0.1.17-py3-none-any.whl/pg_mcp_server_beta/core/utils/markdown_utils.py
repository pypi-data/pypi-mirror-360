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
    숫자. 또는 숫자.숫자.숫자 ... 형태의 제목을 마크다운 heading(##, ###, ...)으로 변환.
    이미 #이 붙은 줄은 변환하지 않음.
    이스케이프된 점(6\.)도 인식.
    번호형 헤딩 아래에 언더라인(---, ===)이 있으면 자동으로 제거.
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


def _extract_text_from_ast(children):
    if not children:
        return ""
    texts = []
    for node in children:
        if isinstance(node, dict):
            t = node.get("type")
            if t == "emphasis":
                inner = _extract_text_from_ast(node.get("children", []))
                texts.append(f"_{inner}_")
                continue
            if t == "strong":
                inner = _extract_text_from_ast(node.get("children", []))
                texts.append(f"**{inner}**")
                continue
            if t == "codespan":
                inner = node.get("text", "")
                texts.append(f"`{inner}`")
                continue
            if t == "linebreak":
                texts.append("<br>")
                continue
            if t == "html_inline" or t == "html_block":
                # HTML 태그(예: <br>, <td colspan=...>)도 텍스트로 보존
                texts.append(node.get("text", ""))
                continue
            if "raw" in node:
                texts.append(node["raw"])
                continue
            if "text" in node:
                texts.append(node["text"])
            if "children" in node:
                texts.append(_extract_text_from_ast(node["children"]))
    return "".join(texts)


def _table_ast_to_markdown(node):
    if not isinstance(node, dict):
        return ""
    header = node.get("header", [])
    cells = node.get("cells", [])
    n_cols = len(header)
    # 헤더 추출
    header_line = "| " + " | ".join([
        _extract_text_from_ast(h.get("children", [])) for h in header if isinstance(h, dict)
    ]) + " |"
    sep_line = "|" + "---|" * n_cols
    # 셀 추출 (멀티라인, 셀 개수 불일치 보정)
    cell_lines = []
    for row in cells:
        row_cells = [
            _extract_text_from_ast(c.get("children", [])) if isinstance(c, dict) else ""
            for c in row
        ]
        # 셀 개수 맞추기
        if len(row_cells) < n_cols:
            row_cells += ["" for _ in range(n_cols - len(row_cells))]
        elif len(row_cells) > n_cols:
            row_cells = row_cells[:n_cols]
        cell_lines.append("| " + " | ".join(row_cells) + " |")
    return "\n".join([header_line, sep_line] + cell_lines)


def _list_ast_to_markdown(node):
    if not isinstance(node, dict):
        return ""
    items = node.get("children", [])
    ordered = node.get("ordered", False)
    lines = []
    for idx, item in enumerate(items, 1):
        prefix = f"{idx}. " if ordered else "- "
        if isinstance(item, dict):
            lines.append(prefix + _extract_text_from_ast(item.get("children", [])))
    return "\n".join(lines)
