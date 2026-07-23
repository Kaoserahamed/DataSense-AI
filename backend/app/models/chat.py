from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text)
    query_result = Column(JSON)
    chart_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="chat_history")

    @property
    def question(self):
        return self.user_message

    @question.setter
    def question(self, value):
        self.user_message = value

    @property
    def answer(self):
        return self.ai_response

    @answer.setter
    def answer(self, value):
        self.ai_response = value

    @property
    def code(self):
        if isinstance(self.query_result, dict):
            return self.query_result.get("code")
        return None

    @code.setter
    def code(self, value):
        if isinstance(self.query_result, dict):
            self.query_result["code"] = value
        else:
            self.query_result = {"code": value}

    def __init__(self, *args, **kwargs):
        if "question" in kwargs and "user_message" not in kwargs:
            kwargs["user_message"] = kwargs.pop("question")
        if "answer" in kwargs and "ai_response" not in kwargs:
            kwargs["ai_response"] = kwargs.pop("answer")
        if "code" in kwargs and "query_result" not in kwargs:
            kwargs["query_result"] = {"code": kwargs.pop("code")}
        super().__init__(*args, **kwargs)
