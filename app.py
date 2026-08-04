"""
RAG Chatbot — E-commerce Support (Starter Template)
Streamlit app kết nối RAG Retrieval (Task 9) và Generation (Task 10).

Chạy:
    streamlit run app.py
"""

import html
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Thêm project root vào sys.path để import các task từ src/
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="E-commerce Support RAG Chatbot",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# STYLE — Tông cam Shopee, bong bóng chat, thẻ nguồn tham khảo
# =============================================================================

st.markdown(
    """
    <style>
    :root {
        --shopee: #EE4D2D;
        --shopee-dark: #D7411F;
        --shopee-soft: #FFF3EC;
    }

    /* ---------- Header (topbar + navbar, phong cách Shopee) ---------- */
    .shopee-header {
        background: linear-gradient(135deg, #FF7A45, var(--shopee));
        border-radius: 0 0 18px 18px;
        margin: 0 0 1.2rem 0;
        box-shadow: 0 4px 16px rgba(238,77,45,0.25);
    }
    .topbar {
        background: rgba(0,0,0,0.14);
        color: #fff;
        font-size: 0.72rem;
        padding: 0.35rem 1.6rem;
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.3rem;
        border-radius: 0 0 18px 18px;
    }
    .navbar {
        padding: 0.9rem 1.6rem 0.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.6rem;
    }
    .brand {
        font-size: 1.35rem;
        font-weight: 800;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        letter-spacing: 0.01em;
    }
    .navlinks { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .navchip {
        background: rgba(255,255,255,0.18);
        color: #fff;
        font-size: 0.75rem;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-weight: 600;
        white-space: nowrap;
    }
    .tagline {
        margin: 0;
        padding: 0 1.6rem 0.9rem;
        color: #fff;
        opacity: 0.92;
        font-size: 0.85rem;
    }

    /* ---------- Layout: header dính trên, footer dính dưới, nội dung giữa (kiểu Claude Web) ---------- */
    div[data-testid="stMain"] .block-container {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        max-width: 900px;
        margin: 0 auto;
        padding-top: 0.5rem;
    }

    /* ---------- Footer (phong cách Shopee) — luôn nằm ở cuối trang ---------- */
    .shopee-footer {
        margin-top: auto;
        padding-top: 2.2rem;
    }
    .shopee-footer .footer-inner {
        border-top: 1px solid rgba(238,77,45,0.18);
        padding-top: 1.4rem;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1.2rem;
    }
    .footer-grid h4 {
        font-size: 0.76rem;
        color: var(--shopee-dark);
        margin: 0 0 0.5rem 0;
        letter-spacing: 0.03em;
    }
    .footer-grid p { font-size: 0.78rem; opacity: 0.65; margin: 0.25rem 0; }
    .footer-bottom {
        text-align: center;
        font-size: 0.72rem;
        opacity: 0.5;
        margin-top: 1.4rem;
        padding-top: 1rem;
        border-top: 1px dashed rgba(0,0,0,0.08);
    }

    /* ---------- Empty state ---------- */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        opacity: 0.7;
    }
    .empty-state .big { font-size: 2.4rem; margin-bottom: 0.5rem; }
    .empty-state .hint { font-size: 0.85rem; opacity: 0.75; margin-top: 0.3rem; }

    /* ---------- Chat bubbles (tô màu theo container key msg-user-*/msg-bot-*) --- */
    [class*="st-key-msg-user-"] [data-testid="stChatMessage"] {
        background: linear-gradient(135deg, #FF7A45, var(--shopee));
        border-radius: 18px 18px 4px 18px;
        border: none;
        box-shadow: 0 2px 8px rgba(238,77,45,0.2);
    }
    [class*="st-key-msg-user-"] [data-testid="stChatMessage"] p,
    [class*="st-key-msg-user-"] [data-testid="stChatMessage"] li,
    [class*="st-key-msg-user-"] [data-testid="stChatMessage"] span {
        color: #FFFFFF !important;
    }
    [class*="st-key-msg-user-"] [data-testid="stChatMessageAvatarCustom"] {
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
    }

    [class*="st-key-msg-bot-"] [data-testid="stChatMessage"] {
        background: #FFFFFF;
        border: 1px solid rgba(238,77,45,0.15);
        border-radius: 18px 18px 18px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    [class*="st-key-msg-bot-"] [data-testid="stChatMessageAvatarCustom"] {
        background: var(--shopee-soft);
        border-radius: 50%;
    }

    /* ---------- Source cards ---------- */
    .source-card {
        border: 1px solid rgba(238,77,45,0.18);
        border-left: 4px solid var(--shopee);
        border-radius: 10px;
        padding: 0.65rem 0.9rem;
        margin-bottom: 0.55rem;
        background: var(--shopee-soft);
    }
    .src-head {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.3rem;
        flex-wrap: wrap;
    }
    .src-rank {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px; height: 22px;
        border-radius: 50%;
        background: var(--shopee);
        color: white;
        font-size: 0.72rem;
        font-weight: 700;
        flex-shrink: 0;
    }
    .src-name { font-weight: 600; font-size: 0.88rem; }
    .src-badge {
        font-size: 0.66rem;
        padding: 0.1rem 0.5rem;
        border-radius: 999px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .badge-legal { background: rgba(34,139,87,0.18); color: #1f8a52; }
    .badge-news { background: rgba(37,99,235,0.18); color: #2563eb; }
    .badge-pageindex { background: rgba(147,51,234,0.18); color: #9333ea; }
    .badge-unknown { background: rgba(120,120,120,0.2); color: #6b7280; }
    .src-score { font-size: 0.7rem; opacity: 0.6; margin-left: auto; font-family: monospace; }
    .src-content { font-size: 0.8rem; opacity: 0.85; line-height: 1.4; white-space: pre-wrap; }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] { border-right: 1px solid rgba(238,77,45,0.12); }
    .sidebar-title { font-size: 1.15rem; font-weight: 700; color: var(--shopee-dark); margin-bottom: 0.1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

DOC_TYPE_BADGES = {
    "legal": ("badge-legal", "Pháp lý"),
    "news": ("badge-news", "Tin tức"),
    "pageindex": ("badge-pageindex", "PageIndex"),
}

SUGGESTIONS = [
    "Thời hạn yêu cầu trả hàng/hoàn tiền là bao lâu?",
    "Shopee hỗ trợ những phương thức thanh toán nào?",
    "Làm sao để đổi phương thức thanh toán đơn hàng?",
    "Quy định về đăng bán sản phẩm cho người bán?",
    "Cách mua hàng trên Shopee của quốc gia khác?",
]


def render_sources(sources: list[dict]) -> None:
    """Hiển thị danh sách tài liệu tham khảo dạng card có badge loại tài liệu + score."""
    if not sources:
        return

    with st.expander(f"📚 Nguồn tham khảo ({len(sources)} đoạn trích)"):
        for i, src in enumerate(sources, 1):
            meta = src.get("metadata", {}) or {}
            source_name = html.escape(str(meta.get("source", "Unknown")))
            doc_type = str(meta.get("type", "unknown"))
            badge_class, badge_label = DOC_TYPE_BADGES.get(doc_type, ("badge-unknown", doc_type or "unknown"))
            pipeline_source = html.escape(str(src.get("source", "-")))
            score = src.get("score", 0) or 0

            raw_content = src.get("content", "")
            content = html.escape(raw_content[:280].strip())
            if len(raw_content) > 280:
                content += "…"

            st.markdown(
                f"""<div class="source-card">
                    <div class="src-head">
                        <span class="src-rank">{i}</span>
                        <span class="src-name">{source_name}</span>
                        <span class="src-badge {badge_class}">{html.escape(str(badge_label))}</span>
                        <span class="src-score">{pipeline_source} · score {score:.4f}</span>
                    </div>
                    <div class="src-content">{content}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def render_message(role: str, key: str, content: str, sources: list[dict] | None = None) -> None:
    """Render 1 lượt chat trong bong bóng màu theo role (user = cam, assistant = trắng)."""
    avatar = "🧑" if role == "user" else "🤖"
    with st.container(key=key):
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            if role == "assistant":
                render_sources(sources or [])

# =============================================================================
# SIDEBAR — INFO & SETTINGS
# =============================================================================

with st.sidebar:
    st.markdown('<div class="sidebar-title">🛒 RAG Chatbot</div>', unsafe_allow_html=True)
    st.caption("Trợ lý hỏi đáp chính sách đổi trả, thanh toán, bảo mật và quy định người bán.")

    st.divider()

    st.markdown("**💡 Câu hỏi gợi ý**")
    for s in SUGGESTIONS:
        if st.button(s, use_container_width=True, key=f"sug_{s[:20]}", type="secondary"):
            st.session_state["pending_query"] = s

    st.divider()
    st.markdown("**⚙️ Thiết lập**")
    top_k = st.slider("Số đoạn trích truy xuất (top_k)", 3, 10, 5)

    st.divider()
    if st.button("🧹 Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()

    st.divider()
    st.caption("**Kiến trúc hệ thống:**")
    st.caption("Hybrid Retrieval (Semantic + BM25) → RRF Rerank → PageIndex Fallback → LLM Generation có Citation")

# =============================================================================
# SESSION STATE
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# =============================================================================
# MAIN CHAT AREA
# =============================================================================

if not st.session_state.messages:
    st.markdown(
        """<div class="empty-state">
            <div class="big">👋🛍️</div>
            <div>Đặt câu hỏi về chính sách đổi trả, thanh toán, bảo mật hoặc quy định người bán.</div>
            <div class="hint">Hoặc chọn một câu hỏi gợi ý ở thanh bên trái để bắt đầu.</div>
        </div>""",
        unsafe_allow_html=True,
    )

for i, msg in enumerate(st.session_state.messages):
    render_message(
        role=msg["role"],
        key=f"msg-{msg['role']}-hist-{i}",
        content=msg["content"],
        sources=msg.get("sources", []),
    )

# =============================================================================
# QUERY HANDLING
# =============================================================================

user_input = st.chat_input("Nhập câu hỏi của bạn về chính sách/hỗ trợ e-commerce...")
query = user_input or st.session_state.pending_query

if query:
    st.session_state.pending_query = None

    # Hiển thị câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": query})
    render_message(role="user", key="msg-user-live", content=query)

    # Sinh câu trả lời từ RAG Pipeline
    avatar = "🤖"
    with st.container(key="msg-bot-live"):
        with st.chat_message("assistant", avatar=avatar):
            with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời..."):
                try:
                    from src.task10_generation import generate_with_citation

                    response = generate_with_citation(query, top_k=top_k)
                    answer = response.get("answer", "Chưa thể trả lời.")
                    sources = response.get("sources", [])

                except NotImplementedError:
                    answer = "⚠️ **Task 10 chưa được implement.** Hãy hoàn thành `src/task10_generation.py` để kết nối pipeline vào UI!"
                    sources = []
                except Exception as e:
                    answer = f"❌ **Lỗi khi chạy RAG Pipeline:** {e}"
                    sources = []

                st.markdown(answer)
                render_sources(sources)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
