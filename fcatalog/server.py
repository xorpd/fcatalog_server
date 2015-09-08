from fcatalog.proto.serializer import serialize_string,deserialize_string,\
        serialize_uint32,deserialize_uint32

class ChooseDB(MsgDef):
    afields = ['db_name']
    def serialize(self,msg_inst) -> bytes:
        """
        Serialize a msg_inst into bytes.
        """
        return serialize_string(msg_inst.get_field('db_name'))

    def deserialize(self,msg_data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        nextl,db_name = deserialize_string(msg_data)
        return db_name


class AddFunction(MsgDef):
    afields = ['func_name','func_comment','func_data']
    def serialize(self,msg_inst) -> bytes:
        """
        Serialize a msg_inst into bytes.
        """
        resl = []
        res_l.append(serialize_string(msg_inst.get_field('func_name')))
        res_l.append(serialize_string(msg_inst.get_field('func_comment')))


        raise NotImplementedError()

    def deserialize(self,msg_data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        raise NotImplementedError()


class RequestSimilars(MsgDef):
    afields = ['func_data','num_similars']
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


class ResponseSimilars(MsgDef):
    afields = ['similars']
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


proto_def = {\
        0:ChooseDB,\
        1:AddFunction,\
        2:RequestSimilars,\
        3:ResponseSimilars}
