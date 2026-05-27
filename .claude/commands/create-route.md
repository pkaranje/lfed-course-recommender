Create the FastAPI route for "$ARGUMENTS" in `app/api/routes/$ARGUMENTS.py`.

Follow CLAUDE.md conventions:
- Routes are thin — validate input, call service, return response. No business logic here.
- Inject service via FastAPI Depends() from app/core/dependencies.py
- Catch domain exceptions from app/domain/ and map to correct HTTP status codes
- Use Pydantic schemas from app/api/schemas/ for request/response
- Add slowapi rate limiter on write endpoints
- Return correct HTTP codes: 200 GET, 201 POST, 422 validation error, 429 rate limit
- No bare except — catch specific domain exceptions only

Read existing routes in app/api/routes/ first to match the pattern exactly.
After creating, show me the file and confirm it is registered in app/main.py.
