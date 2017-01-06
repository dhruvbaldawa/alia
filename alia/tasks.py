import asyncio

from registry import Registry


async def task_create_websocket_connections(app):
    print('running task_create_websocket_connections')
    containers = app.docker.containers.list()
    for container in containers:
        await Registry.register_container(container)
    print('done task_create_websocket_connections')


def task_cleanup(loop):
    print('cleaning up...')
    try:
        for k, v in Registry.containers.items():
            if v['ws'] is not None:
                loop.create_task(v['ws'].close)
    finally:
        loop.stop()
