import asyncio
from fcatalog.proto.frame_endpoint import FrameEndpoint

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


class MockFrameEndpoint(FrameEndpoint):
    def __init__(self,frame_reader,frame_writer,uid=None,log_list=None):
        # Keep frame reader and writer:
        self._frame_reader = frame_reader
        self._frame_writer = frame_writer

        # Keep unique id: (For debugging)
        self._uid = uid
        # Keep log list: (For debugging)
        self._log_list = log_list

    @asyncio.coroutine
    def send(self,data_frame:bytes):
        """Send a frame"""
        yield from self._frame_writer(data_frame)

    @asyncio.coroutine
    def recv(self) -> bytes:
        """Receive a frame"""
        return (yield from self._frame_reader())

    @asyncio.coroutine
    def close(self):
        """Close the connection"""
        yield from self._frame_writer(None)
        if self._log_list is not None:
            # Write None. The other side will interpret this as closing the
            # connection:
            # Append 'stop' callback to the log list:
            self._log_list.append(('stop',self._uid))
