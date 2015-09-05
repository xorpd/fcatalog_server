import struct
import asyncio

# Generic class for FrameEndpoint.
# A method to send frames over a streaming protocol.

class FrameEndpoint:
    @asyncio.coroutine
    def send(self,data_frame:bytes):
        """Send a frame"""
        raise NotImplementedError()

    @asyncio.coroutine
    def recv(self):
        """Receive a frame"""
        raise NotImplementedError()

    @asyncio.coroutine
    def close(self):
        """Close the connection"""
        raise NotImplementedError()


################################################
################################################


# Default Maximum length for a string being sent: 1 mb.
MAX_FRAME_LEN = 2**20

# Amount of bytes of length prefix:
SIZE_PREFIX_LEN = 4

class TCPFrameEndpoint(FrameEndpoint):
    def __init__(self,reader,writer,max_frame_len=MAX_FRAME_LEN):
        # Max length of one frame:
        self._max_frame_len = max_frame_len

        # Keep reader and writer:
        # Those are asyncio TCP Stream Reader and Writer.
        self._reader = reader
        self._writer = writer

        # Set connection state to be open:
        self._is_open = True


    @asyncio.coroutine
    def send(self,data_frame:bytes):
        """
        Send a frame
        (Send data as a length prefixed frame)
        """
        # Encode the length of the data as an unsigned int (4 bytes):
        blen = struct.pack('I',len(data_frame))
        # Write the length prefix and the data:
        self._writer.write(blen + data_frame)
        # Try to flush underlying buffer:
        # See https://docs.python.org/3/library/asyncio-stream.html#asyncio.StreamWriter.drain
        yield from self._writer.drain()


    @asyncio.coroutine
    def recv(self):
        """
        Receive a frame:
        Receive prefixed string data.
        return value of None means that the remote host has closed the
        connection (Or some read error has occured).
        """

        try:
            # Read the length prefix (4 bytes):
            blen = yield from self._reader.readexactly(SIZE_PREFIX_LEN)
            # Unpack 4 bytes into an integer:
            len_data = struct.unpack('I',blen)[0]

            # If the message length is too big, we close the connection.
            if len_data > self._max_frame_len:
                yield from self.close()
                return None

            # Read the message itself (We already know the length):
            # Will read exactly len_data:
            bmsg = yield from self._reader.readexactly(len_data)
            
            return bmsg

        except asyncio.IncompleteReadError:
            # Reached end of stream. (Remote peer disconnected).
            yield from self.close()
            # We return None:
            return None


    @asyncio.coroutine
    def close(self):
        """Close the connection"""
        # We call _writer.close() at most once:
        if self._is_open:
            self._writer.close()
            # Mark connection as closed:
            self._is_open = False


