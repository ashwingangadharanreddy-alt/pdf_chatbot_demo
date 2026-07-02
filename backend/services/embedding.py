from sentence_transformers import SentenceTransformer

# Load the model only once when the application starts
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks: list[str]):
    """
    Convert text chunks into embeddings.
    """
    embeddings = embedding_model.encode(chunks).tolist()

    return embeddings


def generate_query_embedding(query: str):
    """
    Convert a user question into an embedding.
    """
    return embedding_model.encode(query).tolist()