# coding=utf-8
# !/usr/bin/python
import logging
import os
import tornado
from tornado.options import define, options

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from wsgi import app

define("port", default=5000, help="run on the given port", type=int)
define("develop", default=True, help="develop environment", type=bool)


tornado.options.parse_command_line()
if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(options.port)
    print "visit at", "http://127.0.0.1:%s" % options.port
    IOLoop.instance().start()
