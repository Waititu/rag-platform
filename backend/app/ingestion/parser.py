from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_TEXT_TYPES = {
    "text/plain",
    "text/markdown",
}


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".pdf",
}


class DocumentParser:
    @staticmethod
    def parse(
        filename: str,
        content_type: str,
        data: bytes,
    ) -> str:
        extension = Path(filename).suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension: {extension}"
            )

        if extension == ".pdf":
            return DocumentParser._parse_pdf(data)

        if extension in {".txt", ".md", ".markdown"}:
            return data.decode("utf-8")

        if content_type in SUPPORTED_TEXT_TYPES:
            return data.decode("utf-8")

        raise ValueError(
            f"Unsupported content type: {content_type}"
        )

    @staticmethod
    def _parse_pdf(data: bytes) -> str:
        reader = PdfReader(BytesIO(data))

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text.strip())

        return "\n\n".join(pages).strip()
