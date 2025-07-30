from typing import Any

from pydantic import BaseModel

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.llm_models import (
    ChatInput,
    ChatOutput,
    Enum,
    ErrorHandling,
    InferenceMode,
    LLMUsageData,
)
from ..models.tools.workflow_models import ToolStreamResponse

__all__ = [
    "ChatInput",
    "ChatOutput",
    "Enum",
    "ErrorHandling",
    "InferenceMode",
    "LLMUsageData",
    "chat",
    "chat_stream",
]


def chat(
    *,
    schema: dict[str, Any] | type[BaseModel] | None = DEFAULT,
    model: str = DEFAULT,
    prompt_str: str | None = DEFAULT,
    temperature: float = DEFAULT,
    stop: list[str] | None = DEFAULT,
    error_handling: ErrorHandling = DEFAULT,
    top_p: float | None = DEFAULT,
    seed: int | None = DEFAULT,
    presence_penalty: float | None = DEFAULT,
    frequency_penalty: float | None = DEFAULT,
    tool_choice: str | None = DEFAULT,
    inference_mode: InferenceMode = DEFAULT,
    output_schema: dict[str, Any] | type[BaseModel] | None = DEFAULT,
    stream: bool = DEFAULT,
) -> ChatOutput:
    """
    AI powered chat
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ChatInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="llm", name="chat", input=input_model.model_dump()
    )
    return ChatOutput.model_validate(output_model)


def chat_stream(
    *,
    schema: dict[str, Any] | type[BaseModel] | None = DEFAULT,
    model: str = DEFAULT,
    prompt_str: str | None = DEFAULT,
    temperature: float = DEFAULT,
    stop: list[str] | None = DEFAULT,
    error_handling: ErrorHandling = DEFAULT,
    top_p: float | None = DEFAULT,
    seed: int | None = DEFAULT,
    presence_penalty: float | None = DEFAULT,
    frequency_penalty: float | None = DEFAULT,
    tool_choice: str | None = DEFAULT,
    inference_mode: InferenceMode = DEFAULT,
    output_schema: dict[str, Any] | type[BaseModel] | None = DEFAULT,
    stream: bool = DEFAULT,
) -> ToolStreamResponse:
    """
    A streaming version of the chat tool that returns a StreamingResponse.

    This function is designed for use with server-sent events (SSE) and frameworks
    like FastAPI. The returned StreamingResponse can be used directly in web endpoints.

    Args:
        input: ChatInput containing the prompt and options

    Returns:
        StreamingResponse: StreamingResponse object containing the SSE data chunks

    Example:
        ```python
        # Use directly in FastAPI endpoint
        @app.get("/stream")
        def stream_endpoint():
            return llm.chat_stream(chat_input)

        # Or return the response directly
        streaming_response = llm.chat_stream(chat_input)
        ```
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ChatInput.model_validate(kwargs)

    client = A79Client()
    stream_id = client.execute_tool_streaming(
        package="llm", name="chat_stream", input=input_model.model_dump()
    )
    return ToolStreamResponse(
        stream_id=stream_id, tool_name="chat_stream", package_name="llm"
    )
