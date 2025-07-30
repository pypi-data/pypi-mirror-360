# 패키지 진입점에서 별도 import 없음

import importlib.metadata

try:
    __version__ = importlib.metadata.version("pg-mcp-server-beta")
except importlib.metadata.PackageNotFoundError:
    __version__ = "dev"

__all__ = []
