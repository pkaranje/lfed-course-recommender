from app.core.config import settings
from app.repositories._base import BaseRepository, RepositoryError


class LLMClientError(RepositoryError):
    pass


class LLMClient(BaseRepository):
    def complete(self, messages: list[dict]) -> str:
        """Send messages to the configured LLM and return the completion.

        Args:
            messages: List of {role, content} dicts.

        Returns:
            LLM response string.

        Raises:
            LLMClientError: On any SDK failure.
            ValueError: If LLM_MODEL prefix is not supported.
        """
        model = settings.LLM_MODEL

        try:
            if model.startswith("ollama/"):
                import ollama

                model_name = model.replace("ollama/", "")
                client = ollama.Client(host=settings.OLLAMA_HOST)
                r = client.chat(model=model_name, messages=messages)
                response = r["message"]["content"]
                self.logger.info(
                    "llm_complete",
                    provider="ollama",
                    model=model_name,
                    response_length=len(response),
                )
                return response

            elif model.startswith("gpt"):
                from openai import OpenAI

                r = OpenAI(api_key=settings.OPENAI_API_KEY).chat.completions.create(
                    model=model, messages=messages, max_tokens=1000
                )
                response = r.choices[0].message.content
                self.logger.info(
                    "llm_complete",
                    provider="openai",
                    model=model,
                    response_length=len(response),
                )
                return response

            elif model.startswith("gemini/"):
                import google.generativeai as genai

                model_name = model.replace("gemini/", "")
                genai.configure(api_key=settings.GEMINI_API_KEY)
                r = genai.GenerativeModel(model_name).generate_content(
                    messages[-1]["content"]
                )
                response = r.text
                self.logger.info(
                    "llm_complete",
                    provider="gemini",
                    model=model_name,
                    response_length=len(response),
                )
                return response

            elif model.startswith("anthropic/"):
                from anthropic import Anthropic

                model_name = model.replace("anthropic/", "")
                r = Anthropic(api_key=settings.ANTHROPIC_API_KEY).messages.create(
                    model=model_name,
                    max_tokens=1000,
                    messages=messages,
                )
                response = r.content[0].text
                self.logger.info(
                    "llm_complete",
                    provider="anthropic",
                    model=model_name,
                    response_length=len(response),
                )
                return response

        except LLMClientError:
            raise
        except Exception as exc:
            raise LLMClientError(f"LLM call failed for model '{model}': {exc}") from exc

        raise ValueError(f"Unsupported LLM_MODEL: {model}")
