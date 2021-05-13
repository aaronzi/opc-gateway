import tornado.ioloop
import tornado.web
from  tornado.escape import json_decode, json_encode
from tornado.gen import Return

import time

from opc_read import connectUa
from opc_read import read
from opc_read import writeX
from opc_read import writeY
from opc_read import subscribe

class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, Content-Type, Content-Range, Content-Disposition, Content-Description, origin, Accept, Authorization, Access-Control-Allow-Origin, X-Custom-Header, Access-Control-Allow-Headers, Referer, User-Agent")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

class MainHandler(BaseHandler):

    async def post(self):
        #Request Data
        data = json_decode(self.request.body)

        # Ping function
        if data['task'] == 'ping':
            self.write('Server returned Status 200; OK')
        # opc write
        if data['task'] == 'write_opc_data':
            await writeX(data)
            await writeY(data)
            self.write(data)
        # opc read
        if data['task'] == 'read_opc_data':
            opc_data = await read(data)
            self.write(str(opc_data))
        # subscribe to OPC Server
        if data['task'] == 'subscribe':
            await subscribe(data)
            #self.write(nodeData)
        if data['task'] == 'connectUa':
            uaData = await connectUa(data)
            self.write(str(uaData))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    tornado.ioloop.IOLoop.current().start()