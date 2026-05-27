Create tests for "$ARGUMENTS" in `tests/test_$ARGUMENTS.py`.

Follow CLAUDE.md conventions:
- Use pytest with fixtures from tests/conftest.py
- Mock all external calls — ollama, openai, google, anthropic SDKs and ChromaDB
- Never hit real APIs in tests — all SDK calls must be mocked
- Test the happy path + at least 2 edge cases + at least 1 domain exception case
- Use descriptive test names: test_<what>_<when>_<expected>
- No hardcoded secrets or API keys anywhere in test files

Read conftest.py first to use existing fixtures.
After creating, run `make test` and show me the output.
