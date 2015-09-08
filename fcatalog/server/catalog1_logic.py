import asyncio
import os

from .proto.msg_endpoint import MsgEndpoint
from .server_proto import cser_serializer,FSimilar
from .funcs_db import FuncsDB

class ServerLogicError(Exception)

class Catalog1ServerLogic:
    def __init__(self,db_base_path,num_hashes,msg_endpoint):
        # Keep database base path:
        self._db_base_path = db_base_path
        # Keep amount of hashes:
        self._num_hashes = num_hashes
        # Message endpoint:
        self._msg_endpoint = msg_endpoint

        # Initially Functions Database interface is None:
        self._fdb = None

    @asyncio.coroutine
    def client_handler(self):
        """
        Main logic of the catalog1 server, for one client.
        Communication with the client is done through the msg_endpoint class
        instance.
        """
        msg_inst = ( yield from self._msg_endpoint.recv() )

        if msg_inst is None:
            # Remote peer has disconnected or sent invalid data. We disconnect.
            return

        if msg_inst.msg_name != 'ChooseDB':
            # If the first message is not ChooseDB, we disconnect.
            return

        # Database name:
        db_name = msg_inst.get_field('db_name')
        # Conclude database path:
        db_path = os.path.join(db_base_path,db_name)

        # Build a Functions DB interface:
        self._fdb = FuncsDB(db_path,num_hashes)
        try:
            msg_inst = ( yield from self._msg_endpoint.recv() )
            while msg_inst is not None:
                if msg_inst.msg_name == 'ChooseDB':
                    # We can't have two ChooseDB messages in a connection. We
                    # close the connection:
                    return
                elif msg_inst.msg_name == 'AddFunction':
                    yield from self._handle_add_function(msg_inst)
                elif msg_inst.msg_name == 'RequestSimilars':
                    yield from self._handle_request_similars(msg_inst)
                else:
                    # This should never happen:
                    raise ServerLogicError('Unknown message name {}'.\
                            format(msg_inst.msg_name))

                # Receive the next message:
                msg_inst = ( yield from self._msg_endpoint.recv() )

        finally:
            # We make sure to eventually close the fdb interface (To commit all
            # changes that might be pending).
            fdb.close()


    @asyncio.coroutine
    def handle_add_function(self,msg_inst):
        """
        Handle an AddFunction message.
        """
        func_name = msg_inst.get_field('func_name')
        func_comment = msg_inst.get_field('func_comment')
        func_data = msg_inst.get_field('func_data')

        # Add function to database:
        self._fdb.add_function(func_name,func_data,func_comment)

        
    @asyncio.coroutine
    def handle_request_similars(self,msg_inst):
        """
        Handle a RequestSimilars message.
        """
        func_data = msg_inst.get_field('func_data')
        num_similars = msg_inst.get_field('num_similars')

        # Get a list of similar functions from the db:
        sims = self._fdb.get_similars(func_data,num_similars)
        # We convert the sims we have received from the db to another format:
        res_sims = []
        for s in sims:
            fs = FSimilar(name=s.func_name,\
                    comment=s.func_comment,\
                    grade=s.func_grade)
            res_sims.append(fs)
        
        # Build a ResponseSimilars message:
        resp_msg = cser_serializer.get_msg('ResponseSimilars')
        resp_msg.set_field('similars',res_sims)

        # Send back the Response similars message:
        yield from self._msg_endpoint.send(resp_msg)

