#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/websocket", WebSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    obj = None

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        WebSocketHandler.waiters.add(self)
        if self.obj:
            self.write_message(self.obj)

        logging.info(self.request.remote_ip)

    def on_close(self):
        WebSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, obj, self):
        cls.cache.append(obj)

    @classmethod
    def send_updates(cls, obj, self):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            if waiter is not self:
                try:
                    waiter.write_message(obj)
                except:
                    logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %s %r" % (self.request.full_url(), message))
        obj = tornado.escape.json_decode(message)

        if  "DOUYU_Code" in obj:
            self.obj = obj

        WebSocketHandler.update_cache(obj, self)
        WebSocketHandler.send_updates(obj, self)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
