import asyncio

from websockets import WebsocketManager


async def task_create_websocket_connections(app):
    print('running task_create_websocket_connections')
    containers = app.docker.containers.list()
    for container in containers:
        task = asyncio\
                .get_event_loop()\
                .create_task(WebsocketManager.connect_container(container))
        WebsocketManager.register_task(container, task)
    print('done task_create_websocket_connections')


def task_cleanup(loop):
    print('cleaning up...')
    try:
        WebsocketManager.cleanup()
    except:
        raise
    finally:
        loop.stop()
