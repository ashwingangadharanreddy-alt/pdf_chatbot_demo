from services.embedding import generate_query_embedding
from services.chroma_service import client
from services.gemini_service import generate_answer

ACTIVE_COLLECTION = None


def set_active_collection(collection_name):
    global ACTIVE_COLLECTION
    ACTIVE_COLLECTION = collection_name


def ask_question(question: str):

    question = question.strip()

    if not question:
        return "Please enter a valid question."

    user_input = question.lower()

    # -------------------------------------
    # Greetings
    # -------------------------------------
    greetings = (
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "hola",
        "hi there",
        "hello there"
    )

    if user_input.startswith(greetings):
        return (
            "Hello! 👋\n\n"
            "Welcome to the **Document RAG Chatbot**.\n\n"
            "📄 Upload a PDF, DOCX or TXT file and I'll answer questions using only the uploaded document."
        )

    # -------------------------------------
    # How are you
    # -------------------------------------
    if "how are you" in user_input:
        return (
            "I'm doing great! 😊\n\n"
            "I'm ready to help you understand your uploaded documents."
        )

    # -------------------------------------
    # Who are you
    # -------------------------------------
    if (
        "who are you" in user_input
        or "what are you" in user_input
    ):
        return (
            "I'm a **Document Retrieval-Augmented Generation (RAG) Chatbot**.\n\n"
            "I can answer questions based only on the document you upload."
        )

    # -------------------------------------
    # Help
    # -------------------------------------
    if user_input in ["help", "commands"]:

        return (
            "**I can help you with:**\n\n"
            "• Greeting 😊\n"
            "• Answering questions from your uploaded PDF\n"
            "• Summarizing the document\n"
            "• Explaining document content\n"
            "• Finding information from the document\n\n"
            "Upload a document and start asking questions!"
        )

    # -------------------------------------
    # Thanks
    # -------------------------------------
    thanks = (
        "thanks",
        "thank you",
        "thankyou",
        "thank u"
    )

    if user_input.startswith(thanks):
        return (
            "You're welcome! 😊\n\n"
            "Feel free to ask another question."
        )

    # -------------------------------------
    # Goodbye
    # -------------------------------------
    goodbye = (
        "bye",
        "goodbye",
        "see you",
        "exit"
    )

    if user_input.startswith(goodbye):
        return (
            "Goodbye! 👋\n\n"
            "Thank you for using the Document RAG Chatbot.\n"
            "Have a wonderful day!"
        )

    # -------------------------------------
    # Check document
    # -------------------------------------
    if ACTIVE_COLLECTION is None:
        return (
            "📄 Please upload a document first.\n\n"
            "After uploading, I'll answer questions based on that document."
        )

    # -------------------------------------
    # Load collection
    # -------------------------------------
    try:
        collection = client.get_collection(ACTIVE_COLLECTION)

    except Exception:
        return "Unable to access the uploaded document."

    # -------------------------------------
    # Generate embedding
    # -------------------------------------
    try:
        query_embedding = generate_query_embedding(question)

    except Exception:
        return "Failed to generate query embedding."

    # -------------------------------------
    # Retrieve relevant chunks
    # -------------------------------------
    try:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )

    except Exception:

        return "Failed to search the document."

    documents = results.get("documents", [[]])[0]

    if not documents:

        return (
            "The uploaded document does not contain enough information to answer this question."
        )

    context = "\n\n".join(documents)

    # -------------------------------------
    # Gemini
    # -------------------------------------
    try:

        answer = generate_answer(
            context=context,
            question=question
        )

    except Exception as e:

        return f"Failed to generate answer.\n\n{e}"

    return answer