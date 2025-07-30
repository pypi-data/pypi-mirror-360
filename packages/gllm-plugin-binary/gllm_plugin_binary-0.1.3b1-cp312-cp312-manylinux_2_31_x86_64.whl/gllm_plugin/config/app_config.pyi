from pydantic import BaseModel
from typing import TypeVar

Chatbot = TypeVar('Chatbot')

class AppConfig(BaseModel):
    """Application configuration model."""
    chatbots: dict[str, Chatbot]
    user_chatbots: dict[str, list[str]]
