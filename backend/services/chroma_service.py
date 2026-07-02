import uuid
import chromadb

client = chromadb.PersistentClient(path="chroma_db")


def create_collection():

    collection_name = f"document_{uuid.uuid4().hex}"

    collection = client.create_collection(
        name=collection_name
    )

    return collection


def store_embeddings(collection, chunks, embeddings):

    ids = [str(i) for i in range(len(chunks))]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )


def search_documents(collection_name, query_embedding, top_k=5):

    collection = client.get_collection(collection_name)

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )