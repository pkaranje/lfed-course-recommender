from typing import Optional

from pydantic import BaseModel, HttpUrl


class CourseCard(BaseModel):
    title: str
    url: str
    category: str
    level: Optional[str] = None
    duration: Optional[str] = None
    cert_available: bool = False


class CourseResult(BaseModel):
    course: CourseCard
    score: float
