import google.generativeai as genai
import re

from config import GOOGLE_API_KEY

# --------------------------------------------------
# Configure Gemini
# --------------------------------------------------

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

generation_config = {
    "temperature": 0.2,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}


def generate_answer(context: str, question: str):

    prompt = f"""
You are an intelligent Document RAG Assistant.

You MUST answer ONLY using the provided document context.

If the answer cannot be found in the document, reply exactly:

The uploaded document does not contain enough information to answer this question.

After answering, generate FOUR follow-up questions that are closely related to BOTH:
1. the current answer
2. the uploaded document

Return your response EXACTLY in this format:

ANSWER:
<your answer>

SUGGESTIONS:
1. Question One
2. Question Two
3. Question Three
4. Question Four

--------------------------------------------------

DOCUMENT

{context}

--------------------------------------------------

QUESTION

{question}

--------------------------------------------------
"""

    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )

    text = response.text.strip()

    answer = ""
    suggestions = []

    if "SUGGESTIONS:" in text:

        parts = text.split("SUGGESTIONS:")

        answer = (
            parts[0]
            .replace("ANSWER:", "")
            .strip()
        )

        suggestion_text = parts[1]

        suggestions = re.findall(
            r"\d+\.\s*(.*)",
            suggestion_text
        )

    else:

        answer = text

    return {
        "answer": answer,
        "suggestions": suggestions
    }