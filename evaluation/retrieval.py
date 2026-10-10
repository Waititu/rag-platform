import json
from pathlib import Path

from app.db.database import SessionLocal
from app.retrieval.service import RetrievalService


DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset():
    with DATASET_PATH.open() as f:
        return json.load(f)


def evaluate():
    dataset = load_dataset()
    session = SessionLocal()
    retrieval = RetrievalService(session)

    results = []

    try:
        for case in dataset:
            matches = retrieval.search(
                query=case["question"],
                top_k=5,
            )

            documents = [
                result["filename"]
                for result in matches
            ]

            expected = case["expected_document"]

            result = {
                "id": case["id"],
                "question": case["question"],
                "expected_document": expected,
                "retrieved_documents": documents,
                "hit_at_1": expected in documents[:1],
                "hit_at_3": expected in documents[:3],
                "hit_at_5": expected in documents[:5],
            }

            results.append(result)

            print(f"\n{case['id']}")
            print(f"Question: {case['question']}")
            print(f"Expected: {expected}")
            print(f"Retrieved: {documents}")
            print(f"Hit@1: {result['hit_at_1']}")
            print(f"Hit@3: {result['hit_at_3']}")
            print(f"Hit@5: {result['hit_at_5']}")

    finally:
        session.close()

    total = len(results)

    hit_at_1 = sum(r["hit_at_1"] for r in results)
    hit_at_3 = sum(r["hit_at_3"] for r in results)
    hit_at_5 = sum(r["hit_at_5"] for r in results)

    print("\n" + "=" * 50)
    print("RETRIEVAL EVALUATION")
    print("=" * 50)

    print(f"Cases:  {total}")

    print(
        f"Hit@1:  {hit_at_1}/{total} "
        f"({hit_at_1 / total:.1%})"
    )

    print(
        f"Hit@3:  {hit_at_3}/{total} "
        f"({hit_at_3 / total:.1%})"
    )

    print(
        f"Hit@5:  {hit_at_5}/{total} "
        f"({hit_at_5 / total:.1%})"
    )


if __name__ == "__main__":
    evaluate()
