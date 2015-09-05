import asyncio
import struct

class MsgProtocolError: pass
class SerializeError(MsgProtocolError): pass
class DeserializeError(MsgProtocolError): pass

class MsgError(MsgProtocolError): pass


# A message instance:
class Msg:
    def __init__(self,serializer,msg_type,afields):
        # Keep a link to the serializer:
        self._serializer = serializer
        # Keep the msg_type:
        self._msg_type = msg_type
        # Set of allowed fields:
        self._afields = afields

        # Values of fields:
        self._fields = {}

    def _check_field_exists(self,field):
        """
        Make sure that a field exists.
        """
        if field not in self._afields
            raise MsgError('Msg {} does not have field {}.'.format(\
                    self._serializer.msg_name_by_msg_type(self._msg_type),\
                    field))

    def set_field(self,field,value):
        """
        Set a message field (If exists):
        """
        self._check_field_exists(field)
        self._fields[field] = value

    def get_field(self,field):
        """
        Get a message field (If exists):
        """
        self._check_field_exists(field)
        return self._fields[field]


class MsgDef:
    # The allowed fields of the message:
    AFIELDS = []
    def __init__(self):
        pass

    def serialize(self,msg_inst) -> bytes:
        """
        Serialize an msg_inst into bytes.
        """
        raise NotImplementedError()

    def deserialize(self,data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        raise NotImplementedError()


class AddFunction(MsgDef):
    pass

class GetSimilars(MsgDef):
    pass

class ResultSimilars(MsgDef):
    pass

class ChooseDB(MsgDef):
    pass


proto_def = {\
        0:AddFunction,\
        1:GetSimilars,\
        2:ChooseDB}


def unpack_msg_type(data:bytes):
    """
    Get the msg type from the data.
    Return the message type and the remaining data as a tuple.
    """

    if len(data) < 4:
        raise DeserializeError('Data is too short. len(data) ='
                '{}'.format(len(data)))

    try:
        msg_type = struct.unpack("I",data[0:4])[0]
        msg_data = data[4:]
        return msg_type,msg_data
    except Exception as e:
        raise DeserializeError() from e


def pack_msg_type(msg_type,msg_data:bytes):
    """
    Given the msg type and the message data, build a full message (Made of
    bytes).
    """
    try:
        msg_type_data = struct.pack("I",data[0:4])
        data = msg_type_data + msg_data
        return data
    except Exception as e:
        raise SerializeError() from e


class Serializer:
    def __init__(self,proto_def):
        raise NotImplementedError()

    def msg_name_by_msg_type(self,msg_type):
        """
        Convert message type (Integer) to message name (string).
        """
        raise NotImplementedError()

    def serialize_msg(msg_type,obj):
        raise NotImplementedError()




