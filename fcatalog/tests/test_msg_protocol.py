from fcatalog.proto.msg_protocol import Msg,MsgDef,Serializer,\
        SerializeError,DeserializeError


dummy_proto_def = {
        0:DummyMsgDef()
        }

dummy_ser = Serializer(dummy_proto_def)

class DummyMsgDef(MsgDef):
    afields = ['a_int','b_str']

    def serialize(msg_inst):
        msg_data = b''

        # Write the integer as a dword.
        a_int = msg_inst.get_field('a_int')
        # Assert the a_int is a dword:
        if not (0 <= a_int <= 0xffffffff):
            raise SerializeError('a_int is not a dword!')

        msg_data += struct.pack('I',a_int)

        b_str = msg_inst.get_field('b_str')
        b_str_bytes = b_str.decode('UTF-8')
        # Write the length of b_str as a dword:
        msg_data += struct.pack('I',len(b_str_bytes))
        # Write b_str:
        msg_data += b_str_bytes


    def deserialize(msg_data):
        # msg_inst = dummy_ser.get_msg()
        # msg_inst = Msg(dummy_ser,'DummyMsgDef')
        assert False
        # How to solve cyclic links?

        a_int = struct.unpack('I',msg_data[0:4])[0]
        msg_data = msg_data[4:]
        b_str_len = struct.unpack('I',msg_data[0:4])[0]
        msg_data = msg_data[4:]

        if len(msg_data) != b_str_len:
            raise DeserializeError('b_str length is invalid!')

        b_str = msg_data.encode('UTF-8')



        pass



proto_def = {\
        0:AddFunction(),\
        1:GetSimilars(),\
        2:ChooseDB()}

def test_msg():

    pass
