import asyncio

# Timeout in seconds for an asynchronous test:
ASYNC_TEST_TIMEOUT = 1

class ExceptAsyncTestTimeout(Exception): pass

def run_timeout(cor,loop,timeout=ASYNC_TEST_TIMEOUT):
    """
    Run a given coroutine with timeout.
    """
    task_with_timeout = asyncio.wait_for(cor,timeout,loop=loop)
    try:
        return loop.run_until_complete(task_with_timeout)
    except asyncio.futures.TimeoutError:
        # Timeout:
        raise ExceptAsyncTestTimeout()


