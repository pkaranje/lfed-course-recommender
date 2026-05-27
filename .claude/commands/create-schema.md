Create the Pydantic schemas for "$ARGUMENTS" in `app/api/schemas/$ARGUMENTS.py`.

Follow CLAUDE.md conventions:
- Use Pydantic v2 with model_config = ConfigDict(...)
- Separate Request and Response models — never reuse the same model for both
- Use strict types — no bare str where an enum applies
- Add field-level validation with @field_validator where needed
- Re-export via app/api/schemas/__init__.py

Read existing schemas in app/api/schemas/ first to match the pattern exactly.
After creating, show me the file and confirm __init__.py is updated.
