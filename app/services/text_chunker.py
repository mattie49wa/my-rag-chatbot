from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings


class TextChunker:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            is_separator_regex=False,
        )

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata.

        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of dictionaries containing chunk text and metadata
        """
        if not text or not text.strip():
            return []

        chunks = self.text_splitter.split_text(text)

        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_obj = {
                "text": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
            }

            if metadata:
                chunk_obj.update(metadata)

            chunk_objects.append(chunk_obj)

        return chunk_objects

    def chunk_documents(self, documents: Dict[str, str]) -> List[Dict]:
        """
        Chunk multiple documents.

        Args:
            documents: Dictionary mapping document URLs to their text content

        Returns:
            List of all chunks from all documents
        """
        all_chunks = []

        for doc_url, doc_text in documents.items():
            if doc_text.startswith("Error:"):
                continue

            metadata = {"source": doc_url, "document_name": doc_url.split("/")[-1]}

            chunks = self.chunk_text(doc_text, metadata)
            all_chunks.extend(chunks)

        return all_chunks
