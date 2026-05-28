from app.core.config import settings
from app.repositories.llm_client import LLMClient, LLMClientError
from app.services import BaseService, ServiceError

_SYSTEM_PROMPT = (
    "You are a learning advisor for the Linux Foundation.\n"
    "Given a learner's background and career goal, recommend a personalised learning path\n"
    "using ONLY the courses provided in context.\n"
    "Always cite course names and include their URLs.\n"
    "Be specific, actionable, and honest about prerequisites."
)


class LLMError(ServiceError):
    pass


class LLMService(BaseService):
    def __init__(self, llm_client: LLMClient) -> None:
        self._client = llm_client

    def _format_courses(self, courses: list[dict]) -> str:
        lines = []
        for i, course in enumerate(courses, 1):
            lines.append(
                f"{i}. {course.get('title', 'Untitled')} — {course.get('url', '')}"
            )
            desc = course.get("description", "")
            if desc:
                lines.append(f"   {desc[:200]}")
        return "\n".join(lines)

    def generate(self, query: str, courses: list[dict]) -> str:
        """Generate a learning roadmap from the query context and retrieved courses.

        Args:
            query: Formatted learner background and career goal string.
            courses: Retrieved course metadata dicts from the vector store.

        Returns:
            LLM-generated roadmap string.

        Raises:
            LLMError: On LLM call failure.
        """
        user_prompt = (
            f"{query}\n\n"
            f"Available courses from the LF catalog:\n{self._format_courses(courses)}\n\n"
            "Recommend a step-by-step learning path."
        )
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        try:
            response = self._client.complete(messages)
        except LLMClientError as exc:
            raise LLMError(f"LLM generation failed: {exc}") from exc
        self.logger.info(
            "llm_generation_complete",
            model=settings.LLM_MODEL,
            response_length=len(response),
        )
        return response
