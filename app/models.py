"""Request and response models for the ScriptForge API."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class VideoStyle(str, Enum):
    educational = "Educational"
    storytelling = "Storytelling"
    documentary = "Documentary"
    motivational = "Motivational"
    listicle = "Listicle"
    conversational = "Conversational"


class ScriptLength(str, Enum):
    short = "Short"
    medium = "Medium"
    long = "Long"


class ScriptRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=180)
    style: VideoStyle
    length: ScriptLength

    @field_validator("topic")
    @classmethod
    def clean_topic(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not any(character.isalnum() for character in cleaned):
            raise ValueError("Topic must contain letters or numbers")
        return cleaned


class ScriptResponse(BaseModel):
    id: int
    topic: str
    style: VideoStyle
    length: ScriptLength
    hook: str
    introduction: str
    main_content: str
    call_to_action: str
    titles: list[str]
    thumbnail_ideas: list[str]
    full_script: str
    word_count: int
    estimated_minutes: float
    created_at: datetime


class HistoryItem(BaseModel):
    id: int
    topic: str
    style: VideoStyle
    length: ScriptLength
    word_count: int
    created_at: datetime

