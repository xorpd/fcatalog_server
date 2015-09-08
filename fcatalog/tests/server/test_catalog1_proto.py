from fcatalog.server.catalog1_proto import \
        ChooseDB,AddFunction,RequestSimilars,ResponseSimilars,\
        FSimilar

from fcatalog.proto.serializer import Serializer,ProtoDef


# Create a full catalog1 protocol definition:

class FullCatalog1ProtoDef(ProtoDef):
    incoming_msgs = {\
        0:ChooseDB,\
        1:AddFunction,\
        2:RequestSimilars,\
        3:ResponseSimilars}
    outgoing_msgs = {\
        0:ChooseDB,\
        1:AddFunction,\
        2:RequestSimilars,\
        3:ResponseSimilars}

ser = Serializer(FullCatalog1ProtoDef)


def test_choose_db_msg():
    """
    Verify serialization/deserialization of ChooseDB message.
    """
    msg_inst = ser.get_msg('ChooseDB')
    msg_inst.set_field('db_name','my_database')
    msg_data = ser.serialize_msg(msg_inst)
    msg_data2 = ser.serialize_msg(ser.deserialize_msg(msg_data))
    assert msg_data == msg_data2


def test_add_function_msg():
    """
    Verify serialization/deserialization of AddFunction message.
    """
    msg_inst = ser.get_msg('AddFunction')
    msg_inst.set_field('func_name','function name')
    msg_inst.set_field('func_comment','comment')
    msg_inst.set_field('func_data',b'This is the data')

    msg_data = ser.serialize_msg(msg_inst)
    msg_data2 = ser.serialize_msg(ser.deserialize_msg(msg_data))
    assert msg_data == msg_data2


def test_request_similars_msg():
    """
    Verify serialization/deserialization of RequestSimilars message.
    """
    msg_inst = ser.get_msg('RequestSimilars')
    msg_inst.set_field('func_data',b'Function data example')
    msg_inst.set_field('num_similars',8)

    msg_data = ser.serialize_msg(msg_inst)
    msg_data2 = ser.serialize_msg(ser.deserialize_msg(msg_data))
    assert msg_data == msg_data2


def test_response_similars_msg():
    """
    Verify serialization/deserialization of Response message.
    """
    msg_inst = ser.get_msg('ResponseSimilars')
    sims = []
    sims.append(FSimilar(\
            name='name1',\
            comment='comment1',\
            sim_grade=5))

    sims.append(FSimilar(\
            name='name2',\
            comment='comment2',\
            sim_grade=8))
    msg_inst.set_field('similars',sims)

    msg_data = ser.serialize_msg(msg_inst)
    msg_data2 = ser.serialize_msg(ser.deserialize_msg(msg_data))
    assert msg_data == msg_data2
