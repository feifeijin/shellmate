"""
CLI runner for local testing without Telegram.
Usage: python -m shellmate.interfaces.cli.runner "your task description"
"""
import asyncio
import sys
import uuid
from shellmate.core.models import TaskContext
from shellmate.runtime.dispatcher import Dispatcher


async def run_once(dispatcher: Dispatcher, raw_input: str, user_id: str = "cli-user") -> None:
    context = TaskContext(
        task_id=str(uuid.uuid4())[:8],
        raw_input=raw_input,
        user_id=user_id,
    )
    print(f"[shellmate] dispatching task {context.task_id!r}: {raw_input!r}")
    result = await dispatcher.dispatch(context)
    print(f"[shellmate] result:\n{result}")


def main(dispatcher: Dispatcher) -> None:
    if len(sys.argv) < 2:
        print("Usage: runner.py <task description>")
        sys.exit(1)
    raw = " ".join(sys.argv[1:])
    asyncio.run(run_once(dispatcher, raw))
