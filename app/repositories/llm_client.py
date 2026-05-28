from app.core.config import settings
from app.repositories import BaseRepository


class LLMClient(BaseRepository):
    def complete(self, messages: list[dict]) -> str:
        """Send messages to the configured LLM and return the completion.

        Args:
            messages: List of {role, content} dicts.

        Returns:
            LLM response string.

        Raises:
            ValueError: If LLM_MODEL prefix is not supported.
        """
        if settings.LLM_MODEL.startswith("ollama/"):
            import ollama

            model = settings.LLM_MODEL.replace("ollama/", "")
            r = ollama.chat(model=model, messages=messages)
            return r["message"]["content"]

        elif settings.LLM_MODEL.startswith("gpt"):
            from openai import OpenAI

            r = OpenAI(api_key=settings.OPENAI_API_KEY).chat.completions.create(
                model=settings.LLM_MODEL, messages=messages, max_tokens=1000
            )
            return r.choices[0].message.content

        elif settings.LLM_MODEL.startswith("gemini/"):
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            r = genai.GenerativeModel(
                settings.LLM_MODEL.replace("gemini/", "")
            ).generate_content(messages[-1]["content"])
            return r.text

        elif settings.LLM_MODEL.startswith("anthropic/"):
            from anthropic import Anthropic

            r = Anthropic(api_key=settings.ANTHROPIC_API_KEY).messages.create(
                model=settings.LLM_MODEL.replace("anthropic/", ""),
                max_tokens=1000,
                messages=messages,
            )
            return r.content[0].text

        raise ValueError(f"Unsupported LLM_MODEL: {settings.LLM_MODEL}")
