import asyncio
import os

from fcatalog.proto.msg_endpoint import MsgFromFrame
from fcatalog.tests.asyncio_util import run_timeout,MockFrameEndpoint

from fcatalog.server.catalog1_logic import Catalog1ServerLogic


from fcatalog.server.catalog1_proto import cser_serializer,\
        ChooseDB,AddFunction,RequestSimilars,ResponseSimilars,\
        FSimilar

from fcatalog.proto.serializer import Serializer,ProtoDef


# A protocol definition for a catalog1 client:
class CatalogClientProtoDef(ProtoDef):
    incoming_msgs = {3:ResponseSimilars}
    outgoing_msgs = {\
        0:ChooseDB,\
        1:AddFunction,\
        2:RequestSimilars}

# Build a client serializer:
client_ser = Serializer(CatalogClientProtoDef)

# Amount of hashes to be used:
NUM_HASHES = 16

def test_basic_catalog1_logic(tmpdir):
    my_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    # Messages from player 1 to player 2
    q12 = asyncio.Queue(loop=my_loop)

    # Messages from player 2 to player 1
    q21 = asyncio.Queue(loop=my_loop)

    mff1 = MsgFromFrame(cser_serializer,MockFrameEndpoint(q21.get,q12.put))
    mff2 = MsgFromFrame(client_ser,MockFrameEndpoint(q12.get,q21.put))


    # A future that marks the end of transaction
    # between player1 and player2:
    transac_fin = asyncio.Future(loop=my_loop)
    sl = Catalog1ServerLogic(tmpdir,NUM_HASHES,mff1)

    server_task1 = asyncio.async(sl.client_handler(),loop=my_loop)

    @asyncio.coroutine
    def client_cor1():
        msg_inst = client_ser.get_msg('ChooseDB')
        msg_inst.set_field('db_name','my_db')
        yield from mff2.send(msg_inst)

        msg_inst = client_ser.get_msg('RequestSimilars')
        msg_inst.set_field('func_data',b'function data example')
        msg_inst.set_field('num_similars',0)
        yield from mff2.send(msg_inst)

        msg_inst = yield from mff2.recv()
        assert msg_inst.msg_name == 'ResponseSimilars'
        assert msg_inst.get_field('similars') == []

        # Add three functions:
        msg_inst = client_ser.get_msg('AddFunction')
        msg_inst.set_field('func_name','name1')
        msg_inst.set_field('func_comment','comment1')
        msg_inst.set_field('func_data',b'This is the function1 data')
        yield from mff2.send(msg_inst)

        msg_inst = client_ser.get_msg('AddFunction')
        msg_inst.set_field('func_name','name2')
        msg_inst.set_field('func_comment','comment2')
        msg_inst.set_field('func_data',b'This is the function2 data')
        yield from mff2.send(msg_inst)

        msg_inst = client_ser.get_msg('AddFunction')
        msg_inst.set_field('func_name','name3')
        msg_inst.set_field('func_comment','comment3')
        msg_inst.set_field('func_data',b'02938459238459283458932452345')
        yield from mff2.send(msg_inst)


        # Request similars:
        msg_inst = client_ser.get_msg('RequestSimilars')
        msg_inst.set_field('func_data',b'This is the function2 data')
        msg_inst.set_field('num_similars',3)
        yield from mff2.send(msg_inst)

        msg_inst = yield from mff2.recv()
        assert msg_inst.msg_name == 'ResponseSimilars'
        sims = msg_inst.get_field('similars')
        assert len(sims) == 2

        assert sims[0].name == 'name2'
        assert sims[0].comment == 'comment2'
        assert sims[0].sim_grade == NUM_HASHES

        assert sims[1].name == 'name1'
        assert sims[1].comment == 'comment1'
        assert sims[1].sim_grade < NUM_HASHES


        # Close the connection with the server:
        yield from mff2.close()
        # Wait for the server coroutine to finish:
        yield from asyncio.wait_for(server_task1,timeout=None,loop=my_loop)
        # Mark as finished:
        transac_fin.set_result(True)


    asyncio.async(client_cor1(),loop=my_loop)
    run_timeout(transac_fin,loop=my_loop,timeout=3.0)

    # We check persistance by logging in with another user:

    # Messages from player 1 to player 2
    q12 = asyncio.Queue(loop=my_loop)
    # Messages from player 2 to player 1
    q21 = asyncio.Queue(loop=my_loop)
    mff1 = MsgFromFrame(cser_serializer,MockFrameEndpoint(q21.get,q12.put))
    mff2 = MsgFromFrame(client_ser,MockFrameEndpoint(q12.get,q21.put))


    # A future that marks the end of transaction
    # between player1 and player2:
    sl = Catalog1ServerLogic(tmpdir,NUM_HASHES,mff1)
    transac_fin = asyncio.Future(loop=my_loop)
    server_task2 = asyncio.async(sl.client_handler(),loop=my_loop)

    @asyncio.coroutine
    def client_cor2():
        # Choose a database:
        msg_inst = client_ser.get_msg('ChooseDB')
        msg_inst.set_field('db_name','my_db')
        yield from mff2.send(msg_inst)

        # Request similars:
        msg_inst = client_ser.get_msg('RequestSimilars')
        msg_inst.set_field('func_data',b'This is the function2 data')
        msg_inst.set_field('num_similars',3)
        yield from mff2.send(msg_inst)

        msg_inst = yield from mff2.recv()
        assert msg_inst.msg_name == 'ResponseSimilars'
        sims = msg_inst.get_field('similars')
        assert len(sims) == 2

        assert sims[0].name == 'name2'
        assert sims[0].comment == 'comment2'
        assert sims[0].sim_grade == NUM_HASHES

        assert sims[1].name == 'name1'
        assert sims[1].comment == 'comment1'
        assert sims[1].sim_grade < NUM_HASHES


        # Close the connection with the server:
        yield from mff2.close()
        # Wait for the server coroutine to finish:
        yield from asyncio.wait_for(server_task2,timeout=None,loop=my_loop)
        # Mark as finished:
        transac_fin.set_result(True)


    asyncio.async(client_cor2(),loop=my_loop)
    run_timeout(transac_fin,loop=my_loop,timeout=3.0)
