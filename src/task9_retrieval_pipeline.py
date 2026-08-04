"""
Task 9 — Retrieval Pipeline.

Nối chuỗi retrieval hoàn chỉnh:
    1. Semantic search
    2. Lexical search (BM25)
    3. RRF rerank
    4. Fallback sang PageIndex nếu dense score quá thấp

Lưu ý cực kỳ quan trọng:
    - So sánh fallback bằng dense_results[0]["score"]
    - KHÔNG dùng score sau RRF để quyết định fallback
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


def retrieve(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.48,
) -> list[dict]:
    """
    Hybrid retrieval pipeline + PageIndex fallback.

    Args:
        query: Câu truy vấn
        top_k: Số kết quả tối đa
        score_threshold: Ngưỡng fallback dựa trên dense score gốc

    Returns:
        List of {
            "content": str,
            "score": float,
            "metadata": dict,
            "source": "hybrid" | "pageindex"
        }
    """
    dense_results = semantic_search(query, top_k=top_k)
    lexical_results = lexical_search(query, top_k=top_k)

    # Fallback nếu dense search không có kết quả đủ tốt
    if not dense_results:
        fallback_results = pageindex_search(query, top_k=top_k)
        return fallback_results[:top_k]

    best_dense_score = dense_results[0].get("score", 0.0)
    if best_dense_score < score_threshold:
        fallback_results = pageindex_search(query, top_k=top_k)
        return fallback_results[:top_k]

    # Hybrid fusion bằng RRF
    fused_results = rerank_rrf([dense_results, lexical_results], top_k=top_k)

    output = []
    for item in fused_results:
        result = item.copy()
        result["source"] = "hybrid"
        output.append(result)

    return output[:top_k]


if __name__ == "__main__":
    test_queries = [
        "chính sách trả hàng hoàn tiền",
        "phương thức thanh toán",
        "quy định đăng bán sản phẩm",
        "xyzabc123 no relevant document",
    ]

    for query in test_queries:
        print("=" * 80)
        print(f"Query: {query}")
        results = retrieve(query, top_k=3)
        for r in results:
            print(f"[{r['source']}] [{r['score']:.4f}] {r['content'][:100]}...")