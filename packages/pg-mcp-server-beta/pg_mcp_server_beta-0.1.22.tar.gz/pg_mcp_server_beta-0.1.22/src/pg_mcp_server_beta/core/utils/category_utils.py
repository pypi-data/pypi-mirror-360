import json
from pathlib import Path

CATEGORY_MAP_PATH = Path(__file__).parent / "category_map.json"

# 최초 1회만 로딩 (성능 최적화)
def load_category_map():
    with open(CATEGORY_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)

CATEGORY_MAP = load_category_map()

def extract_category(path: str) -> str:
    path_lower = path.lower()
    for key, value in CATEGORY_MAP.items():
        if key != "etc" and key in path_lower:
            return value
    return CATEGORY_MAP.get("etc", "기타")
