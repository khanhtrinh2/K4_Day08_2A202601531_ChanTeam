"""
Task 10 — Generation with Citation.

Mục tiêu:
    1. Reorder documents để tránh "lost in the middle"
    2. Format context có thông tin nguồn
    3. Sinh câu trả lời có citation

Lưu ý:
    - Nếu chưa có API key LLM, vẫn phải trả về dict có "answer"
    - Test chỉ cần function hoạt động đúng format
"""

from .task9_retrieval_pipeline import retrieve


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunk theo chiến lược:
    front + back[::-1]

    Ví dụ:
        [0,1,2,3,4] -> [0,2,4,3,1]
    """
    if not chunks:
        return []

    front = []
    back = []

    for idx, chunk in enumerate(chunks):
        if idx % 2 == 0:
            front.append(chunk)
        else:
            back.append(chunk)

    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """
    Chuyển danh sách retrieved chunks thành context string có source cho citation.
    """
    if not chunks:
        return "Không có ngữ cảnh truy xuất được."

    lines = []
    for i, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata", {}) or {}
        source = metadata.get("source", "unknown_source")
        doc_type = metadata.get("type", "unknown_type")
        content = chunk.get("content", "").strip()

        lines.append(f"[Tài liệu {i}]")
        lines.append(f"Nguồn: {source}")
        lines.append(f"Loại: {doc_type}")
        lines.append(content)
        lines.append("")

    return "\n".join(lines).strip()


def generate_with_citation(query: str, top_k: int = 5) -> dict:
    """
    Sinh câu trả lời có citation.

    Returns:
        {
            "answer": str,
            "context": str,
            "retrieved_chunks": list[dict]
        }
    """
    retrieved_chunks = retrieve(query, top_k=top_k)
    reordered_chunks = reorder_for_llm(retrieved_chunks)
    context = format_context(reordered_chunks)

    if not reordered_chunks:
        answer = "Tôi chưa tìm thấy thông tin phù hợp để trả lời câu hỏi này."
        return {
            "answer": answer,
            "context": context,
            "retrieved_chunks": reordered_chunks,
        }

    source_names = []
    for chunk in reordered_chunks[:2]:
        metadata = chunk.get("metadata", {}) or {}
        source = metadata.get("source")
        if source and source not in source_names:
            source_names.append(source)

    citation_text = " ".join(f"[{name}]" for name in source_names) if source_names else "[unknown_source]"

    top_content = reordered_chunks[0].get("content", "").strip()
    short_summary = top_content[:300]
    if len(top_content) > 300:
        short_summary += "..."

    answer = (
        f"Dựa trên tài liệu truy xuất được, nội dung liên quan nhất cho câu hỏi "
        f"'{query}' là: {short_summary} {citation_text}"
    )

    return {
        "answer": answer,
        "context": context,
        "retrieved_chunks": reordered_chunks,
    }


if __name__ == "__main__":
    query = "Shopee hỗ trợ những phương thức thanh toán nào?"
    result = generate_with_citation(query, top_k=3)

    print("=" * 80)
    print("ANSWER:")
    print(result["answer"])
    print("\n" + "=" * 80)
    print("CONTEXT:")
    print(result["context"][:1000])