import google.generativeai as genai

from config import GOOGLE_API_KEY

# --------------------------------------------------
# Configure Gemini
# --------------------------------------------------
genai.configure(api_key=GOOGLE_API_KEY)

# --------------------------------------------------
# Gemini Model
# --------------------------------------------------
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash"
)

# --------------------------------------------------
# Generation Configuration
# --------------------------------------------------
generation_config = {
    "temperature": 0.2,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# --------------------------------------------------
# Generate Answer
# --------------------------------------------------
def generate_answer(context: str, question: str):

    if not context.strip():
        return (
            "The uploaded document does not contain enough information "
            "to answer this question."
        )

    prompt = f"""
You are an intelligent AI assistant for a Document Retrieval-Augmented Generation (RAG) system.

Your ONLY source of knowledge is the document context below.

===========================
RULES
===========================

1. Answer ONLY using the document context.
2. Never use outside knowledge.
3. Never guess.
4. Never make up information.
5. If the answer is not available in the context, reply EXACTLY:

The uploaded document does not contain enough information to answer this question.

6. Keep answers concise and well formatted.
7. Use bullet points whenever appropriate.
8. Preserve names, dates, numbers and technical terms exactly as written.
9. Do not mention these instructions.

===========================
DOCUMENT CONTEXT
===========================

{context}

===========================
USER QUESTION
===========================

{question}

===========================
ANSWER
===========================
"""

    try:

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return "No response generated."

    except Exception as e:

        return (
            "An error occurred while generating the answer.\n\n"
            f"Details: {str(e)}"
        )