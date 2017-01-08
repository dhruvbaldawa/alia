import asyncio

from websockets import WebsocketManager


async def task_create_websocket_connections(app):
    print('running task_create_websocket_connections')
    containers = app.docker.containers.list()
    for container in containers:
        task = asyncio\
                .get_event_loop()\
                .create_task(WebsocketManager.connect_container(container))
    print('done task_create_websocket_connections')


def task_cleanup(loop):
    print('cleaning up...')
    for task in asyncio.Task.all_tasks():
        task.cancel()
    loop.call_later(1, loop.stop)
