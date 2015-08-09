import tornado.web

from sockjs.tornado import SockJSConnection


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")


class TickerConnection(SockJSConnection):
    def on_open(self, info):
        self.timeout = tornado.ioloop.PeriodicCallback(self._ticker, 1000)
        self.timeout.start()

    def on_close(self):
        self.timeout.stop()

    def _ticker(self):
        self.send('tick!')
