"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

Cài đặt:
    pip install rank-bm25

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)
"""

import numpy as np
from .task4_chunking_indexing import load_documents, chunk_documents

try:
    from rank_bm25 import BM25Okapi
except Exception:
    BM25Okapi = None

# =============================================================================
# BM25 Index — Lazy initialization
# =============================================================================

_bm25_index = None
_corpus: list[dict] = []


def _ensure_bm25_index():
    """Load corpus và build BM25 index nếu chưa có."""
    global _bm25_index, _corpus

    if _bm25_index is not None:
        return

    # Load và chunk documents (giống Task 4 nhưng không cần embed)
    docs = load_documents()
    _corpus = chunk_documents(docs)

    # Tokenize corpus cho BM25
    tokenized_corpus = [doc["content"].lower().split() for doc in _corpus]
    _bm25_index = BM25Okapi(tokenized_corpus) if BM25Okapi is not None else tokenized_corpus


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    global _bm25_index, _corpus
    _corpus = corpus
    tokenized_corpus = [doc["content"].lower().split() for doc in corpus]
    _bm25_index = BM25Okapi(tokenized_corpus) if BM25Okapi is not None else tokenized_corpus
    return _bm25_index


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score
            'metadata': dict
        }
        Sorted by score descending.
    """
    _ensure_bm25_index()

    tokenized_query = query.lower().split()
    if BM25Okapi is not None:
        scores = _bm25_index.get_scores(tokenized_query)
    else:
        query_terms = set(tokenized_query)
        scores = np.array(
            [
                float(sum(1 for token in doc["content"].lower().split() if token in query_terms))
                for doc in _corpus
            ]
        )

    # Get top_k indices sorted by score descending
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "content": _corpus[idx]["content"],
            "score": float(scores[idx]),
            "metadata": _corpus[idx]["metadata"],
        })
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    # Test
    results = lexical_search("phương thức thanh toán shopee", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
