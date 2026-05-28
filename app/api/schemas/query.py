from pydantic import BaseModel, ConfigDict, field_validator

from app.api.schemas.course import CourseCard
from app.domain.course import CourseCategory


class RecommendRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    skills: str
    goal: str
    category: CourseCategory | None = None
    top_k: int = 5

    @field_validator("skills", "goal")
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("must be at least 3 characters")
        if len(v) > 500:
            raise ValueError("must be at most 500 characters")
        return v


class RecommendResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    roadmap: str
    courses: list[CourseCard]
    model_used: str
