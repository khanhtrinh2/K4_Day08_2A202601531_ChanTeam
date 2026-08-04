"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

from .task4_chunking_indexing import (
    chunk_documents,
    get_collection,
    get_embedding_model,
    load_documents,
)


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity (Cosine).

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score [0, 1]
            'metadata': dict     # source, type, chunk_index, customer_role
        }
        Sorted by score descending.
    """
    # Bước 1: Embed query bằng cùng model ở Task 4
    model = get_embedding_model()
    query_vector = model.encode(query)
    if hasattr(query_vector, "tolist"):
        query_vector = query_vector.tolist()

    # Ưu tiên ChromaDB nếu đã index sẵn, fallback sang so khớp trực tiếp trên chunks.
    try:
        collection = get_collection()
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0]
            ):
                score = max(0.0, 1.0 - dist)
                output.append({"content": doc, "score": round(score, 4), "metadata": meta})

        output.sort(key=lambda x: x["score"], reverse=True)
        if output:
            return output[:top_k]
    except Exception:
        pass

    docs = load_documents()
    chunks = chunk_documents(docs)
    output = []
    for chunk in chunks:
        chunk_vector = model.encode(chunk["content"])
        if hasattr(chunk_vector, "tolist"):
            chunk_vector = chunk_vector.tolist()
        score = _cosine_similarity(query_vector, chunk_vector)
        output.append(
            {
                "content": chunk["content"],
                "score": round(max(0.0, score), 4),
                "metadata": chunk["metadata"],
            }
        )

    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:top_k]


if __name__ == "__main__":
    # Test
    results = semantic_search("quy định trả hàng hoàn tiền shopee", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
