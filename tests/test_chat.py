from app.chat import ChatService


def test_empty_message_rejected():
    try:
        ChatService.send_message(
            db=None,
            conversation=None,
            content="",
            top_k=5,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Message cannot be empty"

