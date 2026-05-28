from pydantic import BaseModel, ConfigDict


class CourseCard(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str
    url: str
    category: str
    level: str
    cert_available: bool
    relevance_score: float | None = None


class CourseResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    course: CourseCard
    score: float
