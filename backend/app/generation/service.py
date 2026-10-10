import json
import requests
from app.config import get_settings


class GenerationService:
    @staticmethod
    def generate(
        question: str,
        context: str,
    ) -> str:
        settings = get_settings()

        prompt = (
            "Answer the user's question using only the provided "
            "context. If the context does not contain enough "
            "information, say that the information is not available "
            "in the indexed documents.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )

        response = requests.post(
            f"{settings.ollama_url.rstrip('/')}/api/chat",
            json={
                "model": settings.generation_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a retrieval-augmented "
                            "question answering assistant. "
                            "Use only the supplied context."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "stream": False,
            },
            timeout=settings.request_timeout_seconds,
        )

        response.raise_for_status()
        data = response.json()

        return data["message"]["content"]

    @staticmethod
    def stream(
        question: str,
        context: str,
    ):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question cannot be empty")

        if not isinstance(context, str) or not context.strip():
            raise ValueError("Context cannot be empty")

        settings = get_settings()

        prompt = (
            "Answer the user's question using only the provided "
            "context. If the context does not contain enough "
            "information, say that the information is not available "
            "in the indexed documents.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )

        response = requests.post(
            f"{settings.ollama_url.rstrip('/')}/api/chat",
            json={
                "model": settings.generation_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a retrieval-augmented "
                            "question answering assistant. "
                            "Use only the supplied context."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "stream": True,
            },
            timeout=settings.request_timeout_seconds,
            stream=True,
        )

        try:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                payload = json.loads(line)

                content = payload.get("message", {}).get(
                    "content",
                    "",
                )

                if content:
                    yield content

        finally:
            response.close()
