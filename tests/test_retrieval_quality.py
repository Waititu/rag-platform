import pytest

from app.retrieval.config import RetrievalConfig
from app.retrieval.service import RetrievalService


def test_default_retrieval_configuration():
    config = RetrievalConfig()

    assert config.default_top_k == 5
    assert config.max_top_k == 20
    assert config.min_similarity == 0.35
    assert config.candidate_multiplier == 3


def test_candidate_limit():
    config = RetrievalConfig(
        max_top_k=10,
        candidate_multiplier=3,
    )

    assert config.candidate_limit == 30


def test_similarity_threshold_validation():
    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        RetrievalService._validate_similarity_threshold(-0.1)

    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        RetrievalService._validate_similarity_threshold(1.1)


def test_query_validation():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        RetrievalService._validate_query("")

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        RetrievalService._validate_query("   ")


def test_top_k_validation():
    service = RetrievalService.__new__(RetrievalService)

    service.config = RetrievalConfig(
        max_top_k=20
    )

    with pytest.raises(
        ValueError,
        match="between 1 and 20",
    ):
        service._validate_top_k(0)

    with pytest.raises(
        ValueError,
        match="between 1 and 20",
    ):
        service._validate_top_k(21)

    with pytest.raises(
        ValueError,
        match="integer",
    ):
        service._validate_top_k("5")
