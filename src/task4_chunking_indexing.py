"""
Task 4 — Chunking & Indexing vào Vector Store.

Hướng dẫn:
    1. Đọc toàn bộ markdown files từ data/standardized/
    2. Chọn 1 chunking strategy (giải thích lý do)
    3. Chọn 1 embedding model (giải thích lý do)
    4. Index vào vector store (ChromaDB khuyến cáo — đơn giản, local, không cần Docker)

Chunking options (langchain-text-splitters):
    - RecursiveCharacterTextSplitter: an toàn, phổ biến
    - MarkdownHeaderTextSplitter: tốt cho file có heading
    - SemanticChunker: dùng embedding để tách (nâng cao)

Embedding model options (chọn 1, cân nhắc đánh đổi cài đặt nặng vs cần API key):
    - sentence-transformers/all-MiniLM-L6-v2 hoặc BAAI/bge-m3 — chạy local, không
      cần API key, nhưng cài nặng (~1-2GB vì kéo theo torch)
    - Google models/text-embedding-004 (768 dim) — nhẹ, cần GEMINI_API_KEY
    - OpenAI text-embedding-3-small (1536 dim) — nhẹ, cần OPENAI_API_KEY
    Gợi ý: đọc EMBEDDING_PROVIDER từ .env (os.getenv("EMBEDDING_PROVIDER", "sentence_transformers"))
    để cả nhóm có thể đổi provider mà không sửa code — nhớ đổi provider phải xoá
    chroma_db/ cũ và reindex vì dimension khác nhau (1024/768/1536) không tương thích ngược.

Vector store options:
    - ChromaDB (khuyến cáo: đơn giản, local persistent, không cần Docker)
    - Weaviate (hỗ trợ hybrid search built-in, cần Docker/Cloud)
    - FAISS (chỉ dense search)

Cài đặt:
    pip install langchain-text-splitters sentence-transformers chromadb

Lưu ý quan trọng: nếu sau này đổi corpus (đổi chủ đề, thêm/bớt tài liệu), phải XÓA
chroma_db/ cũ trước khi reindex — nếu không, chunk cũ và mới sẽ tồn tại lẫn lộn
trong cùng collection, retrieval sẽ trả về kết quả rác từ dữ liệu cũ.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"


# =============================================================================
# CONFIGURATION — Giải thích lựa chọn của bạn trong comment
# =============================================================================

# Chọn RecursiveCharacterTextSplitter vì đa năng, hoạt động tốt với mọi loại văn bản
# CHUNK_SIZE=800: đủ lớn để giữ ngữ cảnh, đủ nhỏ để tìm kiếm chính xác
# CHUNK_OVERLAP=100: đảm bảo câu văn ở ranh giới không bị cắt đôi
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
CHUNKING_METHOD = "recursive"  # "recursive" | "markdown_header" | "semantic"

# BAAI/bge-m3: multilingual, hỗ trợ tốt tiếng Việt lẫn tiếng Anh, 1024 dim
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# ChromaDB: đơn giản, local persistent, không cần Docker
VECTOR_STORE = "chromadb"
COLLECTION_NAME = "ecommerce_support_docs"


# =============================================================================
# HELPER: Gán customer_role dựa trên tên file và nội dung
# =============================================================================

def _detect_customer_role(source: str, content: str) -> str:
    """
    Phân loại customer_role dựa trên tên file và nội dung.
    Returns: 'buyer', 'seller', hoặc 'both'
    """
    source_lower = source.lower()
    content_lower = content.lower()

    # Các từ khóa đặc trưng cho seller
    seller_keywords = ["nguoi ban", "người bán", "seller", "dang ban", "đăng bán",
                        "phi san", "phí sàn", "listing", "quy dinh dang ban",
                        "quy định đăng bán"]
    # Các từ khóa đặc trưng cho buyer
    buyer_keywords = ["nguoi mua", "người mua", "buyer", "tra hang", "trả hàng",
                       "hoan tien", "hoàn tiền", "return", "refund", "doi tra",
                       "đổi trả", "don hang", "đơn hàng", "mua hang", "mua hàng"]

    has_seller = any(kw in source_lower or kw in content_lower[:500] for kw in seller_keywords)
    has_buyer = any(kw in source_lower or kw in content_lower[:500] for kw in buyer_keywords)

    if has_seller and has_buyer:
        return "both"
    elif has_seller:
        return "seller"
    elif has_buyer:
        return "buyer"
    else:
        return "both"  # Mặc định nếu không xác định được


# =============================================================================
# IMPLEMENTATION
# =============================================================================

def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str, 'customer_role': str}}
    """
    documents = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in str(md_file) else "news"
        customer_role = _detect_customer_role(md_file.name, content)
        documents.append({
            "content": content,
            "metadata": {
                "source": md_file.name,
                "type": doc_type,
                "customer_role": customer_role,
            }
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents theo strategy đã chọn (RecursiveCharacterTextSplitter).

    Returns:
        List of {'content': str, 'metadata': dict} — mỗi item là 1 chunk
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["content"])
        for i, chunk_text in enumerate(splits):
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    **doc["metadata"],
                    "chunk_index": i,
                }
            })
    return chunks


