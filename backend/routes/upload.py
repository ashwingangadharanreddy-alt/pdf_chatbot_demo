from fastapi import APIRouter, UploadFile, File, HTTPException

from services.pdf_reader_stream import extract_text_bytes
from services.text_splitter import split_text
from services.embedding import generate_embeddings
from services.qdrant_service import create_collection, store_embeddings
from services.rag_service import set_active_collection

router = APIRouter(tags=["Upload"])

# ----------------------------------------
# Configuration
# ----------------------------------------
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

    try:
        text = extract_text_bytes(file.filename, contents)

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

        # Create Qdrant collection
        collection_name = create_collection()

        # Store vectors
        store_embeddings(
            collection_name,
            chunks,
            embeddings
        )

        # Set active collection
        set_active_collection(collection_name)

        return {
            "success": True,
            "message": "Document uploaded and indexed successfully.",
            "collection": collection_name,
            "chunks": len(chunks),
            "characters": len(text)
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )