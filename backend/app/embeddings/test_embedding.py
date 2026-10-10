from unittest.mock import Mock

import pytest

from app.embeddings.service import EmbeddingService


def test_embedding_service_returns_768_dimensions(monkeypatch):
    fake_embedding = [0.1] * 768

    response = Mock()
    response.json.return_value = {
        "embeddings": [fake_embedding]
    }
    response.raise_for_status.return_value = None

    def mock_post(*args, **kwargs):
        return response

    monkeypatch.setattr(
        "app.embeddings.service.requests.post",
        mock_post,
    )

    service = EmbeddingService()

    embedding = service.embed(
        "Amazon Web Services provides cloud computing infrastructure."
    )

    assert len(embedding) == 768


def test_embedding_service_rejects_empty_text():
    service = EmbeddingService()

    with pytest.raises(
        ValueError,
        match="Text cannot be empty",
    ):
        service.embed("")
