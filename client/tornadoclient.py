#!/usr/bin/python
# -*- coding: utf-8 -*-
from ws4py.client.tornadoclient import TornadoWebSocketClient
from tornado import ioloop

class MyClient(TornadoWebSocketClient):
     def opened(self):
         for i in range(0, 200, 25):
             self.send("*" * i)

     def received_message(self, m):
         print m
         if len(m) == 175:
             self.close(reason='Bye bye')

     def closed(self, code, reason=None):
         ioloop.IOLoop.instance().stop()

ws = MyClient('ws://localhost:8888/echo', protocols=['http-only', 'chat'])
ws.connect()

ioloop.IOLoop.instance().start()