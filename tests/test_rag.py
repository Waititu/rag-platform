from app.rag import RAGService


def test_empty_question_rejected():
    try:
        RAGService.answer(
            db=None,
            question="",
            top_k=5,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Question cannot be empty"
