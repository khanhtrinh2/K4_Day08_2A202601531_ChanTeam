"""
Task 10 — Generation with Citation.

Mục tiêu:
    1. Reorder documents để tránh "lost in the middle"
    2. Format context có thông tin nguồn
    3. Sinh câu trả lời có citation (gọi LLM qua OpenRouter, fallback OpenAI)

Lưu ý:
    - Nếu chưa có API key LLM, vẫn phải trả về dict có "answer"
    - Test chỉ cần function hoạt động đúng format
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model free tier OpenRouter dùng cho bài lab (giới hạn ~50 req/ngày).
OPENROUTER_MODEL = "inclusionai/ling-3.0-flash:free"
OPENAI_MODEL = "gpt-4o-mini"

# Temperature thấp + top_p cao: ưu tiên độ chính xác factual (giảm bịa đặt),
# vẫn giữ đủ tự nhiên khi diễn giải lại nội dung nguồn.
TEMPERATURE = 0.3
TOP_P = 0.9

SYSTEM_PROMPT = """Bạn là trợ lý hỗ trợ khách hàng thương mại điện tử.
Chỉ trả lời dựa vào các tài liệu trong phần NGỮ CẢNH được cung cấp, không suy đoán
hay bịa thêm thông tin ngoài ngữ cảnh.
Với MỌI khẳng định trong câu trả lời, phải chèn ngay trích dẫn nguồn theo định dạng
[Tên nguồn] lấy đúng từ nhãn "Nguồn:" tương ứng trong ngữ cảnh.
Nếu ngữ cảnh không đủ thông tin để trả lời, hãy trả lời:
"Tôi chưa đủ thông tin để xác nhận điều này." thay vì đoán.
Trả lời ngắn gọn, rõ ràng, bằng tiếng Việt."""


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


def _call_llm(query: str, context: str) -> str | None:
    """
    Gọi LLM để sinh câu trả lời có citation.

    Thử OpenRouter trước (model free tier), nếu thiếu key/lỗi (vd 429 hết quota)
    thì thử OpenAI. Trả về None nếu không có key nào hoặc cả hai đều thất bại —
    caller sẽ dùng câu trả lời mock làm fallback an toàn.
    """
    providers = []
    if OPENROUTER_API_KEY:
        providers.append((OPENROUTER_API_KEY, "https://openrouter.ai/api/v1", OPENROUTER_MODEL))
    if OPENAI_API_KEY:
        providers.append((OPENAI_API_KEY, None, OPENAI_MODEL))

    if not providers:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    user_prompt = f"NGỮ CẢNH:\n{context}\n\nCÂU HỎI: {query}"

    for api_key, base_url, model in providers:
        try:
            client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
        except Exception:
            continue  # thử provider fallback tiếp theo

    return None


def generate_with_citation(query: str, top_k: int = 5) -> dict:
    """
    Sinh câu trả lời có citation.

    Returns:
        {
            "answer": str,
            "context": str,
            "retrieved_chunks": list[dict],
            "sources": list[dict]  # alias của retrieved_chunks, dùng cho app.py
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
            "sources": reordered_chunks,
        }

    llm_answer = _call_llm(query, context)
    if llm_answer:
        return {
            "answer": llm_answer,
            "context": context,
            "retrieved_chunks": reordered_chunks,
            "sources": reordered_chunks,
        }

    # Fallback mock: dùng khi chưa có API key hoặc LLM call thất bại (vd hết rate limit free tier)
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
        "sources": reordered_chunks,
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