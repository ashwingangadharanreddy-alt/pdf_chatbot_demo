import requests

from config import HUGGINGFACE_API_TOKEN

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_URL = (
    f"https://api-inference.huggingface.co/embeddings/{EMBEDDING_MODEL}"
)


def _call_huggingface_embeddings(inputs):
    if not HUGGINGFACE_API_TOKEN:
        raise RuntimeError("HUGGINGFACE_API_TOKEN is not configured.")

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        EMBEDDING_URL,
        headers=headers,
        json={"inputs": inputs},
        timeout=60
    )
    response.raise_for_status()

    result = response.json()

    if isinstance(result, dict) and result.get("error"):
        raise RuntimeError(result["error"])

    return result


def generate_embeddings(chunks: list[str]):
    """
    Convert text chunks into embeddings.
    """
    embeddings = _call_huggingface_embeddings(chunks)

    if not isinstance(embeddings, list):
        raise RuntimeError("Unexpected embeddings response from Hugging Face.")

    return embeddings


def generate_query_embedding(query: str):
    """
    Convert a user question into an embedding.
    """
    embeddings = _call_huggingface_embeddings(query)

    if isinstance(embeddings, list) and len(embeddings) > 0:
        return embeddings[0]

    return embeddings