Run the full ingestion pipeline and verify the ChromaDB collection is populated.

Steps:
1. Run `make ingest` and show me the output
2. Verify the ChromaDB collection "lfed_courses" exists and has documents:
   - Open a Python shell and run: `import chromadb; c = chromadb.HttpClient(host="localhost", port=8080); print(c.get_collection("lfed_courses").count())`
3. Run a test similarity query to confirm retrieval works:
   - Query: "I want to learn Kubernetes from scratch"
   - Show me the top 3 results with titles and URLs
4. If count is 0 or query returns no results, run `make ingest-force` and repeat

Do not proceed to the next step until count > 0 and query returns relevant results.
