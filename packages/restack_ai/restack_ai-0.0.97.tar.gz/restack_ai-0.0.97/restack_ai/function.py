from typing import Any

import websockets
from temporalio import activity
from temporalio.exceptions import ApplicationError

from .observability import log_with_context, logger

activity.logger.logger = logger


class ActivityLogger:
    """Enables consistent formatting for function logs."""

    def __init__(self) -> None:
        self._logger = activity.logger

    def _log(
        self,
        level: str,
        message: str,
        **kwargs: Any,
    ) -> None:
        try:
            activity.info()
            getattr(self._logger, level)(
                message,
                extra={
                    "extra_fields": {
                        **kwargs,
                        "client_log": True,
                    },
                },
            )
        except RuntimeError:
            log_with_context(level.upper(), message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("critical", message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log an exception with traceback (equivalent to `logging.exception`)."""
        kwargs["exc_info"] = True
        self._log("exception", message, **kwargs)


log = ActivityLogger()

function_info = activity.info
heartbeat = activity.heartbeat
function = activity


class NonRetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=True)


class RetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=False)


__all__ = [
    "NonRetryableError",
    "RetryableError",
    "function_info",
    "heartbeat",
    "log",
    "mcp_progress",
]


def mcp_progress(
    progress: float,
    total: float | None = None,
    message: str | None = None,
) -> bool:
    """Send an MCP-compliant progress information.

    Example:

    .. code-block:: python

        # Basic progress
        mcp_progress(progress=25, total=100, message="Loading data")

        # Progress update
        mcp_progress(progress=50, total=100, message="Processing data")

    Args:
        progress (float): Current progress value (must increase with each call)
        total (float, optional): Total progress value if known
        message (str, optional): Human-readable progress message

    Returns:
        bool: True if the progress information was sent successfully, False otherwise

    """
    try:
        info = activity.info()

        mcp_data = {
            "_mcp_progress": True,
            "progress": float(progress),
            "activity_id": info.activity_id,
            "activity_type": info.activity_type,
        }

        # Add optional fields
        if total is not None:
            mcp_data["total"] = float(total)

        if message is not None:
            mcp_data["message"] = str(message)

        heartbeat(mcp_data)

        log.debug(
            "MCP progress sent: progress=%s, total=%s, message=%s",
            progress,
            total,
            message,
        )

    except Exception:
        log.exception("Error sending MCP progress")
        return False
    else:
        return True


def current_workflow() -> Any:
    return activity.Context.current().info


async def stream_to_websocket(
    api_address: str | None = None,
    data: Any = None,
) -> Any:
    """Stream data to Restack Engine WebSocket API endpoint.

    Args:
        api_address (str): The address of the Restack Engine API.
        data (Any): The streamed data from an OpenAI-compatible API or a JSON dict.

    Returns:
        str: The final combined response as a string.

    """
    if api_address is None:
        api_address = "localhost:9233"

    info = {
        "activityId": activity.info().activity_id,
        "workflowId": activity.info().workflow_id,
        "runId": activity.info().workflow_run_id,
        "activityType": activity.info().activity_type,
        "taskQueue": activity.info().task_queue,
    }

    protocol = (
        "ws" if api_address.startswith("localhost") else "wss"
    )
    websocket_url = f"{protocol}://{api_address}/stream/ws/agent?agentId={info['workflowId']}&runId={info['runId']}"

    try:
        async with websockets.connect(websocket_url) as websocket:
            try:
                heartbeat(info)

                collected_messages = []

                # Check if module name is openai (no need to import openai package in this library)
                if data.__class__.__module__.startswith("openai"):
                    for chunk in data:
                        raw_chunk_json = chunk.model_dump_json()
                        heartbeat(raw_chunk_json)
                        await websocket.send(
                            message=raw_chunk_json,
                        )
                        if (
                            chunk.choices
                            and chunk.choices[0].delta
                        ):
                            content = chunk.choices[
                                0
                            ].delta.content
                        else:
                            content = None
                        if content:
                            collected_messages.append(content)
            finally:
                # Ensure the WebSocket connection is closed
                await websocket.send(message="[DONE]")
                await websocket.close()

            return "".join(collected_messages)
    except Exception as e:
        error_message = (
            f"Error with restack stream to websocket: {e}"
        )
        log.exception(error_message)
        raise ApplicationError(error_message) from e
