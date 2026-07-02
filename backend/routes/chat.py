from fastapi import APIRouter, HTTPException
from datetime import datetime

from models.chat_request import ChatRequest
from services.rag_service import ask_question

router = APIRouter(tags=["Chat"])


@router.post("/chat")
def chat(request: ChatRequest):

    # Remove unnecessary spaces
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    start_time = datetime.now()

    try:

        answer = ask_question(question)

        processing_time = (
            datetime.now() - start_time
        ).total_seconds()

        return {
            "success": True,
            "question": question,
            "answer": answer,
            "processing_time": round(processing_time, 2)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )