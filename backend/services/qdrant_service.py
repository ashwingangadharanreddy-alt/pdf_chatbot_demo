import os
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import (  # type: ignore
    PointStruct,
    VectorParams,
)

from config import QDRANT_API_KEY, QDRANT_URL


if not QDRANT_URL:
    raise RuntimeError("QDRANT_URL is not configured.")

if not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_API_KEY is not configured.")


client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    prefer_grpc=False,
)


DEFAULT_COLLECTION_NAME = "document_rag_collection"
VECTOR_SIZE = 384


def create_collection(collection_name: str | None = None, vector_size: int | None = None) -> str:
    collection_name = collection_name or DEFAULT_COLLECTION_NAME
    vector_size = vector_size or VECTOR_SIZE

    if collection_name not in [c.name for c in client.get_collections().result.collections]:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance="Cosine"),
        )

    return collection_name


def store_embeddings(collection_name: str, chunks: list[str], embeddings: list[list[float]]):
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have the same length.")

    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=i,
                vector=embedding,
                payload={"text": chunk},
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
    )


def search_collection(collection_name: str, query_embedding: list[float], top_k: int = 5) -> list[str]:
    response = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        with_payload=["text"],
        top=top_k,
    )

    results = []
    for hit in response:
        payload = hit.payload or {}
        if isinstance(payload, dict) and "text" in payload:
            results.append(payload["text"])

    return results
