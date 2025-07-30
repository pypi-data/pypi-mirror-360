from .get_docs import get_docs
from .list_docs import list_docs as _list_docs_mod
from .search_docs import search_docs as _search_docs_mod

list_docs = _list_docs_mod
search_docs = _search_docs_mod

__all__ = ["list_docs", "get_docs", "search_docs"]
