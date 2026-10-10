import pytest

from app.retrieval.service import RetrievalService


def test_empty_query_rejected():
    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        RetrievalService._validate_query("")


def test_whitespace_query_rejected():
    with pytest.raises(
        ValueError,
        match="Query cannot be empty",
    ):
        RetrievalService._validate_query("   ")


def test_invalid_top_k_rejected():
    service = RetrievalService.__new__(RetrievalService)

    from app.retrieval.config import RetrievalConfig

    service.config = RetrievalConfig()

    with pytest.raises(
        ValueError,
        match="between 1 and 20",
    ):
        service._validate_top_k(0)


def test_excessive_top_k_rejected():
    service = RetrievalService.__new__(RetrievalService)

    from app.retrieval.config import RetrievalConfig

    service.config = RetrievalConfig()

    with pytest.raises(
        ValueError,
        match="between 1 and 20",
    ):
        service._validate_top_k(21)


def test_non_integer_top_k_rejected():
    service = RetrievalService.__new__(RetrievalService)

    from app.retrieval.config import RetrievalConfig

    service.config = RetrievalConfig()

    with pytest.raises(
        ValueError,
        match="must be an integer",
    ):
        service._validate_top_k("5")
