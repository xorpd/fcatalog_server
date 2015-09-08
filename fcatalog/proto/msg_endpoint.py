import asyncio
from fcatalog.proto.serializer import DeserializeError,SerializeError


class MsgEndpoint:
    @asyncio.coroutine
    def send(self,msg):
        """Send a message"""
        raise NotImplementedError()

    @asyncio.coroutine
    def recv(self):
        """Receive a message"""
        raise NotImplementedError()

    @asyncio.coroutine
    def close(self):
        """Close the connection"""
        raise NotImplementedError()



class MsgFromFrame(MsgEndpoint):
    def __init__(self,serializer,frame_endpoint):
        # Keep serializer:
        self.serializer = serializer

        # Keep frame_endpoint:
        self._frame_endpoint = frame_endpoint


    @asyncio.coroutine
    def recv(self):
        """
        receive a message from the other side.
        Return None if connection should be considered closed.
        """
        # Get a frame from the frame_endpoint:
        frame = yield from self._frame_endpoint.recv()

        # Check if the remote host has closed the connection:
        if frame is None:
            return None

        try:
            # Deserialize the frame into a message:
            msg_inst = self.serializer.deserialize_msg(frame)
        except DeserializeError:
            # If we have an error reading the frame, we consider the
            # connection as closed:
            return None

        return msg_inst


    @asyncio.coroutine
    def send(self,msg):
        """
        Send a message msg to the other side.
        """
        frame = self.serializer.serialize_msg(msg)
        return ( yield from self._frame_endpoint.send(frame) )


    @asyncio.coroutine
    def close(self):
        """
        Close the connection
        """
        # Close the connection:
        yield from self._frame_endpoint.close()
