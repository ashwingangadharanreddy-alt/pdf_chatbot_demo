from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from datetime import datetime

from services.pdf_reader import extract_text
from services.text_splitter import split_text
from services.embedding import generate_embeddings
from services.chroma_service import create_collection, store_embeddings
from services.rag_service import set_active_collection

router = APIRouter(tags=["Upload"])

# ----------------------------------------
# Configuration
# ----------------------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

# ----------------------------------------
# Upload Route
# ----------------------------------------
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    extension = file.filename.split(".")[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT and DOCX files are allowed."
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 20 MB."
        )

    # Reset pointer after reading
    file.file.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{timestamp}_{file.filename}"

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    try:

        # Save uploaded file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        text = extract_text(filepath)

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="The uploaded document contains no readable text."
            )

        # Split into chunks
        chunks = split_text(text)

        if len(chunks) == 0:
            raise HTTPException(
                status_code=400,
                detail="No text chunks were created."
            )

        # Generate embeddings
        embeddings = generate_embeddings(chunks)

        # Create Chroma collection
        collection = create_collection()

        # Store vectors
        store_embeddings(
            collection,
            chunks,
            embeddings
        )

        # Set active collection
        set_active_collection(collection.name)

        return {
            "success": True,
            "message": "Document uploaded and indexed successfully.",
            "filename": filename,
            "collection": collection.name,
            "chunks": len(chunks),
            "characters": len(text)
        }

    except HTTPException:
        raise

    except Exception as e:

        if os.path.exists(filepath):
            os.remove(filepath)

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )