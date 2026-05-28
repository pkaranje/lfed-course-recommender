from app.repositories.llm_client import LLMClient
from app.services import BaseService


class LLMService(BaseService):
    def __init__(self, llm_client: LLMClient) -> None:
        self._client = llm_client

    def generate(self, query: str, courses: list[dict]) -> str:
        """Generate a learning roadmap from query and retrieved courses.

        Args:
            query: User query with skills and goal.
            courses: Retrieved course metadata dicts.

        Returns:
            LLM-generated roadmap string.
        """
        raise NotImplementedError
