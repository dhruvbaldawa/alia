import os
import tornado
import tornado.httpserver

from tornado.options import define, options
from tornado.web import url

from sockjs.tornado import SockJSRouter

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from handlers import *

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


def main():
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
