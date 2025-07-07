from typing import Dict, List
from app.services.pdf_processor import PDFProcessor
from app.services.text_chunker import TextChunker
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService
from app.core.config import settings


class QueryProcessor:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_chunker = TextChunker()
        self.vector_store = None
        self.llm_service = None

    def _get_vector_store(self):
        """Lazy initialization of vector store."""
        if self.vector_store is None:
            self.vector_store = VectorStore()
        return self.vector_store

    def _get_llm_service(self):
        if self.llm_service is None:
            self.llm_service = LLMService()
        return self.llm_service

    async def process_query(
        self, query: str, document_urls: List[str], validate: bool = True
    ) -> Dict:
        """
        Process a query against documents.

        Args:
            query: The user's question
            document_urls: List of PDF URLs to process
            validate: Whether to validate the answer (Enhancement 1)

        Returns:
            Dictionary with answer and metadata
        """
        try:
            print("Step 1: Processing PDFs...")
            documents = await self.pdf_processor.process_documents(document_urls)

            valid_docs = {
                k: v for k, v in documents.items() if not v.startswith("Error:")
            }
            if not valid_docs:
                return {
                    "answer": "Could not process any of the provided documents.",
                    "error": "All document processing failed",
                    "document_errors": documents,
                }

            print("Step 2: Chunking documents...")
            chunks = self.text_chunker.chunk_documents(documents)
            print(f"Created {len(chunks)} chunks")

            print("Step 3: Building vector index...")
            vector_store = self._get_vector_store()
            vector_store.build_index(chunks)

            print("Step 4: Searching for relevant chunks...")
            relevant_chunks = vector_store.search(query, top_k=settings.top_k_chunks)
            if not relevant_chunks:
                return {
                    "answer": "No relevant information found in the documents for your query.",
                    "chunks_found": 0,
                }

            # Step 5: Generate answer using LLM
            print("Step 5: Generating answer...")
            llm_service = self._get_llm_service()
            result = await llm_service.generate_answer(query, relevant_chunks)

            # Step 6: Validate answer (Enhancement 1)
            confidence_note = None
            if validate:
                print("Step 6: Validating answer...")
                confidence_note = await llm_service.validate_answer(
                    query, result["answer"], relevant_chunks
                )

            # Prepare response
            response = {
                "answer": result["answer"],
                "metadata": {
                    "chunks_used": result["chunks_used"],
                    "total_chunks": len(chunks),
                    "documents_processed": len(valid_docs),
                    "model_used": result["model_used"],
                },
            }

            if confidence_note:
                response["confidence_note"] = confidence_note

            return response

        except Exception as e:
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "error": str(e),
            }
