import asyncio
import struct
import bidict

class SerializerError(Exception): pass
class SerializeError(SerializerError): pass
class DeserializeError(SerializerError): pass

class MsgError(SerializerError): pass


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
        return self._msg_type


    def _check_field_exists(self,field):
        """
        Make sure that a field exists.
        """
        if field not in self._afields:
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

    def __init__(self,serializer):
        # Keep serializer:
        self._serializer = serializer

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

    def get_msg(self):
        """
        Get an empty message of the type of this message.
        """
        # Get this class name:
        class_name = type(self).__name__
        return self._serializer.get_msg(class_name)


##################################################################

class ProtoDef:
    outgoing_msgs = {}
    incoming_msgs = {}


##################################################################


def unpack_msg_type(data:bytes):
    """
    Get the msg type from the data.
    Return the message type and the remaining data as a tuple.
    """

    if len(data) < 4:
        raise DeserializeError('Data is too short. len(data) ='
                '{}'.format(len(data)))

    msg_type = struct.unpack("I",data[0:4])[0]
    msg_data = data[4:]
    return msg_type,msg_data


def pack_msg_type(msg_type,msg_data:bytes):
    """
    Given the msg type and the message data, build a full message (Made of
    bytes).
    """
    msg_type_data = struct.pack("I",msg_type)
    data = msg_type_data + msg_data
    return data

###################################################################

def dicts_agree(dc1,dc2):
    """
    Check if two dictionaries agree on the intersection of their domains.
    """
    dom1 = set(dc1.keys())
    dom2 = set(dc2.keys())

    # Domain intersection:
    int_dom = dom1.intersection(dom2)

    # Make sure that the two dicts agree on all of their common domain:
    for k in int_dom:
        if dc1[k] != dc2[k]:
            return False

    return True



class Serializer:
    def __init__(self,proto_def):
        # Calculate intersection between keys of outgoing messages and incoming
        # messages:
        if not \
            dicts_agree(proto_def.incoming_msgs,proto_def.outgoing_msgs):
            raise SerializerError('Incompatible definitions of ' 
                    'incoming and outgoing msgs: {}')

        self._in_keys = proto_def.incoming_msgs.keys()
        self._out_keys = proto_def.outgoing_msgs.keys()

        # Collect a dictionary of all the messages:
        all_msgs = {}
        all_msgs.update(proto_def.incoming_msgs)
        all_msgs.update(proto_def.outgoing_msgs)


        # Dict between msg_type and MsgDef instance:
        self._proto_def = dict()
        # Bidirectional dict between msg type and msg name: 
        self._b_msg_type_name = bidict.bidict()
        for msg_type, msg_def in all_msgs.items():
            # Initialize msg_def with serializer=self
            msg_def_inst = msg_def(self)
            self._proto_def[msg_type] = msg_def_inst
            # Assign the msg_def's instance name:
            self._b_msg_type_name[msg_type] = type(msg_def_inst).__name__

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


    def serialize_msg(self,msg_inst):
        """
        Serialize a message instance to bytes.
        """
        try:
            # Get the relevant msg_def instance:
            msg_type = msg_inst.msg_type
            # Check if we are willing to send this kind of message:
            if msg_type not in self._out_keys:
                raise SerializeError('Message {} is not of type outgoing!'.\
                        format(msg_type))
            msg_def = self._proto_def[msg_type]
            msg_data = msg_def.serialize(msg_inst)
            return pack_msg_type(msg_type,msg_data)
        except SerializeError as e:
            msg_name = self.msg_type_to_msg_name(msg_type)
            raise SerializeError('Failed serializing msg {}.'.\
                    format(msg_name)) from e


    def deserialize_msg(self,data):
        """
        Deserialize data bytes to a message instance.
        """
        try:
            msg_type, msg_data = unpack_msg_type(data)
            if msg_type not in self._proto_def:
                raise DeserializeError('Invalid message type {}.'.\
                        format(msg_type))
            
            # Check if we are willing to receive this message type:
            if msg_type not in self._in_keys:
                raise DeserializeError('Message {} is not of type incoming!'.\
                        format(msg_type))


            msg_def = self._proto_def[msg_type]
            msg_inst = msg_def.deserialize(msg_data)
            return msg_inst
        except DeserializeError as e:
            raise DeserializeError('Failed deserializing msg:\n {}'.\
                    format(msg_data)) from e


    def get_msg(self,msg_name):
        """
        Get an empty message of name msg_name
        """
        msg_type = self.msg_name_to_msg_type(msg_name)
        msg_def = self._proto_def[msg_type]

        # Build an empty message of the correct type:
        msg_inst = Msg(self,msg_type,msg_def.afields)
        return msg_inst


#####################################################
#####################################################


def s_string(s:str) -> bytes:
    """
    Serialize a python string into a length prefixed serialized bytes string
    ('UTF-8')
    """
    s_bytes = s.encode('UTF-8')
    res = struct.pack('I',len(s_bytes))
    res += s_bytes
    return res


def d_string(data:bytes) -> str:
    """
    Parse a length prefixed string from data.
    Returns: Next location (to keep parsing), The resulting string.
    """
    if len(data) < 4:
        raise DeserializeError('data is too short to contain a string.')

    s_len = struct.unpack('I',data[0:4])[0]

    if len(data) < 4 + s_len:
        raise DeserializeError('Invalid length prefix')

    try:
        return 4+s_len,data[4:4+s_len].decode('UTF-8','strict')
    except UnicodeDecodeError:
        raise DeserializeError('Invalid utf-8 string.')


def s_blob(b:bytes) -> bytes:
    """
    Serialize a python bytes object into a length prefixed serialized bytes.
    """
    res = struct.pack('I',len(b))
    res += b
    return res

def d_blob(data:bytes) -> bytes:
    """
    Deserialize data bytes to a python bytes object.
    """
    if len(data) < 4:
        raise DeserializeError('data is too short to contain a blob.')
    
    b_len = struct.unpack('I',data[0:4])[0]

    if len(data) < 4 + b_len:
        raise DeserializeError('Invalid length prefix')

    return 4+b_len,data[4:4+b_len]


def s_uint32(x:int) -> bytes:
    """
    Serializer an integer to bytes
    """
    return struct.pack('I',x)


def d_uint32(data:bytes) -> int:
    """
    Deserialize an integer from the data bytes.
    Returns next location and resulting integer.
    """
    if len(data) < 4:
        raise DeserializeError('data is too short to contain a uint32.')

    return 4,struct.unpack('I',data[0:4])[0]
