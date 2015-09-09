import collections
from fcatalog.proto.serializer import s_string,d_string,\
        s_blob,d_blob,s_uint32,d_uint32,\
        Serializer,ProtoDef,MsgDef


# A similar function struct
FSimilar = collections.namedtuple('FSimilar',\
        ['name','comment','sim_grade'])

class ChooseDB(MsgDef):
    afields = ['db_name']
    def serialize(self,msg_inst) -> bytes:
        """
        Serialize a msg_inst into bytes.
        """
        return s_string(msg_inst.get_field('db_name'))

    def deserialize(self,msg_data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        msg_inst = self.get_msg()
        nextl,db_name = d_string(msg_data)
        msg_inst.set_field('db_name',db_name)
        return msg_inst


class AddFunction(MsgDef):
    afields = ['func_name','func_comment','func_data']
    def serialize(self,msg_inst) -> bytes:
        """
        Serialize a msg_inst into bytes.
        """
        resl = []
        resl.append(s_string(msg_inst.get_field('func_name')))
        resl.append(s_string(msg_inst.get_field('func_comment')))
        resl.append(s_blob(msg_inst.get_field('func_data')))
        return b''.join(resl)

    def deserialize(self,msg_data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        nl,func_name = d_string(msg_data)
        msg_data = msg_data[nl:]
        nl,func_comment = d_string(msg_data)
        msg_data = msg_data[nl:]
        nl,func_data = d_blob(msg_data)

        msg_inst = self.get_msg()
        msg_inst.set_field('func_name',func_name)
        msg_inst.set_field('func_comment',func_comment)
        msg_inst.set_field('func_data',func_data)
        return msg_inst


class RequestSimilars(MsgDef):
    afields = ['func_data','num_similars']
    def serialize(self,msg_inst) -> bytes:
        """
        Serialize a msg_inst into bytes.
        """
        resl = []
        resl.append(s_blob(msg_inst.get_field('func_data')))
        resl.append(s_uint32(msg_inst.get_field('num_similars')))
        return b''.join(resl)

    def deserialize(self,msg_data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        nl,func_data = d_blob(msg_data)
        msg_data = msg_data[nl:]
        nl,num_similars = d_uint32(msg_data)

        msg_inst = self.get_msg()
        msg_inst.set_field('func_data',func_data)
        msg_inst.set_field('num_similars',num_similars)
        return msg_inst


class ResponseSimilars(MsgDef):
    afields = ['similars']
    def serialize(self,msg_inst) -> bytes:
        """
        Serialize a msg_inst into bytes.
        """
        sims = msg_inst.get_field('similars')
        resl = []
        resl.append(s_uint32(len(sims)))
        
        for sim in sims:
            resl.append(s_string(sim.name))
            resl.append(s_string(sim.comment))
            resl.append(s_uint32(sim.sim_grade))

        return b''.join(resl)


    def deserialize(self,msg_data:bytes):
        """
        Deserialize data bytes into a msg_inst.
        """
        # Read the amount of similars:
        nl,num_sims = d_uint32(msg_data)
        msg_data = msg_data[nl:]

        sims = []
        for _ in range(num_sims):
            nl,sim_name = d_string(msg_data)
            msg_data = msg_data[nl:]
            nl,sim_comment = d_string(msg_data)
            msg_data = msg_data[nl:]
            nl,sim_grade = d_uint32(msg_data)
            msg_data = msg_data[nl:]

            sims.append(FSimilar(\
                    name=sim_name,\
                    comment=sim_comment,\
                    sim_grade=sim_grade\
                    ))

        msg_inst = self.get_msg()
        msg_inst.set_field('similars',sims)
        return msg_inst


class FCatalogProtoDef(ProtoDef):
    incoming_msgs = {\
        0:ChooseDB,\
        1:AddFunction,\
        2:RequestSimilars}
    outgoing_msgs = {3:ResponseSimilars}



cser_serializer = Serializer(FCatalogProtoDef)

###############################################################
###############################################################

