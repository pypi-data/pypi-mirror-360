from pydantic import BaseModel, Field

class GetDocumentByIDResponse(BaseModel):
    """
    Response model for getting a document by its ID operation.
    """
    metadata: dict = Field(..., description="Metadata associated with the document.")
    download_url: str = Field(..., description="The pre-signed s3 url to download the content.")