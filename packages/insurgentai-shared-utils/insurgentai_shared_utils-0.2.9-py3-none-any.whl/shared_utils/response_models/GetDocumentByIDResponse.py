from pydantic import BaseModel, Field
from fastapi.responses import FileResponse

class GetDocumentByIDResponse(BaseModel):
    """
    Response model for getting a document by its ID operation.
    """
    metadata: dict = Field(..., description="Metadata associated with the document.")
    content: FileResponse = Field(..., description="The content of the document retrieved from the database.")