import os

from .document_repository import (
    HectoDocumentRepository,
    get_repository,
    initialize_repository,
)

__all__ = ["HectoDocumentRepository", "get_repository", "initialize_repository", "documents", "load_docs"]

def load_docs(base_dir):
    docs = {}
    for dirpath, _, filenames in os.walk(base_dir):
        for filename in filenames:
            if filename.startswith('.'):
                continue
            # .md, .js 파일만 로딩
            if not (filename.endswith('.md') or filename.endswith('.js')):
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, base_dir)
            with open(abs_path, encoding="utf-8") as f:
                docs[rel_path] = f.read()
    return docs

documents = load_docs(os.path.join(os.path.dirname(__file__), "..", "resource", "docs"))
