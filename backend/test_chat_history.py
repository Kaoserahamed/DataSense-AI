from app.models.chat import ChatHistory


def test_chat_history_accepts_legacy_question_answer_code_kwargs():
    history = ChatHistory(
        dataset_id=1,
        question="What is this dataset?",
        answer="It contains sales data.",
        code="print('hello')",
    )

    assert history.user_message == "What is this dataset?"
    assert history.ai_response == "It contains sales data."
    assert history.query_result == {"code": "print('hello')"}
