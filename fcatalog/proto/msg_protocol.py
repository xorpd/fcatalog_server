import asyncio
import struct
import bidict

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
        self._afields = set(afields)

        # Values of fields:
        self._fields = {}

    @property
    def msg_name(self):
        """
        Get the message name of the Msg.
        """
        return self._serializer.msg_type_to_msg_name(self._msg_type)

    @property
    def msg_type(self):
        """
        Get the message type of the Msg
        """
        return self._msg_type()


    def _check_field_exists(self,field):
        """
        Make sure that a field exists.
        """
        if field not in self._afields
            raise MsgError('Msg {} does not have field {}.'.format(\
                    self.msg_name,field))

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

#######################################################


class MsgDef:
    # The allowed fields of the message:
    afields = []

    def serialize(self,msg_inst) -> bytes:
        """
        Serialize a msg_inst into bytes.
        """
        raise NotImplementedError()

    def deserialize(self,msg_data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        raise NotImplementedError()





##################################################################


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

###################################################################


class Serializer:
    def __init__(self,proto_def):
        # Create a bidirectional dictionary from proto_def
        self._proto_def = proto_def

        # Bidirectional dict between msg type and msg name: 
        self._b_msg_type_name = bidict.bidict()
        for msg_type,msg_def in self._proto_def.items():
            # Assign the msg_def's instance name:
            self._b_msg_type_name[msg_type] = type(msg_def).__name__

    def msg_type_to_msg_name(self,msg_type):
        """
        Convert message type (Integer) to message name (string).
        """
        return self._b_msg_type_name[msg_type:]

    def msg_name_to_msg_type(self,msg_name):
        """
        Convert message name (string) to message type (Integer).
        """
        return self._b_msg_type_name[:msg_name]


    def serialize_msg(msg_inst):
        """
        Serialize a message instance to bytes.
        """
        try:
            # Get the relevant msg_def instance:
            msg_type = msg_inst.msg_type
            msg_def = self._proto_def[msg_type]
            msg_data = msg_def.serialize(msg_inst)
            return pack_msg_type(msg_type,msg_data)
        except Exception as e:
            msg_name = self.msg_type_to_msg_name(msg_type)
            raise SerializeError('Failed serializing msg {}.'.format(msg_name))\
                    from e


    def deserialize_msg(data):
        """
        Deserialize data bytes to a message instance.
        """
        try:
            msg_type, msg_data = unpack_msg_type(data)
            if msg_type not in self._proto_def:
                raise DeserializeError('Invalid message type {}.'.\
                        format(msg_type))

            msg_def = self._proto_def[msg_type]
            msg_inst = msg_def.deserialize(msg_data)
            return msg_inst
        except Exception as e:
            msg_name = self.msg_type_to_msg_name(msg_type)
            raise DeserializeError('Failed deserializing msg {}'.\
                    format(msg_name)) from e


    def get_msg(self,msg_name):
        """
        Get an empty message of name msg_name
        """
        msg_type = self._msg_name_to_msg_type(msg_name)
        msg_def = self._proto_def[msg_type]

        # Build an empty message of the correct type:
        msg_inst = Msg(self,msg_type,msg_def.afields)
        return msg_inst


#####################################################
#####################################################


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
        raise NotImplementedError()


    @asyncio.coroutine
    def recv(self):
        """
        receive a message from the other side.
        """
        raise NotImplementedError()


    @asyncio.coroutine
    def send(self,msg):
        """
        Send a message msg to the other side.
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def close(self):
        """
        Close the connection
        """
        # Close the connection:
        yield from self._frame_endpoint.close()
