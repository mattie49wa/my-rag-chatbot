import httpx
import pdfplumber
from typing import List, Dict
import tempfile
import os
from app.core.config import settings


class PDFProcessor:
    def __init__(self):
        self.max_size = settings.max_pdf_size_mb * 1024 * 1024
        self.timeout = settings.pdf_download_timeout

    async def download_pdf(self, url: str) -> bytes:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, timeout=self.timeout, follow_redirects=True
                )
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                if "pdf" not in content_type.lower():
                    raise ValueError(
                        f"URL does not point to a PDF file: {content_type}"
                    )

                content_length = int(response.headers.get("content-length", 0))
                if content_length > self.max_size:
                    raise ValueError(f"PDF file too large: {content_length} bytes")

                return response.content

            except httpx.TimeoutException:
                raise ValueError(f"Timeout downloading PDF from {url}")
            except httpx.HTTPStatusError as e:
                raise ValueError(
                    f"HTTP error downloading PDF: {e.response.status_code}"
                )

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        text_parts = []

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name

        try:
            with pdfplumber.open(tmp_file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            # Add page number for reference
                            text_parts.append(f"[Page {page_num}]\n{text}")
                    except Exception as e:
                        print(f"Error extracting text from page {page_num}: {e}")
                        continue
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

        return "\n\n".join(text_parts)

    async def process_documents(self, document_urls: List[str]) -> Dict[str, str]:
        documents = {}

        for url in document_urls:
            try:
                pdf_content = await self.download_pdf(url)

                text = self.extract_text_from_pdf(pdf_content)

                if text.strip():
                    documents[url] = text
                else:
                    raise ValueError("No text could be extracted from PDF")

            except Exception as e:
                print(f"Error processing {url}: {e}")
                documents[url] = f"Error: {str(e)}"

        return documents
