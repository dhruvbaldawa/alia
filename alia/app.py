import os
import asyncio
import docker
import tornado.httpserver
import signal

from tornado.options import define, options
from tornado.web import url

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from handlers import *
from tasks import task_create_websocket_connections, task_cleanup

try:
    import config
except ImportError:
    print("Configuration not found. Please make sure that config.py exists")

# define command line arguments
define('port', default=config.port, type=int)
define('debug', default=config.debug, type=bool)
define('db_url', default=config.db_url, type=str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            url(r'/', IndexHandler, name='index'),
            url(r'/ws', ProxyWebSocket, name='ws'),
        ]

        settings = dict(
            debug=options.debug,
            port=options.port,
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            xsrf_cookies=True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        engine = create_engine(options.db_url, convert_unicode=True,
                               echo=options.debug)
        self.db = scoped_session(sessionmaker(bind=engine))
        self.docker = docker.from_env()


def main():
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app = Application()

    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)

    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    loop.create_task(task_create_websocket_connections(app))
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), task_cleanup, loop)

    try:
        loop.run_forever()
    except asyncio.CancelledError:
        print('tasks have been cancelled')
    finally:
        loop.close()


if __name__ == '__main__':
    main()
