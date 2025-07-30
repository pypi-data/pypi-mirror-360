import math
from typing import Any


class BM25Params:
    def __init__(self, k1: float = 1.2, b: float = 0.75, average_doc_length: float = 0.0, n: float = 0.0):
        self.k1 = k1
        self.b = b
        self.average_doc_length = float(average_doc_length)
        self.n = float(n)

class BM25Result:
    def __init__(self, id: int, score: float, total_tf: int):
        self.id = id
        self.score = score
        self.total_tf = total_tf


def bm25_score(term_frequencies: dict[int, dict[str, int]], doc_frequencies: dict[str, int],
               chunks: list[Any], params: BM25Params, keywords: list[str]) -> list[BM25Result]:
    """
    BM25 점수 계산 함수. (search_engine.py에서 분리)
    - term_frequencies: {chunk_id: {term: count}}
    - doc_frequencies: {term: doc_count}
    - chunks: DocumentChunk 리스트 (word_count 필드 필요)
    - params: BM25Params (k1, b, average_doc_length, N)
    - keywords: 검색어 리스트 (헤딩 가중치 적용용)
    """
    results = []
    for chunk in chunks:
        if chunk.id not in term_frequencies:
            continue
        tf = term_frequencies[chunk.id]
        length = chunk.word_count
        score = 0.0
        for term in tf:
            df = doc_frequencies.get(term, 0)
            idf = math.log((params.n - df + 0.5) / (df + 0.5) + 1) if df > 0 else 0
            numerator = tf[term] * (params.k1 + 1)
            denominator = tf[term] + params.k1 * (1 - params.b + params.b * (length / params.average_doc_length))
            score += idf * (numerator / denominator)
        # 헤딩(첫 줄)에 검색어 포함 시 1.5배 가중치
        heading_line = chunk.text.splitlines()[0] if chunk.text else ""
        if any(keyword in heading_line for keyword in keywords):
            score *= 1.5
        total_tf = sum(tf.values())
        results.append(BM25Result(id=chunk.id, score=score, total_tf=total_tf))
    return results
