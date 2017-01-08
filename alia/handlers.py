import tornado

from tornado import ioloop, escape, gen, httpclient, httputil, websocket
from websockets import WebsocketManager

URL = "ws://192.168.99.100:2376/containers/214662dd6d69/attach/ws" \
      "?logs=1&stream=1&stdin=1&stdout=1&stderr=1"
DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60


class WebSocketClient(object):
    """Base for web socket clients.
    """

    def __init__(self, connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout

    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        headers = httputil.HTTPHeaders({'Origin': 'https://192.168.99.100:2376'})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(ioloop.IOLoop.current(),
                                                      request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')

        self._ws_connection.write_message(escape.utf8(data))

    def close(self):
        """Close connection.
        """

        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')

        self._ws_connection.close()

    def _connect_callback(self, future):
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break

            self._on_message(msg)

    def _on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """

        pass

    def _on_connection_success(self):
        """This is called on successful connection ot the server.
        """

        print("Connection success")

    def _on_connection_close(self):
        """This is called when server closed the connection.
        """
        print("Connection closed")

    def _on_connection_error(self, exception):
        """This is called in case if connection to the server could
        not established.
        """

        print("Connection error {}".format(exception))


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")


class ProxyWebSocket(tornado.websocket.WebSocketHandler):
    def _validate_container_argument(self):
        try:
            container = self.request.query_arguments['container'][0].decode()
            return container
        except KeyError:
            print('no container specified')
            return None

    def open(self):
        container = self._validate_container_argument()
        if container is None or not WebsocketManager.has_container(container):
            self.close()
            return
        self.container = container
        WebsocketManager.register_listener(container, self._receive_callback)

        print(self.request.query_arguments)
        print("WebSocket opened")

    def on_message(self, message):
        WebsocketManager.send_message(self.container, message)

    def _receive_callback(self, message):
        self.write_message(message)

    def on_close(self):
        # @TODO: remove individual listener
        print("WebSocket closed")

    def check_origin(self, origin):
        return True
