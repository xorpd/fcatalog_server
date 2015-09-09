import asyncio
import server_conf

from fcatalog.server.fcatalog_logic import FCatalogServerLogic
from fcatalog.server.fcatalog_proto import cser_serializer
from fcatalog.proto.frame_endpoint import TCPFrameEndpoint
from fcatalog.proto.msg_endpoint import MsgFromFrame


@asyncio.coroutine
def client_handler(reader,writer):
    """
    A coroutine for handling one client.
    """
    frame_endpoint = TCPFrameEndpoint(reader,writer)
    msg_endpoint = MsgFromFrame(cser_serializer,frame_endpoint)
    sl = FCatalogServerLogic(server_conf.DB_BASE_PATH,\
            server_conf.NUM_HASHES,\
            msg_endpoint)

    # Handle one client:
    yield from sl.client_handler()


def start_server(host,port):
    """
    Start a fcatalog server on host <host> and port <port>.
    """
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(client_handler,host=host,port=port,loop=loop)
    server = loop.run_until_complete(coro)

    print('FCatalog server is running on {}:{}'.format(host,port))

    loop.run_forever()

    server.close()
    loop.run_until_complete(server.wait_closed)
    loop.close()


if __name__ == '__main__':
    start_server()
