from typing import Any, Coroutine

from galileo_core.helpers.event_loop_thread_pool import EventLoopThreadPool

_thread_pool = EventLoopThreadPool(name="galileo_async_run")


def async_run(coroutine: Coroutine) -> Any:
    """
    Run an async coroutine synchronously.

    This function is useful for running async code in a synchronous context. This will
    ensure that the async code is run in a separate thread and the result is returned
    to the caller.

    Parameters
    ----------
    coroutine : Coroutine
        The coroutine to run.

    Returns
    -------
    Any
        The result of the coroutine.
    """
    return _thread_pool.submit(coroutine)
