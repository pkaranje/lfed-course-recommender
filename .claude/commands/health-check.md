Run a full health check across all services and confirm the stack is ready.

Check each service in order:
1. Ollama: `curl -s http://localhost:11434/api/tags | python3 -m json.tool` — confirm mistral and nomic-embed-text are listed
2. ChromaDB: `curl -s http://localhost:8080/api/v1/heartbeat` — should return {"nanosecond heartbeat": ...}
3. Backend: `curl -s http://localhost:8000/api/v1/health` — should return {"status": "ok"}
4. Frontend: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8501` — should return 200

Show me the output of each check.
If any service is down, show the relevant docker-compose logs and suggest the fix.
Only mark the stack as ready when all 4 pass.
