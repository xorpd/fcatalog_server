import pytest
import asyncio
import struct

from fcatalog.proto.msg_endpoint import MsgFromFrame,Serializer,MsgDef

from fcatalog.tests.asyncio_util import run_timeout,MockFrameEndpoint

####################################################################
# A dummy protocol messages definition:

class Mess1(MsgDef):
    afields = ['a_int','b_str']

    def serialize(self,msg_inst):
        """
        Serialize a msg_inst to data bytes.
        """
        msg_data = b''

        # Write the integer as a dword.
        a_int = msg_inst.get_field('a_int')
        if not isinstance(a_int,int):
            raise SerializeError('a_int is not an integer!')
        # Assert the a_int is a dword:
        if not (0 <= a_int <= 0xffffffff):
            raise SerializeError('a_int is not a dword!')


        msg_data += struct.pack('I',a_int)

        b_str = msg_inst.get_field('b_str')
        b_str_bytes = b_str.encode('UTF-8')
        # Write the length of b_str as a dword:
        msg_data += struct.pack('I',len(b_str_bytes))
        # Write b_str:
        msg_data += b_str_bytes

        return msg_data


    def deserialize(self,msg_data):
        """
        Deserialize msg_data to msg_inst.
        """
        msg_inst = self.get_msg()

        a_int = struct.unpack('I',msg_data[0:4])[0]
        msg_inst.set_field('a_int',a_int)
        msg_data = msg_data[4:]
        b_str_len = struct.unpack('I',msg_data[0:4])[0]
        msg_data = msg_data[4:]

        if len(msg_data) != b_str_len:
            raise DeserializeError('b_str length is invalid!')

        b_str = msg_data.decode('UTF-8')
        msg_inst.set_field('b_str',b_str)

        return msg_inst


class Mess2(MsgDef):
    afields = ['c_int']

    def serialize(self,msg_inst):
        """
        Serialize a msg_inst to data bytes.
        """
        msg_data = b''

        # Write the integer as a dword.
        c_int = msg_inst.get_field('c_int')
        if not isinstance(c_int,int):
            raise SerializeError('c_int is not an integer!')
        # Assert the a_int is a dword:
        if not (0 <= c_int <= 0xffffffff):
            raise SerializeError('c_int is not a dword!')

        msg_data += struct.pack('I',c_int)

        return msg_data


    def deserialize(self,msg_data):
        """
        Deserialize msg_data to msg_inst.
        """
        msg_inst = self.get_msg()

        c_int = struct.unpack('I',msg_data[0:4])[0]
        msg_inst.set_field('c_int',c_int)
        return msg_inst


proto_def = {1:Mess1, 2:Mess2}

########################################################################


def test_msg_from_frame_passing():
    """
    Test passing messages using msg_from_frame over a frame_endpoint.
    """
    my_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    # Build a serializer:
    ser = Serializer(proto_def)

    # Messages from player 1 to player 2
    q12 = asyncio.Queue(loop=my_loop)

    # Messages from player 2 to player 1
    q21 = asyncio.Queue(loop=my_loop)

    # mff1 = MsgFromFrame(msg_mapper,q21.get,q12.put)
    mff1 = MsgFromFrame(ser,MockFrameEndpoint(q21.get,q12.put))
    # mff2 = MsgFromFrame(msg_mapper,q12.get,q21.put)
    mff2 = MsgFromFrame(ser,MockFrameEndpoint(q12.get,q21.put))

    # A future that marks the end of transaction
    # between player1 and player2:
    transac_fin = asyncio.Future(loop=my_loop)

    @asyncio.coroutine
    def player1():
        # Send mess1 to player 2:
        mess1 = mff1.serializer.get_msg('Mess1')
        mess1.set_field('a_int',1)
        mess1.set_field('b_str','hello')

        yield from mff1.send(mess1)

        # Expect to receive mess2 from player 2:
        mess2 = yield from mff1.recv()
        assert mess2.msg_name == 'Mess2'
        assert mess2.get_field('c_int') == 2

        # Send mess3 to player 1:
        mess1 = mff1.serializer.get_msg('Mess1')
        mess1.set_field('a_int',8)
        mess1.set_field('b_str','The string')
        yield from mff1.send(mess1)


    @asyncio.coroutine
    def player2():
        # Expect to receive mess1 from player 1:
        mess1 = yield from mff2.recv()
        assert mess1.msg_name == 'Mess1'
        assert mess1.get_field('a_int') == 1
        assert mess1.get_field('b_str') == 'hello'

        # Send mess2 to player 1:
        mess2 = mff2.serializer.get_msg('Mess2')
        mess2.set_field('c_int',2)
        yield from mff2.send(mess2)

        # Expect to receive mess1 from player 1:
        mess1 = yield from mff2.recv()
        assert mess1.msg_name == 'Mess1'
        assert mess1.get_field('a_int') == 8
        assert mess1.get_field('b_str') == 'The string'

        transac_fin.set_result(True)


    asyncio.async(player1(),loop=my_loop)
    asyncio.async(player2(),loop=my_loop)
        
    run_timeout(transac_fin,loop=my_loop)

