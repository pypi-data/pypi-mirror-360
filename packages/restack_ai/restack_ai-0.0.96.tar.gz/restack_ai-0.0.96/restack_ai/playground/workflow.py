# ruff: noqa: N815
# PlaygroundRun needs consistent typing between frontend, server, typescript and python library

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from temporalio import workflow


@dataclass
class PlaygroundInput:
    functionName: str
    taskQueue: str
    input: Any | None = None


@workflow.defn(name="playgroundRun", sandboxed=True)
class PlaygroundRun:
    @workflow.run
    async def run(self, params: PlaygroundInput) -> Any:
        engine_id = workflow.memo_value("engineId", "local")
        return await workflow.execute_activity(
            activity=params.functionName,
            task_queue=f"{engine_id}-{params.taskQueue}",
            args=[params.input],
            start_to_close_timeout=timedelta(seconds=120),
        )


@workflow.defn()
class FunctionsOnly:
    """FunctionsOnly workflow that prevents TaskLocals issues for functions-only services.

    This workflow should never actually be executed - it exists only to
    ensure that workers have at least one workflow registered.
    """

    @workflow.run
    async def run(self) -> str:
        # This should never be called
        return "functions_only_workflow_should_not_be_called"
