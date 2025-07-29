from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.perplexity_models import (
    ChatInput,
    ChatMessage,
    ChatOptions,
    ChatOutput,
)
from ..models.tools.workflow_models import ToolStreamResponse

__all__ = ["ChatInput", "ChatMessage", "ChatOptions", "ChatOutput", "chat", "chat_stream"]


def chat(
    *,
    input: str | list[dict[str, Any]] | Any = DEFAULT,
    chat_options: ChatOptions = DEFAULT,
    timeout: int = DEFAULT,
) -> ChatOutput:
    """
    A tool for generating chat completions using Perplexity AI's API.

    Input should be a valid ChatInput.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ChatInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="perplexity", name="chat", input=input_model.model_dump()
    )
    return ChatOutput.model_validate(output_model)


def chat_stream(
    *,
    input: str | list[dict[str, Any]] | Any = DEFAULT,
    chat_options: ChatOptions = DEFAULT,
    timeout: int = DEFAULT,
) -> ToolStreamResponse:
    """
    A streaming version of the chat tool that returns a StreamingResponse.

    This function is designed for use with server-sent events (SSE) and frameworks
    like FastAPI. The returned StreamingResponse can be used directly in web endpoints.

    Args:
        input: ChatInput containing the message and options

    Returns:
        StreamingResponse: StreamingResponse object containing the SSE data chunks

    Example:
        ```python
        # Use directly in FastAPI endpoint
        @app.get("/stream")
        def stream_endpoint():
            return perplexity.chat_stream(chat_input)

        # Or return the response directly
        streaming_response = perplexity.chat_stream(chat_input)
        ```
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ChatInput.model_validate(kwargs)

    client = A79Client()
    stream_id = client.execute_tool_streaming(
        package="perplexity", name="chat_stream", input=input_model.model_dump()
    )
    return ToolStreamResponse(
        stream_id=stream_id, tool_name="chat_stream", package_name="perplexity"
    )
