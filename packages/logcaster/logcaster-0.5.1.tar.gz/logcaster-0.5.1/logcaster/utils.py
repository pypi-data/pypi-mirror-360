import asyncio
import threading
from asyncio import Task
from typing import Any, Callable, Coroutine


def emit_async(
    coroutine: Coroutine[Any, Any, Any],
    on_done: Callable[[Task[Any]], object] | None = None,
) -> None:
    """run the given coroutine inside a already running event loop or
    creates a new one that runs inside a threading

    Args:
        coroutine (Coroutine): the coroutine to be executed
        on_done (Optional[Callable], optional): a function to be executed when
            the task to be done. Defaults to None.
    """
    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(coroutine)
        if callable(on_done):
            task.add_done_callback(on_done)
    except RuntimeError:

        def run() -> None:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(coroutine)
            new_loop.close()

        threading.Thread(target=run, daemon=True).start()
