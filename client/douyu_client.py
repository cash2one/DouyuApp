#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import subprocess
import logging
from tornado import ioloop
import tornado.escape
from tornado.websocket import websocket_connect

Handlers = {}

# 获取指定路径下所有指定后缀的文件
# dir 指定路径
# ext 指定后缀，链表&不需要带点 或者不指定。例子：['xml', 'java']
def GetFileFromThisRootDir(dirFolder,ext = None):
    allfiles = []
    needExtFilter = (ext != None)
    for root,dirs,files in os.walk(dirFolder):
        for filespath in files:
            filepath = os.path.join(root, filespath)
            extension = os.path.splitext(filepath)[1][1:]
            if needExtFilter and extension in ext:
                allfiles.append(filepath)
            elif not needExtFilter:
                pass
    return allfiles

def registerHandler(func):
    def wrapper(*args, **kwargs):
        rpcUrl = unicode(args[1])
        self = args[0]
        Handlers[rpcUrl] = self
        func(*args, **kwargs)
    return wrapper


class FFmpegManager(object):
    
    DOUYU_RTMP = "rtmp://send1a.douyutv.com/live"

    def __init__(self, handler, folder, rtmpURL=None, code=None):
        super(FFmpegManager, self).__init__()
        self.handler = handler
        self.folder = folder
        self.DOUYU_RTMP = rtmpURL
        self.DOUYU_Code = code
        self.breakFlag = False
        self.movies = []
        self.play(self.folder)

    def getRTMPUrl(self):
        return os.path.join(self.DOUYU_RTMP, self.DOUYU_Code)

    def killFFmpeg(self):
        self.breakFlag = True
        cmd = "killall ffmpeg"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    def startFFmpeg(self, cmd):
        print cmd
        self.handler.send({
            "cmd": cmd,
            "movies": self.movies,
            "DOUYU_Code": self.DOUYU_Code
        })
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    def play(self, folder):
        self.movies = GetFileFromThisRootDir(folder, ['mp4'])
        rtmpURL = self.getRTMPUrl()
        self.movies.append("http://dragondjf.github.io/iris/vedio/iris.mp4")

        for movie in self.movies:
            if self.breakFlag:
                break
            cmd = u'''ffmpeg -re -i \"%s\" -vcodec copy -acodec copy -f flv \"%s\"''' % (unicode(movie), unicode(rtmpURL))
            try:
                self.startFFmpeg(cmd)
            except Exception, e:
                print e


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
        obj = tornado.escape.json_encode(message)
        self._connection.write_message(obj)

    def handleRPC(self, message):
        pass


class FFmpegHandler(BaseHandler):

    @registerHandler
    def __init__(self, rpcUrl=None, connection=None):
        super(FFmpegHandler, self).__init__(rpcUrl, connection)
        self.ffmpegManager = None

    def handleRPC(self, obj):
        if u'rpcUrl' in obj:
            if obj['rpcUrl'] == unicode(self.rpcUrl):
                rtmpURL = obj[u'rpcMessage'][u'rtmp-url']
                rtmpCode = obj[u'rpcMessage'][u'rtmp-code']
                if self.ffmpegManager:
                    print ("==============")
                    self.ffmpegManager.killFFmpeg()
                self.ffmpegManager = FFmpegManager(self, sys.argv[1], rtmpURL, rtmpCode)


class LogHandler(BaseHandler):

    @registerHandler
    def __init__(self, rpcUrl=None, connection=None):
        super(LogHandler, self).__init__(rpcUrl, connection)

    def handleRPC(self, message):
        logging.info(message)


class WebsocketClient(object):

    ws_url = "ws://106.186.19.60:8888/websocket?client=Raspberrypi"

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
            cls.handleMessage(obj)
        except Exception, e:
            logging.info("unhandle not json format data")

    @classmethod
    def callback(cls, connection):
        cls.websocketConnection = connection.result()
        cls.registerHandlers(cls.handlers)

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
        if u"rpcUrl" in obj:
            rpcUrl = obj[u'rpcUrl']
            if rpcUrl in WebsocketClient.handlers:
                handler = WebsocketClient.handlers[rpcUrl]
                print obj
                handler.handleRPC(obj)
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
