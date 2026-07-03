from services.embedding import generate_query_embedding
from services.qdrant_service import client
from services.gemini_service import generate_answer

ACTIVE_COLLECTION = None


def set_active_collection(collection_name):
    """
    Store the active Qdrant collection.
    """
    global ACTIVE_COLLECTION
    ACTIVE_COLLECTION = collection_name


def ask_question(question: str):

    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a valid question.",
            "suggestions": []
        }

    user_input = question.lower()

    # -----------------------------
    # Greetings
    # -----------------------------
    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "hola"
    ]

    if any(greet == user_input for greet in greetings):
        return {
            "answer":
                "Hello! 👋\n\n"
                "Welcome to the Document RAG Chatbot.\n\n"
                "Upload a PDF, DOCX, or TXT document and ask me questions about it.",
            "suggestions": []
        }

    # -----------------------------
    # Thank You
    # -----------------------------
    thanks = [
        "thanks",
        "thank you",
        "thankyou",
        "thank u"
    ]

    if any(word == user_input for word in thanks):
        return {
            "answer":
                "You're welcome! 😊\n\nFeel free to ask another question.",
            "suggestions": []
        }

    # -----------------------------
    # Goodbye
    # -----------------------------
    goodbye = [
        "bye",
        "goodbye",
        "see you",
        "exit"
    ]

    if any(word == user_input for word in goodbye):
        return {
            "answer":
                "Goodbye! 👋\n\nHave a wonderful day.",
            "suggestions": []
        }

    # -----------------------------
    # Check Document Upload
    # -----------------------------
    if ACTIVE_COLLECTION is None:
        return {
            "answer": "Please upload a document first.",
            "suggestions": []
        }

    # -----------------------------
    # Get Collection
    # -----------------------------
    try:

        collection = client.get_collection(ACTIVE_COLLECTION)

    except Exception:

        return {
            "answer": "Unable to access the uploaded document.",
            "suggestions": []
        }

    # -----------------------------
    # Generate Query Embedding
    # -----------------------------
    try:

        query_embedding = generate_query_embedding(question)

    except Exception:

        return {
            "answer": "Failed to generate query embedding.",
            "suggestions": []
        }

    # -----------------------------
    # Search ChromaDB
    # -----------------------------
    try:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )

    except Exception:

        return {
            "answer": "Failed to search the document.",
            "suggestions": []
        }

    documents = results.get("documents", [[]])[0]

    if not documents:

        return {
            "answer":
                "The uploaded document does not contain enough information to answer this question.",
            "suggestions": []
        }

    # -----------------------------
    # Build Context
    # -----------------------------
    context = "\n\n".join(documents[:5])

    # -----------------------------
    # Generate Gemini Answer
    # -----------------------------
    try:

        response = generate_answer(
            context,
            question
        )

        return response

    except Exception as e:

        return {
            "answer": f"Failed to generate answer: {str(e)}",
            "suggestions": []
        }