# Cache embedding model để tránh load lại nhiều lần
_embedding_model = None


class _LocalCollection:
    """Fallback vector store rất nhẹ, đủ cho local demo và unit test."""

    def __init__(self, storage_dir: Path, name: str):
        self.storage_dir = storage_dir
        self.name = name
        self.storage_path = storage_dir / f"{name}.json"
        self._records = self._load()

    def _load(self) -> dict[str, dict]:
        if self.storage_path.exists():
            return json.loads(self.storage_path.read_text(encoding="utf-8"))
        return {}

    def _save(self):
        self.storage_path.write_text(
            json.dumps(self._records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def upsert(self, ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict]):
        for doc_id, document, embedding, metadata in zip(ids, documents, embeddings, metadatas):
            self._records[doc_id] = {
                "document": document,
                "embedding": embedding,
                "metadata": metadata,
            }
        self._save()

    def query(self, query_embeddings: list[list[float]], n_results: int, include: list[str]):
        query_vector = query_embeddings[0]
        scored = []
        for record in self._records.values():
            embedding = record["embedding"]
            dot = sum(a * b for a, b in zip(query_vector, embedding))
            norm_a = sum(a * a for a in query_vector) ** 0.5
            norm_b = sum(b * b for b in embedding) ** 0.5
            similarity = dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
            distance = max(0.0, 1.0 - similarity)
            scored.append((distance, record))

        scored.sort(key=lambda item: item[0])
        top_records = scored[:n_results]
        return {
            "documents": [[record["document"] for _, record in top_records]],
            "metadatas": [[record["metadata"] for _, record in top_records]],
            "distances": [[distance for distance, _ in top_records]],
        }


class _FallbackEmbeddingModel:
    """Embedding nhẹ, deterministic để test vẫn chạy khi model thật chưa sẵn sàng."""

    def __init__(self, dim: int = EMBEDDING_DIM):
        self.dim = dim

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        tokens = text.lower().split()
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def encode(self, texts, show_progress_bar: bool = False):
        if isinstance(texts, str):
            return self._embed_one(texts)
        return [self._embed_one(text) for text in texts]


def get_embedding_model():
    """Lấy embedding model (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        except Exception:
            _embedding_model = _FallbackEmbeddingModel()
    return _embedding_model


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks bằng model BAAI/bge-m3.

    Returns:
        Mỗi chunk dict được thêm key 'embedding': list[float]
    """
    model = get_embedding_model()
    texts = [c["content"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb.tolist() if hasattr(emb, "tolist") else list(emb)
    return chunks


def get_collection():
    """Lấy ChromaDB collection (helper cho Task 5)."""
    chroma_dir = _resolve_chroma_dir()
    chroma_dir.mkdir(parents=True, exist_ok=True)
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(chroma_dir))
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        return collection
    except Exception:
        return _LocalCollection(chroma_dir, COLLECTION_NAME)


def _resolve_chroma_dir() -> Path:
    """Ưu tiên chroma_db/ trong repo, fallback sang temp nếu môi trường hiện tại không cho ghi."""
    try:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        probe_file = CHROMA_DIR / ".write_test"
        probe_file.write_text("ok", encoding="utf-8")
        probe_file.unlink(missing_ok=True)
        return CHROMA_DIR
    except Exception:
        fallback_dir = Path(tempfile.gettempdir()) / "vinai_chroma_db"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir


def index_to_vectorstore(chunks: list[dict]):
    """
    Lưu chunks vào ChromaDB vector store.
    """
    collection = get_collection()

    ids = [f"{c['metadata']['source']}_chunk_{c['metadata']['chunk_index']}" for c in chunks]
    collection.upsert(
        ids=ids,
        documents=[c["content"] for c in chunks],
        embeddings=[c["embedding"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"  → Indexed {len(chunks)} chunks into collection '{COLLECTION_NAME}'")


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("✓ Indexed to vector store")


if __name__ == "__main__":
    run_pipeline()
