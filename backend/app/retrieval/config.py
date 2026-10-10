from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalConfig:
    default_top_k: int = 5
    max_top_k: int = 20
    min_similarity: float = 0.35
    candidate_multiplier: int = 3

    @property
    def candidate_limit(self) -> int:
        return self.max_top_k * self.candidate_multiplier
