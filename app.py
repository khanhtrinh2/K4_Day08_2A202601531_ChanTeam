"""
Phopee-style Streamlit RAG chatbot.

Run:
    streamlit run app.py
"""

import html
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="Phopee Support RAG",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --phopee-orange: #ee4d2d;
        --phopee-orange-dark: #d73211;
        --phopee-orange-soft: #fff1ea;
        --phopee-yellow: #ffd166;
        --phopee-teal: #0f9f8f;
        --ink: #2b2f33;
        --muted: #68707a;
        --line: #f0d7cd;
        --surface: #ffffff;
        --page: #fff8f4;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background:
            linear-gradient(180deg, #fff7f1 0%, #ffffff 34%, #fffaf7 100%);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: #ffffff;
        border-bottom: 1px solid rgba(238, 77, 45, 0.14);
    }

    [data-testid="stHeader"] * {
        color: var(--ink) !important;
    }

    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"] {
        background: linear-gradient(180deg, rgba(255,248,244,0) 0%, #fff8f4 40%);
    }

    [data-testid="stChatInput"] {
        background: #ffffff;
        border: 1px solid rgba(238, 77, 45, 0.28);
        border-radius: 999px;
        box-shadow: 0 8px 20px rgba(125, 55, 31, 0.08);
    }

    [data-testid="stChatInput"] textarea {
        color: var(--ink);
    }

    [data-testid="stChatInputSubmitButton"] {
        background: var(--phopee-orange);
        border-radius: 999px;
    }

    [data-testid="stChatInputSubmitButton"] svg {
        fill: #ffffff;
    }

    footer {
        background: #fff8f4;
    }

    .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-bottom: 5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid rgba(238, 77, 45, 0.16);
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 44px;
        border-radius: 8px;
        border: 1px solid rgba(238, 77, 45, 0.2);
        background: #fff9f6;
        color: #6b2b1f;
        font-weight: 600;
        text-align: left;
        white-space: normal;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--phopee-orange);
        color: var(--phopee-orange-dark);
        background: var(--phopee-orange-soft);
    }

    .phopee-shell {
        border: 1px solid rgba(238, 77, 45, 0.14);
        border-radius: 8px;
        overflow: hidden;
        background: var(--surface);
        box-shadow: 0 16px 40px rgba(125, 55, 31, 0.08);
    }

    .phopee-topbar {
        min-height: 34px;
        padding: 0.45rem 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        color: #ffffff;
        background: var(--phopee-orange-dark);
        font-size: 0.78rem;
        font-weight: 600;
        flex-wrap: wrap;
    }

    .phopee-header {
        min-height: 116px;
        padding: 1rem 1.25rem;
        display: grid;
        grid-template-columns: minmax(180px, 1fr) minmax(220px, 1.4fr);
        align-items: center;
        gap: 1rem;
        background: linear-gradient(135deg, #ff7a45 0%, var(--phopee-orange) 66%, #f9421e 100%);
        color: #ffffff;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .brand-mark {
        width: 44px;
        height: 44px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        color: var(--phopee-orange);
        font-size: 1.5rem;
        font-weight: 900;
        box-shadow: 0 8px 20px rgba(100, 31, 11, 0.18);
        flex: 0 0 44px;
    }

    .brand-title {
        font-size: 1.55rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: 0;
        margin: 0;
    }

    .brand-subtitle {
        font-size: 0.86rem;
        line-height: 1.35;
        opacity: 0.93;
        margin-top: 0.22rem;
    }

    .search-panel {
        min-height: 56px;
        padding: 0.55rem 0.75rem;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.96);
        color: var(--muted);
        display: flex;
        align-items: center;
        gap: 0.6rem;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.5);
    }

    .search-icon {
        width: 32px;
        height: 32px;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: var(--phopee-orange-soft);
        color: var(--phopee-orange);
        flex: 0 0 32px;
    }

    .search-copy {
        font-size: 0.88rem;
        line-height: 1.35;
        color: #5b6470;
    }

    .status-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0;
        border-bottom: 1px solid rgba(238, 77, 45, 0.12);
        background: #fffdfb;
    }

    .status-item {
        min-height: 62px;
        padding: 0.75rem 0.9rem;
        border-right: 1px solid rgba(238, 77, 45, 0.1);
    }

    .status-item:last-child {
        border-right: 0;
    }

    .status-label {
        font-size: 0.7rem;
        color: var(--muted);
        text-transform: uppercase;
        font-weight: 750;
        letter-spacing: 0.04em;
    }

    .status-value {
        margin-top: 0.16rem;
        font-size: 0.88rem;
        color: var(--ink);
        font-weight: 760;
    }

    .chat-stage {
        padding: 1rem;
        background:
            linear-gradient(90deg, rgba(238,77,45,0.035) 1px, transparent 1px),
            linear-gradient(180deg, #fffdfb, #ffffff);
        background-size: 28px 28px, auto;
    }

    .empty-state {
        min-height: 260px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2rem 1rem;
        color: var(--muted);
    }

    .empty-icon {
        width: 62px;
        height: 62px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        background: var(--phopee-orange-soft);
        color: var(--phopee-orange);
        font-size: 1.8rem;
        margin-bottom: 0.8rem;
    }

    .empty-title {
        font-size: 1.05rem;
        font-weight: 760;
        color: var(--ink);
    }

    .empty-copy {
        max-width: 560px;
        margin-top: 0.35rem;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .chat-row {
        display: flex;
        gap: 0.65rem;
        margin: 0.72rem 0;
        align-items: flex-start;
    }

    .chat-row.user {
        flex-direction: row-reverse;
    }

    .avatar {
        width: 34px;
        height: 34px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        flex: 0 0 34px;
    }

    .avatar.user {
        color: #ffffff;
        background: var(--phopee-orange);
    }

    .avatar.assistant {
        color: var(--phopee-orange);
        background: var(--phopee-orange-soft);
        border: 1px solid rgba(238, 77, 45, 0.18);
    }

    .bubble {
        width: fit-content;
        max-width: min(760px, calc(100% - 54px));
        border-radius: 8px;
        padding: 0.78rem 0.92rem;
        line-height: 1.52;
        font-size: 0.95rem;
        overflow-wrap: anywhere;
    }

    .bubble.user {
        color: #ffffff;
        background: var(--phopee-orange);
        box-shadow: 0 8px 18px rgba(238, 77, 45, 0.18);
    }

    .bubble.assistant {
        color: var(--ink);
        background: #ffffff;
        border: 1px solid rgba(238, 77, 45, 0.18);
        box-shadow: 0 8px 22px rgba(43, 47, 51, 0.05);
    }

    .source-wrap {
        margin-left: 45px;
        max-width: 760px;
    }

    .source-card {
        margin: 0.5rem 0;
        padding: 0.72rem 0.82rem;
        border-radius: 8px;
        border: 1px solid rgba(238, 77, 45, 0.18);
        border-left: 4px solid var(--phopee-orange);
        background: #fffaf7;
    }

    .source-head {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        flex-wrap: wrap;
        margin-bottom: 0.35rem;
    }

    .source-rank {
        width: 22px;
        height: 22px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        background: var(--phopee-orange);
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 780;
    }

    .source-name {
        font-size: 0.86rem;
        font-weight: 760;
        color: var(--ink);
    }

    .badge {
        padding: 0.14rem 0.44rem;
        border-radius: 999px;
        font-size: 0.68rem;
        font-weight: 760;
        text-transform: uppercase;
    }

    .badge-legal { color: #13765e; background: rgba(15, 159, 143, 0.14); }
    .badge-news { color: #3157b8; background: rgba(49, 87, 184, 0.13); }
    .badge-pageindex { color: #8a4a00; background: rgba(255, 209, 102, 0.38); }
    .badge-unknown { color: #6b7280; background: rgba(107, 114, 128, 0.14); }

    .source-score {
        margin-left: auto;
        font-size: 0.72rem;
        color: var(--muted);
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    }

    .source-body {
        color: #4d5660;
        font-size: 0.82rem;
        line-height: 1.45;
        white-space: pre-wrap;
    }

    .sidebar-brand {
        padding: 0.2rem 0 0.8rem;
    }

    .sidebar-name {
        color: var(--phopee-orange-dark);
        font-size: 1.25rem;
        font-weight: 850;
        margin-bottom: 0.15rem;
    }

    .sidebar-copy {
        color: var(--muted);
        font-size: 0.86rem;
        line-height: 1.45;
    }

    .stChatInput textarea {
        border-radius: 8px;
        border-color: rgba(238, 77, 45, 0.28);
        background: #ffffff;
    }

    .stSlider [data-baseweb="slider"] {
        padding-top: 0.35rem;
    }

    @media (max-width: 760px) {
        .phopee-header {
            grid-template-columns: 1fr;
            min-height: 150px;
        }
        .status-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .status-item:nth-child(2) {
            border-right: 0;
        }
        .bubble {
            max-width: calc(100% - 44px);
        }
        .source-wrap {
            margin-left: 0;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DOC_TYPE_BADGES = {
    "legal": ("badge-legal", "Chính sách"),
    "news": ("badge-news", "Hướng dẫn"),
    "pageindex": ("badge-pageindex", "Fallback"),
}

SUGGESTIONS = [
    "Thời hạn yêu cầu trả hàng/hoàn tiền là bao lâu?",
    "Phopee hỗ trợ những phương thức thanh toán nào?",
    "Làm sao để đổi phương thức thanh toán đơn hàng?",
    "Quy định đăng bán sản phẩm cho người bán?",
    "Cần bằng chứng gì khi yêu cầu hoàn tiền?",
]


def escape_text(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_header(top_k: int) -> None:
    st.markdown(
        f"""
        <div class="phopee-shell">
            <div class="phopee-topbar">
                <span>Kênh hỗ trợ RAG</span>
                <span>Trả lời dựa trên tài liệu nội bộ và nguồn trích dẫn</span>
            </div>
            <div class="phopee-header">
                <div>
                    <div class="brand-row">
                        <div class="brand-mark">P</div>
                        <div>
                            <div class="brand-title">Phopee Support</div>
                            <div class="brand-subtitle">
                                Trợ lý hỏi đáp chính sách e-commerce với truy xuất nguồn rõ ràng.
                            </div>
                        </div>
                    </div>
                </div>
                <div class="search-panel">
                    <div class="search-icon">⌕</div>
                    <div class="search-copy">
                        Hỏi về đổi trả, hoàn tiền, thanh toán, theo dõi đơn hàng,
                        quyền riêng tư hoặc quy định người bán.
                    </div>
                </div>
            </div>
            <div class="status-strip">
                <div class="status-item">
                    <div class="status-label">Retrieval</div>
                    <div class="status-value">Hybrid + RRF</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Fallback</div>
                    <div class="status-value">PageIndex</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Citation</div>
                    <div class="status-value">Bắt buộc</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Top K</div>
                    <div class="status-value">{top_k} chunks</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">🛒</div>
            <div class="empty-title">Bạn cần hỗ trợ về chính sách nào?</div>
            <div class="empty-copy">
                Nhập câu hỏi bên dưới hoặc chọn câu hỏi gợi ý ở thanh bên trái.
                Câu trả lời sẽ kèm nguồn tài liệu để bạn đối chiếu khi demo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return

    with st.expander(f"Nguồn tham khảo ({len(sources)} đoạn trích)", expanded=False):
        st.markdown('<div class="source-wrap">', unsafe_allow_html=True)
        for index, source in enumerate(sources, start=1):
            metadata = source.get("metadata", {}) or {}
            source_name = escape_text(
                metadata.get("source") or metadata.get("source_file") or "Unknown source"
            )
            doc_type = str(metadata.get("type") or source.get("source") or "unknown")
            badge_class, badge_label = DOC_TYPE_BADGES.get(
                doc_type, ("badge-unknown", doc_type or "unknown")
            )
            score = source.get("score", 0) or 0
            content = str(source.get("content", "")).strip()
            preview = escape_text(content[:320] + ("..." if len(content) > 320 else ""))

            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-head">
                        <span class="source-rank">{index}</span>
                        <span class="source-name">{source_name}</span>
                        <span class="badge {badge_class}">{escape_text(badge_label)}</span>
                        <span class="source-score">score {score:.4f}</span>
                    </div>
                    <div class="source-body">{preview}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def render_message(role: str, content: str, sources: list[dict] | None = None) -> None:
    safe_content = escape_text(content).replace("\n", "<br>")
    avatar = "U" if role == "user" else "AI"
    row_class = "user" if role == "user" else "assistant"

    st.markdown(
        f"""
        <div class="chat-row {row_class}">
            <div class="avatar {row_class}">{avatar}</div>
            <div class="bubble {row_class}">{safe_content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if role == "assistant":
        render_sources(sources or [])


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-name">Phopee Support</div>
            <div class="sidebar-copy">
                Giao diện demo RAG tông màu sáng, ưu tiên câu trả lời ngắn gọn,
                có citation và danh sách nguồn.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("**Câu hỏi gợi ý**")
    for suggestion in SUGGESTIONS:
        if st.button(suggestion, use_container_width=True, key=f"sug_{suggestion[:24]}"):
            st.session_state.pending_query = suggestion

    st.divider()
    st.markdown("**Thiết lập truy xuất**")
    top_k = st.slider("Số đoạn trích (top_k)", 3, 10, 5)

    st.divider()
    if st.button("Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()

    st.divider()
    st.caption("Pipeline: Semantic + BM25 -> RRF -> PageIndex fallback -> Generation có citation.")

render_header(top_k)

st.markdown('<div class="chat-stage">', unsafe_allow_html=True)
if not st.session_state.messages:
    render_empty_state()

for message in st.session_state.messages:
    render_message(
        role=message["role"],
        content=message["content"],
        sources=message.get("sources", []),
    )
st.markdown("</div>", unsafe_allow_html=True)

user_input = st.chat_input("Nhập câu hỏi về chính sách, thanh toán, đổi trả...")
query = user_input or st.session_state.pending_query

if query:
    st.session_state.pending_query = None
    st.session_state.messages.append({"role": "user", "content": query})
    render_message("user", query)

    with st.spinner("Đang tìm tài liệu và tạo câu trả lời có citation..."):
        try:
            from src.task10_generation import generate_with_citation

            response = generate_with_citation(query, top_k=top_k)
            answer = response.get("answer", "Chưa thể trả lời.")
            sources = response.get("sources", [])
        except NotImplementedError:
            answer = (
                "Task 10 chưa được implement. Hãy hoàn thiện "
                "`src/task10_generation.py` để kết nối pipeline vào UI."
            )
            sources = []
        except Exception as error:
            answer = f"Lỗi khi chạy RAG Pipeline: {error}"
            sources = []

    render_message("assistant", answer, sources)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )
