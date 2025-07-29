from pydantic import BaseModel, Field


class GetFileContentInput(BaseModel):
    """Input model for file content retrieval operations."""

    file_name: str = Field(description="Name of the file to retrieve content from")


class GetFileContentOutput(BaseModel):
    """Output model for file content retrieval operations."""

    content: str | bytes = Field(description="File content")


class GetFileSearchInput(BaseModel):
    """Input model for file search operations."""

    file_name: str = Field(description="Name of the file to search in")
    query: str = Field(description="Search query to find relevant content")
    num_results: int = Field(description="Number of results to return", default=5)
