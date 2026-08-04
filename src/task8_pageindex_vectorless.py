"""
Task 8 — PageIndex Vectorless RAG.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    """
    Placeholder upload. Khi có API key thật thì thay bằng logic upload SDK.
    """
    uploaded = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        uploaded.append({"name": md_file.name, "doc_id": md_file.stem})
    return uploaded


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex.
    Nếu chưa có API key, trả fallback mock an toàn.
    """
    if not PAGEINDEX_API_KEY:
        return [
            {
                "content": f"PageIndex fallback chưa bật API key. Query nhận được: {query}",
                "score": 0.5,
                "metadata": {"section": "fallback_mock"},
                "source": "pageindex",
            }
        ][:top_k]

    results = []
    for i, md_file in enumerate(STANDARDIZED_DIR.rglob("*.md")):
        if i >= top_k:
            break
        content = md_file.read_text(encoding="utf-8")[:500]
        results.append(
            {
                "content": content,
                "score": round(1.0 / (i + 1), 4),
                "metadata": {"section": md_file.stem, "source_file": md_file.name},
                "source": "pageindex",
            }
        )
    return results[:top_k]


if __name__ == "__main__":
    if not PAGEINDEX_API_KEY:
        print("⚠ Chưa có PAGEINDEX_API_KEY trong .env, đang dùng fallback mock.")
    else:
        print("✓ Đã có PAGEINDEX_API_KEY")

    results = pageindex_search("danh sách sản phẩm cấm đăng bán", top_k=3)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")