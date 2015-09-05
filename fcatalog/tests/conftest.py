import asyncio
import pytest
import os


@pytest.fixture(scope='module')
def asyncio_debug_mode():
    """
    Set debug mode for asyncio
    """
    os.environ['PYTHONASYNCIODEBUG'] = '1'


@pytest.fixture(scope='function')
def tloop(request,asyncio_debug_mode):
    """
    Obtain a test loop. We want each test case to have its own loop.
    """
    # Create a new test loop:
    tloop = asyncio.new_event_loop()
    asyncio.set_event_loop(tloop)

    def teardown():
        # Close the test loop:
        tloop.close()

    request.addfinalizer(teardown)
    return tloop
