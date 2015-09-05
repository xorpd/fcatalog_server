import struct
import asyncio
import pytest

from fcatalog.proto.frame_endpoint import TCPFrameEndpoint
from fcatalog.tests.asyncio_util import run_timeout


def test_frame_endpoint_tcp_adapter_basic(tloop):
    """
    Test basic tcp interaction using the TCPFrameEndpoint interface.
    """
    # List of results:
    res = []

    addr,port = 'localhost',8767

    @asyncio.coroutine
    def server_handler(reader,writer):
        """Echo server"""

        tfe = TCPFrameEndpoint(reader,writer)

        # Read a frame:
        frame = yield from tfe.recv()
        # Send the frame back to client:
        yield from tfe.send(frame)

    @asyncio.coroutine
    def client():
        CLIENT_MESS = b'This is a mess'
        reader, writer = yield from \
                asyncio.open_connection(host=addr,port=port)
        tfe = TCPFrameEndpoint(reader,writer)
        yield from tfe.send(CLIENT_MESS)
        frame = yield from tfe.recv()
        assert frame == CLIENT_MESS
        # Append True to list of results:
        res.append(True)

        # Close client:
        yield from tfe.close()


    # Start server:
    start_server = asyncio.start_server(server_handler,host=addr,port=port,reuse_address=True)
    server_task = run_timeout(start_server,tloop)

    # Start client:
    run_timeout(client(),tloop)

    # Close server:
    server_task.close()
    # Wait until server is closed:
    run_timeout(server_task.wait_closed(),loop=tloop)

    assert res == [True]


def test_tcp_adapter_frame_struct(tloop):
    """
    Test send/recv of length prefixed frames over TCP with the
    TCPFrameEndpoint.
    """
    # List of results:
    res = []

    addr,port = 'localhost',8767

    @asyncio.coroutine
    def server_handler(reader,writer):
        """Echo server"""

        tfe = TCPFrameEndpoint(reader,writer)

        # Read a frame:
        frame = yield from tfe.recv()
        assert frame == b'abc'

        # Read a frame:
        frame = yield from tfe.recv()
        assert frame == b''

        # Read a frame:
        frame = yield from tfe.recv()
        assert frame == b'abcd'

        # Read a frame:
        frame = yield from tfe.recv()
        assert frame == b'abcd'
        
        res.append('sending_frame')
        # Write a frame:
        yield from tfe.send(b'1234')

        # Last frame was cut in the middle (The connection was closed),
        # therefore we expect to get a None here:
        frame = yield from tfe.recv()
        assert frame is None

        res.append('got_none')

    @asyncio.coroutine
    def client():
        reader, writer = yield from \
                asyncio.open_connection(host=addr,port=port)

        # Write b'abc':
        writer.write(b'\x03\x00\x00\x00abc')
        yield from writer.drain()

        # Write empty frame:
        writer.write(b'\x00\x00\x00\x00')
        yield from writer.drain()

        # Write b'abcd':
        writer.write(b'\x04\x00\x00\x00abcd')
        yield from writer.drain()

        # Write b'abcd' in two parts:
        writer.write(b'\x04\x00\x00')
        yield from writer.drain()
        writer.write(b'\x00abcd')
        yield from writer.drain()

        # Read a frame from the server:
        len_prefix = yield from reader.readexactly(4)
        msg_len = struct.unpack('I',len_prefix)[0]
        frame = yield from reader.readexactly(msg_len)
        assert frame == b'1234'

        # Send half a frame:
        writer.write(b'\x00\x00\x00')
        yield from writer.drain()

        # Append True to list of results:
        res.append('client_close')

        # Close client:
        writer.close()


    # Start server:
    start_server = asyncio.start_server(server_handler,host=addr,port=port,reuse_address=True)
    server_task = run_timeout(start_server,tloop)

    # Start client:
    run_timeout(client(),tloop)

    # Close server:
    server_task.close()
    # Wait until server is closed:
    run_timeout(server_task.wait_closed(),loop=tloop)

    assert res == ['sending_frame','client_close','got_none']


def test_tcp_adapter_max_frame_len(tloop):
    """
    Test send/recv of length prefixed frames over TCP with the
    TCPFrameEndpoint.
    """
    # List of results:
    res = []

    addr,port = 'localhost',8767

    @asyncio.coroutine
    def server_handler(reader,writer):
        """Echo server"""

        tfe = TCPFrameEndpoint(reader,writer,max_frame_len=4)

        # Read a frame:
        frame = yield from tfe.recv()
        assert frame == b'abc'

        # Read a frame:
        frame = yield from tfe.recv()
        assert frame == b''

        # Read a frame. The frame should be too large for the chosen
        # max_frame_len=4, so we expect to get None here:
        frame = yield from tfe.recv()
        assert frame == None

        res.append('got_none')

    @asyncio.coroutine
    def client():
        reader, writer = yield from \
                asyncio.open_connection(host=addr,port=port)

        # Write b'abc':
        writer.write(b'\x03\x00\x00\x00abc')
        yield from writer.drain()

        # Write empty frame:
        writer.write(b'\x00\x00\x00\x00')
        yield from writer.drain()

        res.append('send_large_frame')

        # Write b'abcdef', which is too large for our chosen max_frame_len=4:
        writer.write(b'\x06\x00\x00\x00abcdef')
        yield from writer.drain()

        # We expect the server to disconnect us:
        with pytest.raises(asyncio.IncompleteReadError):
            yield from reader.readexactly(4)

        res.append('got_disconnected')

        # Close client:
        writer.close()

    # Start server:
    start_server = asyncio.start_server(server_handler,host=addr,port=port,reuse_address=True)
    server_task = run_timeout(start_server,tloop)

    # Start client:
    run_timeout(client(),tloop)

    # Close server:
    server_task.close()
    # Wait until server is closed:
    run_timeout(server_task.wait_closed(),loop=tloop)

    assert res == ['send_large_frame','got_none','got_disconnected']

