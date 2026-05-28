from pydantic import BaseModel


class CourseCard(BaseModel):
    title: str
    url: str
    category: str
    level: str | None = None
    duration: str | None = None
    cert_available: bool = False


class CourseResult(BaseModel):
    course: CourseCard
    score: float
