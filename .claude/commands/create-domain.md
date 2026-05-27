Create the domain module for "$ARGUMENTS" in `app/domain/$ARGUMENTS.py`.

Follow CLAUDE.md conventions:
- Pure Python only — no I/O, no DB, no HTTP, no SDK imports
- Define all enums, constants, validation functions, and domain exceptions for this entity
- Validation functions raise domain exceptions, never return booleans
- Re-export everything via `app/domain/__init__.py`
- Add type hints on all functions
- Add docstrings: one-line summary + Args + Returns

After creating, show me the file and confirm `app/domain/__init__.py` is updated.
