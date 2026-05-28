from pydantic import BaseModel, ConfigDict

from app.domain.course import CourseCategory, CourseLevel


class CourseCard(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    url: str
    category: CourseCategory
    level: CourseLevel
    cert_available: bool
    relevance_score: float | None = None


class CourseResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    course: CourseCard
    score: float
