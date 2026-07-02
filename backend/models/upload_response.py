from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    collection_id: str
    filename: str