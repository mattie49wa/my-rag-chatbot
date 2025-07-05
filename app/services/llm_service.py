from openai import AsyncOpenAI
from typing import List, Dict, Optional
from app.core.config import settings


class LLMService:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate_answer(
        self, query: str, context_chunks: List[Dict]
    ) -> Dict[str, str]:
        """Generate an answer based on the query and context chunks."""

        # Prepare context from chunks
        context_parts = []
        for chunk in context_chunks:
            source = chunk.get("document_name", "Unknown")
            text = chunk["text"]
            context_parts.append(f"[Source: {source}]\n{text}")

        context = "\n\n---\n\n".join(context_parts)

        # Create the prompt
        system_prompt = """You are a helpful assistant that answers questions based solely on the provided context. 
                            Your task is to answer the user's question using ONLY the information from the provided documents.

                            Important rules:
                            1. Only use information explicitly stated in the provided context
                            2. If the answer cannot be found in the context, clearly state that
                            3. Do not make assumptions or add information not present in the context
                            4. Quote or reference specific parts of the context when possible
                            5. Be concise but thorough in your answer"""

        user_prompt = f"""Context from documents:
                            {context}

                            Question: {query}

                            Please answer the question based only on the provided context."""

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "model_used": self.model,
                "chunks_used": len(context_chunks),
            }

        except Exception as e:
            raise ValueError(f"Error generating answer: {str(e)}")

    async def validate_answer(
        self, query: str, answer: str, context_chunks: List[Dict]
    ) -> str:
        """Validate if the answer properly addresses the query (Enhancement 1)."""

        # Prepare context summary
        context_summary = f"Used {len(context_chunks)} chunks from documents"

        validation_prompt = f"""You are a validation assistant. Your task is to check if an answer properly addresses a question based on the provided context.

                                Question: {query}
                                Answer: {answer}
                                Context info: {context_summary}

                                Evaluate:
                                1. Does the answer directly address the question?
                                2. Is the answer based on the provided context?
                                3. Does the answer acknowledge any limitations or missing information?

                                Provide a brief confidence note about the answer quality."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful validation assistant.",
                    },
                    {"role": "user", "content": validation_prompt},
                ],
                temperature=0.1,
                max_tokens=200,
            )

            return response.choices[0].message.content

        except Exception as e:
            return "Could not validate answer"
