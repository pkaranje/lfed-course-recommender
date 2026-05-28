from pydantic import BaseModel, Field

from app.api.schemas.course import CourseCard


class RecommendRequest(BaseModel):
    skills: str = Field(..., min_length=1, max_length=500)
    goal: str = Field(..., min_length=1, max_length=500)
    category: str | None = None


class RecommendResponse(BaseModel):
    roadmap: str
    courses: list[CourseCard]
