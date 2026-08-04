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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --phopee-orange: #EE4D2D;
        --phopee-orange-hover: #D73211;
        --phopee-orange-dark: #B8250A;
        --phopee-orange-light: #FF6547;
        --phopee-orange-soft: #FFF5F2;
        --phopee-orange-glow: rgba(238, 77, 45, 0.15);
        --phopee-yellow: #FFB800;
        --phopee-teal: #0D9488;
        --phopee-teal-soft: #EEFCF9;
        --phopee-blue: #2563EB;
        --phopee-blue-soft: #EFF6FF;

        --ink-primary: #1E293B;
        --ink-secondary: #475569;
        --ink-muted: #94A3B8;

        --bg-main: #FAFAF9;
        --bg-gradient: linear-gradient(180deg, #FFF6F3 0%, #FAF8F6 30%, #FFFFFF 100%);
        --surface-white: #FFFFFF;
        --surface-glass: rgba(255, 255, 255, 0.85);

        --border-subtle: rgba(238, 77, 45, 0.12);
        --border-medium: rgba(238, 77, 45, 0.22);
        --border-glass: rgba(255, 255, 255, 0.6);

        --shadow-sm: 0 2px 8px rgba(238, 77, 45, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
        --shadow-md: 0 10px 25px -5px rgba(238, 77, 45, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
        --shadow-lg: 0 20px 35px -10px rgba(184, 37, 10, 0.12), 0 10px 15px -5px rgba(0, 0, 0, 0.04);
        --shadow-hover: 0 14px 28px rgba(238, 77, 45, 0.16);

        --radius-sm: 8px;
        --radius-md: 14px;
        --radius-lg: 20px;
        --radius-pill: 9999px;
    }

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        box-sizing: border-box;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-gradient) !important;
        color: var(--ink-primary);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(238, 77, 45, 0.2);
        border-radius: var(--radius-pill);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--phopee-orange);
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stHeader"] * {
        color: var(--ink-primary) !important;
    }

    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"] {
        background: linear-gradient(180deg, rgba(250,248,246,0) 0%, #FAFAF9 40%, #FFFFFF 100%) !important;
        padding-top: 1rem !important;
    }

    /* Chat Input Styling */
    [data-testid="stChatInput"] {
        background: #FFFFFF !important;
        border: 1.5px solid var(--border-medium) !important;
        border-radius: var(--radius-pill) !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 4px 8px !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--phopee-orange) !important;
        box-shadow: 0 12px 35px rgba(238, 77, 45, 0.2), 0 0 0 3px rgba(238, 77, 45, 0.12) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: var(--ink-primary) !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stChatInputSubmitButton"] {
        background: linear-gradient(135deg, var(--phopee-orange-light), var(--phopee-orange)) !important;
        border-radius: var(--radius-pill) !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stChatInputSubmitButton"]:hover {
        transform: scale(1.05);
        background: var(--phopee-orange-hover) !important;
    }

    [data-testid="stChatInputSubmitButton"] svg {
        fill: #FFFFFF !important;
    }

    .block-container {
        max-width: 1200px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 6rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid var(--border-subtle) !important;
        box-shadow: 4px 0 24px rgba(238, 77, 45, 0.03);
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 46px;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle) !important;
        background: #FFFFFF !important;
        color: var(--ink-primary) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        text-align: left !important;
        white-space: normal !important;
        padding: 0.7rem 1rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--phopee-orange) !important;
        color: var(--phopee-orange-dark) !important;
        background: var(--phopee-orange-soft) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md) !important;
    }

    /* Primary Redesign Shell - Sticky Header */
    .phopee-shell {
        position: sticky;
        top: 3.75rem;
        z-index: 990;
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        overflow: hidden;
        background: var(--surface-white);
        box-shadow: var(--shadow-lg);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .phopee-topbar {
        min-height: 38px;
        padding: 0.5rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        color: #FFFFFF;
        background: linear-gradient(90deg, #9C1D06 0%, var(--phopee-orange-dark) 100%);
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .live-pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10B981;
        margin-right: 6px;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-green 2s infinite;
    }

    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .phopee-header {
        min-height: 120px;
        padding: 1.5rem 1.75rem;
        display: grid;
        grid-template-columns: minmax(220px, 1.2fr) minmax(260px, 1fr);
        align-items: center;
        gap: 1.5rem;
        background: linear-gradient(135deg, #FF6547 0%, var(--phopee-orange) 55%, #D73211 100%);
        color: #FFFFFF;
        position: relative;
    }

    .phopee-header::after {
        content: '';
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        background: radial-gradient(circle at 85% 20%, rgba(255,255,255,0.15) 0%, transparent 50%);
        pointer-events: none;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }

    .brand-mark {
        width: 52px;
        height: 52px;
        border-radius: var(--radius-md);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #FFFFFF;
        color: var(--phopee-orange);
        font-size: 1.8rem;
        font-weight: 800;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        flex: 0 0 52px;
        transition: transform 0.3s ease;
    }

    .brand-mark:hover {
        transform: rotate(-5deg) scale(1.05);
    }

    .brand-title {
        font-size: 1.75rem;
        line-height: 1.1;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .version-tag {
        font-size: 0.65rem;
        padding: 0.2rem 0.5rem;
        background: rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: var(--radius-pill);
        font-weight: 700;
        letter-spacing: 0.05em;
    }

    .brand-subtitle {
        font-size: 0.9rem;
        line-height: 1.4;
        opacity: 0.92;
        margin-top: 0.3rem;
        font-weight: 500;
    }

    .search-panel {
        padding: 0.85rem 1.1rem;
        border-radius: var(--radius-md);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        color: var(--ink-secondary);
        display: flex;
        align-items: center;
        gap: 0.8rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.8);
    }

    .search-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: var(--phopee-orange-soft);
        color: var(--phopee-orange);
        font-size: 1.1rem;
        flex: 0 0 36px;
        box-shadow: 0 2px 8px rgba(238, 77, 45, 0.15);
    }

    .search-copy {
        font-size: 0.86rem;
        line-height: 1.4;
        color: var(--ink-secondary);
        font-weight: 500;
    }

    .status-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0;
        border-top: 1px solid rgba(238, 77, 45, 0.08);
        background: #FFFFFF;
    }

    .status-item {
        padding: 0.85rem 1.25rem;
        border-right: 1px solid var(--border-subtle);
        transition: background 0.2s ease;
    }

    .status-item:hover {
        background: var(--phopee-orange-soft);
    }

    .status-item:last-child {
        border-right: 0;
    }

    .status-label {
        font-size: 0.72rem;
        color: var(--ink-muted);
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.06em;
    }

    .status-value {
        margin-top: 0.2rem;
        font-size: 0.92rem;
        color: var(--ink-primary);
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .chat-stage {
        padding: 1.5rem;
        background: var(--surface-white);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        min-height: 400px;
    }

    .empty-state {
        min-height: 320px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2.5rem 1.5rem;
        color: var(--ink-secondary);
    }

    .empty-icon-wrap {
        position: relative;
        margin-bottom: 1.25rem;
    }

    .empty-icon-wrap::before {
        content: '';
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 90px; height: 90px;
        background: radial-gradient(circle, var(--phopee-orange-glow) 0%, transparent 70%);
        border-radius: 50%;
        z-index: 0;
    }

    .empty-icon {
        position: relative;
        z-index: 1;
        width: 72px;
        height: 72px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-lg);
        background: linear-gradient(135deg, #FFF0EC 0%, #FFE4DC 100%);
        color: var(--phopee-orange);
        font-size: 2.2rem;
        box-shadow: 0 10px 25px rgba(238, 77, 45, 0.15);
        border: 1px solid rgba(238, 77, 45, 0.2);
    }

    .empty-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--ink-primary);
        letter-spacing: -0.01em;
    }

    .empty-copy {
        max-width: 540px;
        margin-top: 0.5rem;
        font-size: 0.92rem;
        line-height: 1.6;
        color: var(--ink-secondary);
    }

    /* Chat Rows */
    .chat-row {
        display: flex;
        gap: 0.85rem;
        margin: 1.1rem 0;
        align-items: flex-start;
        animation: fadeInUp 0.3s ease;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-row.user {
        flex-direction: row-reverse;
    }

    .avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        flex: 0 0 38px;
        box-shadow: var(--shadow-sm);
    }

    .avatar.user {
        color: #FFFFFF;
        background: linear-gradient(135deg, #FF6547, var(--phopee-orange));
    }

    .avatar.assistant {
        color: var(--phopee-orange);
        background: var(--phopee-orange-soft);
        border: 1.5px solid var(--border-medium);
    }

    .bubble {
        width: fit-content;
        max-width: min(800px, calc(100% - 60px));
        border-radius: var(--radius-lg);
        padding: 0.95rem 1.2rem;
        line-height: 1.6;
        font-size: 0.95rem;
        overflow-wrap: anywhere;
        box-shadow: var(--shadow-sm);
    }

    .bubble.user {
        color: #FFFFFF;
        background: linear-gradient(135deg, #FF6547 0%, var(--phopee-orange) 100%);
        border-bottom-right-radius: 4px;
        box-shadow: 0 8px 20px rgba(238, 77, 45, 0.2);
        font-weight: 500;
    }

    .bubble.assistant {
        color: var(--ink-primary);
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-bottom-left-radius: 4px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    }

    .source-wrap {
        margin-left: 48px;
        max-width: 800px;
    }

    .source-card {
        margin: 0.6rem 0;
        padding: 0.85rem 1rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
        border-left: 4px solid var(--phopee-orange);
        background: #FFFBF9;
        transition: all 0.2s ease;
    }

    .source-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        background: #FFFFFF;
    }

    .source-head {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.4rem;
    }

    .source-rank {
        width: 24px;
        height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: var(--phopee-orange);
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 800;
    }

    .source-name {
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--ink-primary);
    }

    .badge {
        padding: 0.2rem 0.55rem;
        border-radius: var(--radius-pill);
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .badge-legal { color: #0D9488; background: #EEFCF9; border: 1px solid rgba(13, 148, 136, 0.2); }
    .badge-news { color: #2563EB; background: #EFF6FF; border: 1px solid rgba(37, 99, 235, 0.2); }
    .badge-pageindex { color: #D97706; background: #FEF3C7; border: 1px solid rgba(217, 119, 6, 0.2); }
    .badge-unknown { color: #64748B; background: #F1F5F9; border: 1px solid rgba(100, 116, 139, 0.2); }

    .source-score {
        margin-left: auto;
        font-size: 0.75rem;
        color: var(--ink-muted);
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        background: #F8FAFC;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        border: 1px solid #E2E8F0;
    }

    .source-body {
        color: var(--ink-secondary);
        font-size: 0.85rem;
        line-height: 1.5;
        white-space: pre-wrap;
    }

    .sidebar-brand {
        padding: 0.5rem 0 0.5rem;
    }

    .sidebar-name {
        color: var(--phopee-orange);
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .sidebar-copy {
        color: var(--ink-secondary);
        font-size: 0.86rem;
        line-height: 1.45;
        margin-top: 0.35rem;
    }

    @media (max-width: 768px) {
        .phopee-header {
            grid-template-columns: 1fr;
            min-height: auto;
            padding: 1.25rem;
        }
        .status-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .status-item:nth-child(2) {
            border-right: 0;
        }
        .bubble {
            max-width: calc(100% - 50px);
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
                <span><span class="live-pulse-dot"></span>Hệ thống hỗ trợ RAG AI chính thức</span>
                <span>Truy xuất chính xác theo tài liệu & Nguồn kiểm chứng</span>
            </div>
            <div class="phopee-header">
                <div>
                    <div class="brand-row">
                        <div class="brand-mark">P</div>
                        <div>
                            <div class="brand-title">
                                Phopee Support
                                <span class="version-tag">RAG v2.4</span>
                            </div>
                            <div class="brand-subtitle">
                                Trợ lý thông minh giải đáp chính sách e-commerce & quy trình vận hành.
                            </div>
                        </div>
                    </div>
                </div>
                <div class="search-panel">
                    <div class="search-icon">🔍</div>
                    <div class="search-copy">
                        Tra cứu tức thì về đổi trả, thanh toán, vận chuyển,
                        bảo mật tài khoản & chính sách Người bán.
                    </div>
                </div>
            </div>
            <div class="status-strip">
                <div class="status-item">
                    <div class="status-label">Engine Retrieval</div>
                    <div class="status-value">⚡ Hybrid + RRF</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Fallback Model</div>
                    <div class="status-value">🛡️ PageIndex</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Trích dẫn nguồn</div>
                    <div class="status-value">📄 Bắt buộc</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Context Limit</div>
                    <div class="status-value">🎯 Top-{top_k} Chunks</div>
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
            <div class="empty-icon-wrap">
                <div class="empty-icon">🛍️</div>
            </div>
            <div class="empty-title">Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?</div>
            <div class="empty-copy">
                Hãy nhập câu hỏi vào ô chat bên dưới hoặc bấm chọn các <b>câu hỏi gợi ý</b> ở menu bên trái.
                Mọi câu trả lời đều đính kèm danh sách trích dẫn tài liệu minh bạch.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return

    with st.expander(f"📚 Nguồn tham khảo ({len(sources)} đoạn trích minh chứng)", expanded=False):
        st.markdown('<div class="source-wrap">', unsafe_allow_html=True)
        for index, source in enumerate(sources, start=1):
            metadata = source.get("metadata", {}) or {}
            source_name = escape_text(
                metadata.get("source") or metadata.get("source_file") or "Tài liệu hệ thống"
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
                        <span class="source-score">relevance: {score:.4f}</span>
                    </div>
                    <div class="source-body">{preview}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def render_message(role: str, content: str, sources: list[dict] | None = None) -> None:
    safe_content = escape_text(content).replace("\n", "<br>")
    avatar = "👤" if role == "user" else "🤖"
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
            <div class="sidebar-name">🛍️ Phopee AI</div>
            <div class="sidebar-copy">
                Trợ lý tra cứu RAG thông minh. Trả lời chính xác, giao diện hiện đại & tối ưu trải nghiệm.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("💡 **Câu hỏi thường gặp**")
    for suggestion in SUGGESTIONS:
        if st.button(f"💬 {suggestion}", use_container_width=True, key=f"sug_{suggestion[:24]}"):
            st.session_state.pending_query = suggestion

    st.divider()
    st.markdown("⚙️ **Cấu hình Truy xuất (RAG)**")
    top_k = st.slider("Số lượng đoạn trích (Top-K)", 3, 10, 5)

    st.divider()
    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()

    st.divider()
    st.caption("🚀 Pipeline: Semantic + BM25 ➔ RRF ➔ PageIndex Fallback ➔ Citation Generation.")

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

    with st.spinner("🔍 Đang truy xuất tài liệu và tổng hợp câu trả lời..."):
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
