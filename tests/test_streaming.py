import json

from app.generation.service import GenerationService


class FakeResponse:
    def __init__(self, lines):
        self.lines = lines
        self.closed = False

    def raise_for_status(self):
        pass

    def iter_lines(self):
        return self.lines

    def close(self):
        self.closed = True


def test_generation_stream(monkeypatch):
    response = FakeResponse(
        [
            b'{"message":{"content":"Hello"}}',
            b'{"message":{"content":" world"}}',
            b'{"message":{"content":"!"},"done":true}',
        ]
    )

    def fake_post(*args, **kwargs):
        assert kwargs["stream"] is True
        assert kwargs["json"]["stream"] is True
        assert kwargs["json"]["model"] == "gemma4:12b"

        return response

    monkeypatch.setattr(
        "app.generation.service.requests.post",
        fake_post,
    )

    chunks = list(
        GenerationService.stream(
            question="What is AWS?",
            context="AWS provides cloud computing services.",
        )
    )

    assert chunks == [
        "Hello",
        " world",
        "!",
    ]

    assert response.closed is True


def test_generation_stream_rejects_empty_question():
    try:
        list(
            GenerationService.stream(
                question="",
                context="Some context",
            )
        )

        assert False, "Expected ValueError"

    except ValueError as exc:
        assert str(exc) == "Question cannot be empty"


def test_generation_stream_rejects_empty_context():
    try:
        list(
            GenerationService.stream(
                question="What is AWS?",
                context="",
            )
        )

        assert False, "Expected ValueError"

    except ValueError as exc:
        assert str(exc) == "Context cannot be empty"
