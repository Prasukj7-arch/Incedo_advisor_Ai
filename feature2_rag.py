import requests
import json
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

# EC2 IP loaded from .env
EC2_IP = os.getenv("EC2_RAG_IP", "")
RAG_SERVER_URL = f"http://{EC2_IP}:8000" if EC2_IP else ""


def search_research_reports(question: str, session_id: str = "default"):
    """
    Connects to the RAG server on EC2 to search research documents.
    """
    try:
        payload = {
            "question": question,
            "session_id": session_id
        }
        response = requests.post(
            f"{RAG_SERVER_URL}/research",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Server returned error: {response.status_code}",
                "detail": response.text
            }
    except Exception as e:
        return {
            "error": "Could not connect to RAG server",
            "detail": str(e)
        }


def get_rag_health():
    """Checks if the RAG server is alive."""
    try:
        response = requests.get(f"{RAG_SERVER_URL}/health", timeout=5)
        return response.json()
    except Exception:
        return {"status": "offline"}


if __name__ == "__main__":
    print(f"RAG Server URL: {RAG_SERVER_URL}")
    print("Checking RAG Server health...")
    print(get_rag_health())

    print("\nTesting search query...")
    test_query = "What are the top picks in semiconductor sector?"
    result = search_research_reports(test_query)
    print(json.dumps(result, indent=2))
