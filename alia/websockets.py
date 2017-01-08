import aiohttp
import asyncio


class WebsocketInfo(object):
    def __init__(self, websocket=None, container_id=None, task=None):
        self.websocket = websocket
        self.container_id = container_id
        self.task = task


class _WebsocketManager(object):
    def __init__(self):
        self.info = {}
        self.listeners = {}

    async def connect_container(self, container):
        cid = container.short_id
        if cid in self.info:
            raise RuntimeError('container already has a connection')

        socket = container.attach_socket()
        ssl_context = socket.context
        url = container.client.api._url(
            '/containers/{}/attach/ws?logs=1&stdout=1'
            '&stderr=1&stream=1'
            .format(cid))
        settings = {
            'connector': aiohttp.TCPConnector(ssl_context=ssl_context),
        }
        session = aiohttp.ClientSession(**settings)

        async with session.ws_connect(url) as ws:
            info = WebsocketInfo(ws, cid, asyncio.Task.current_task())
            self.info[cid] = info
            while asyncio.get_event_loop().is_running():
                try:
                    msg = await ws.receive()
                except asyncio.CancelledError:
                    print('got cancelled')
                    ws.close()
                    session.close()
                    return

                if msg.type == aiohttp.WSMsgType.TEXT:
                    print('r:{}:{}'.format(cid, msg.data))
                    self.call_listeners(cid, msg.data)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    print('websocket closed:', msg.extra)
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('error occurred for websocket:', msg.data)
                    break
            ws.close()

    def disconnect_container(self, container_id):
        info = self.info.pop(container_id)
        info.task.cancel()
        self.listeners.pop(container_id, '')

    def cleanup(self):
        containers = tuple(self.info.keys())
        for container in containers:
            self.disconnect_container(container)

    def register_listener(self, container_id, listener):
        if container_id in self.listeners:
            self.listeners[container_id].append(listener)
        else:
            self.listeners[container_id] = [listener, ]

    def register_task(self, container, task):
        cid = container.short_id
        self.info[cid].task = task

    def call_listeners(self, container_id, message):
        for listener in self.listeners.get(container_id, []):
            listener(message)

    def send_message(self, container_id, message):
        ws = self.info[container_id].websocket
        ws.send_str(message)


WebsocketManager = _WebsocketManager()
__all__ = ('WebsocketManager', )
