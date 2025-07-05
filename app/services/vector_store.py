import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import pickle
import os
from app.core.config import settings


class VectorStore:
    def __init__(self):
        try:
            print(f"Loading embedding model: {settings.embedding_model}")
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            print("Embedding model loaded successfully")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            raise
        self.index = None
        self.chunks = []
        self.dimension = None

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts."""
        # Convert texts to embeddings
        embeddings = self.embedding_model.encode(
            texts, convert_to_numpy=True, show_progress_bar=True
        )
        return embeddings

    def build_index(self, chunks: List[Dict]):
        """Build FAISS index from chunks."""
        if not chunks:
            raise ValueError("No chunks provided to build index")

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.create_embeddings(texts)

        self.dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(self.dimension)

        self.index.add(embeddings.astype("float32"))

        self.chunks = chunks

        print(f"Built index with {len(chunks)} chunks")

    def search(self, query: str, top_k: int = settings.top_k_chunks) -> List[Dict]:
        """Search for similar chunks given a query."""
        if self.index is None:
            raise ValueError("Index not built. Call build_index first.")

        query_embedding = self.create_embeddings([query])[0]

        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype("float32"),
            min(top_k, len(self.chunks)),
        )

        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(dist)
                chunk["rank"] = i + 1
                results.append(chunk)

        return results

    def save_index(self, path: str = settings.faiss_index_path):
        os.makedirs(path, exist_ok=True)

        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, os.path.join(path, "index.faiss"))

        # Save chunks and metadata
        with open(os.path.join(path, "chunks.pkl"), "wb") as f:
            pickle.dump({"chunks": self.chunks, "dimension": self.dimension}, f)

    def load_index(self, path: str = settings.faiss_index_path):
        index_path = os.path.join(path, "index.faiss")
        chunks_path = os.path.join(path, "chunks.pkl")

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            raise ValueError(f"Index files not found at {path}")

        # Load FAISS index
        self.index = faiss.read_index(index_path)

        # Load chunks and metadata
        with open(chunks_path, "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.dimension = data["dimension"]
