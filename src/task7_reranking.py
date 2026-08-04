"""
Task 7 — Reranking Module.

Chọn 1 trong các phương pháp:
    - Cross-encoder reranker: Jina Reranker v2 (multilingual) hoặc Qwen3-Reranker
    - MMR (Maximal Marginal Relevance): tự implement
    - RRF (Reciprocal Rank Fusion): tự implement — khuyến nghị vì không cần API key

Nếu dùng MMR hoặc RRF, đảm bảo hiểu và giải thích được cơ chế.

Lưu ý quan trọng về RRF (sẽ dùng lại ở Task 9): điểm RRF fused CHỈ phụ thuộc thứ hạng,
không phải độ tương đồng thật. Top-1 sau khi fuse luôn xấp xỉ 1/(k+1) ≈ 0.0164 (k=60),
bất kể nội dung đó có thật sự liên quan đến câu hỏi hay không. Đừng dùng điểm RRF để
quyết định fallback ở Task 9 — xem ghi chú ở đó.
"""


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Placeholder an toàn: nếu chưa dùng API/model reranker thật,
    tạm thời giữ nguyên thứ tự candidates theo score hiện có.
    """
    sorted_candidates = sorted(
        candidates, key=lambda item: item.get("score", 0.0), reverse=True
    )
    return sorted_candidates[:top_k]


def _cosine_sim(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance — chọn candidates vừa relevant vừa diverse.
    """
    if not candidates:
        return []

    selected_indices = []
    remaining_indices = list(range(len(candidates)))

    for _ in range(min(top_k, len(candidates))):
        best_idx = None
        best_score = float("-inf")

        for idx in remaining_indices:
            candidate = candidates[idx]
            candidate_embedding = candidate.get("embedding", [])
            relevance = _cosine_sim(query_embedding, candidate_embedding)

            max_sim_to_selected = 0.0
            for selected_idx in selected_indices:
                selected_embedding = candidates[selected_idx].get("embedding", [])
                sim = _cosine_sim(candidate_embedding, selected_embedding)
                max_sim_to_selected = max(max_sim_to_selected, sim)

            mmr_score = (
                lambda_param * relevance
                - (1 - lambda_param) * max_sim_to_selected
            )

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        if best_idx is None:
            break

        selected_indices.append(best_idx)
        remaining_indices.remove(best_idx)

    results = []
    for idx in selected_indices:
        item = candidates[idx].copy()
        item["score"] = float(item.get("score", 0.0))
        results.append(item)

    return results


def _make_doc_key(item: dict) -> str:
    metadata = item.get("metadata", {}) or {}
    source = metadata.get("source", "unknown")
    chunk_index = metadata.get("chunk_index", -1)
    content = item.get("content", "")
    return f"{source}::{chunk_index}::{content[:80]}"


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker.

    RRF(d) = Σ 1 / (k + rank_r(d))
    """
    rrf_scores = {}
    item_map = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            key = _make_doc_key(item)
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k + rank)

            if key not in item_map:
                item_map[key] = item.copy()

    sorted_items = sorted(rrf_scores.items(), key=lambda pair: pair[1], reverse=True)

    results = []
    for key, fused_score in sorted_items[:top_k]:
        item = item_map[key].copy()
        item["score"] = round(float(fused_score), 6)
        results.append(item)

    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "rrf",
) -> list[dict]:
    """
    Unified reranking interface.
    """
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
        return sorted(
            candidates, key=lambda item: item.get("score", 0.0), reverse=True
        )[:top_k]
    elif method == "rrf":
        return rerank_rrf([candidates], top_k=top_k)
    else:
        raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    dense_results = [
        {
            "content": "Chính sách trả hàng và hoàn tiền Shopee trong 15 ngày",
            "score": 0.82,
            "metadata": {"source": "returns.md", "chunk_index": 0},
        },
        {
            "content": "Các phương thức thanh toán hỗ trợ trên Shopee Vietnam",
            "score": 0.76,
            "metadata": {"source": "payments.md", "chunk_index": 1},
        },
    ]

    bm25_results = [
        {
            "content": "Các phương thức thanh toán hỗ trợ trên Shopee Vietnam",
            "score": 9.1,
            "metadata": {"source": "payments.md", "chunk_index": 1},
        },
        {
            "content": "Quy định đăng bán sản phẩm dành cho người bán",
            "score": 7.4,
            "metadata": {"source": "listing.md", "chunk_index": 0},
        },
    ]

    results = rerank_rrf([dense_results, bm25_results], top_k=3)
    for r in results:
        print(f"[{r['score']:.6f}] {r['metadata'].get('source')} - {r['content']}")