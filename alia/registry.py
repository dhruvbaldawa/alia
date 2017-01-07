import aiohttp
import asyncio


class _Registry(object):
    def __init__(self):
        self.containers = {}
        self.session = aiohttp.ClientSession()
        self.session.detach()

    @staticmethod
    async def _connect_websocket(container):
        socket = container.attach_socket()
        ssl_context = socket.context
        url = container.client.api._url("/containers/{}/attach/ws?stdout=1"
                                        "&stderr=1&stream=1"
                                        .format(container.short_id))
        print("url: " + url)
        ws = await aiohttp.ws_connect(url, connector=aiohttp.TCPConnector(ssl_context=ssl_context))
        return ws

    async def register_container(self, container):
        cid = container.short_id
        if cid in self.containers:
            raise RuntimeError('container already present in the registry')

        self.containers[cid] = {
            'obj': container,
            'ws': None,
            'task': None,
        }
        resp = await self._connect_websocket(container)
        if not resp.closed and resp.exception() is None:
            from tasks import task_receive
            self.containers[cid]['ws'] = resp
            print('connected to websocket for ' + cid)
            task = asyncio.ensure_future(task_receive(cid, resp))

    def remove_closed_container(self):
        pass


Registry = _Registry()
__all__ = ('Registry', )
