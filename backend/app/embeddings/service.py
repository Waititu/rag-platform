import requests

from app.config import get_settings


class EmbeddingService:
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_url.rstrip("/")
        self.model = settings.embedding_model

    def embed(self, text: str) -> list[float]:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text cannot be empty.")

        response = requests.post(
            f"{self.base_url}/api/embed",
            json={
                "model": self.model,
                "input": text,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        embeddings = data.get("embeddings")

        if not embeddings:
            raise RuntimeError(
                "Embedding service returned no embeddings."
            )

        embedding = embeddings[0]

        if len(embedding) != 768:
            raise RuntimeError(
                f"Expected 768-dimensional embedding, "
                f"received {len(embedding)}."
            )

        return embedding
