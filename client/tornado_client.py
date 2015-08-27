#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from tornado import ioloop
import tornado.escape
from tornado.websocket import websocket_connect

Handlers = {}

def registerHandler(func):
    def wrapper(*args, **kwargs):
        rpcUrl = unicode(args[1])
        self = args[0]
        Handlers[rpcUrl] = self
        func(*args, **kwargs)
    return wrapper


class BaseHandler(object):

    def __init__(self, rpcUrl=None, connection=None):
        self._rpcUrl = rpcUrl
        self._connection = connection

    @property
    def rpcUrl(self):
        return self._rpcUrl

    @rpcUrl.setter
    def rpcUrl(self, value):
        self._rpcUrl = value

    def setrpcUrl(self, value):
        self._rpcUrl = value

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value

    def setConnection(self, value):
        self._connection = value

    def send(self, message):
        logging.info("2142141244")
        self._connection.write_message("message")

    def handleRPC(self, message):
        pass


class FFmpegHandler(BaseHandler):

    @registerHandler
    def __init__(self, rpcUrl=None, connection=None):
        super(FFmpegHandler, self).__init__(rpcUrl, connection)

    def handleRPC(self, message):
        print message, "handleRPC======"
        self.send(message)


class LogHandler(BaseHandler):

    @registerHandler
    def __init__(self, rpcUrl=None, connection=None):
        super(LogHandler, self).__init__(rpcUrl, connection)

    def handleRPC(self, message):
        logging.info(message)


class WebsocketClient(object):

    ws_url = "ws://127.0.0.1:8888/websocket"

    websocketConnection = None

    handlers = {}

    def __init__(self, handlers=None):
        if handlers:
            WebsocketClient.handlers = handlers
        websocket_connect(self.ws_url, 
            callback = self.callback,
            on_message_callback=self.on_message_callback)

    @classmethod
    def on_message_callback(cls, message):
        try:
            obj = tornado.escape.json_decode(message)
            # cls.websocketConnection.write_message(message)
            cls.handleMessage(obj)
            print obj, "========="
        except Exception, e:
            logging.info("unhandle not json format data")

    @classmethod
    def callback(cls, connection):
        cls.websocketConnection = connection.result()
        cls.registerHandlers(cls.handlers)

        print(cls.handlers)

    @classmethod
    def registerHandler(cls, rpcUrl, handler):
        if handler:
            handler.connection = cls.websocketConnection
            cls.handlers.update({rpcUrl: handler})

    @classmethod
    def registerHandlers(cls, handlers):
        for rpcUrl, handler in handlers.items():
            cls.registerHandler(rpcUrl, handler)

    @classmethod
    def handleMessage(cls, obj):
        print obj, "handleMessage", type(obj),  u"rpcUrl" in obj
        if u"rpcUrl" in obj:
            rpcUrl = obj[u'rpcUrl']
            print ("===============", rpcUrl, type(rpcUrl), rpcUrl in WebsocketClient.handlers)
            if rpcUrl in WebsocketClient.handlers:

                handler = WebsocketClient.handlers[rpcUrl]
                print handler
                handler.handleRPC(obj)
                print rpcUrl, "/////////",handler,  obj
        else:
            logging.info("message has no field [rpcUrl]")

def main():
    global Handlers
    ffmpegHandler = FFmpegHandler(u"/FFmpegHandler")
    logHandler =  LogHandler(u"/Log")
    client = WebsocketClient(Handlers)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
