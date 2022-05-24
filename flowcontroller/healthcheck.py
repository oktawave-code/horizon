import BaseHTTPServer
import threading
import kubetools

def HandlerFactory(mainController):

    class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

        def _sendMsg(self, code, msg, headOnly=False, type='text/plain'):
            self.send_response(code)
            self.send_header('Content-type', type)
            self.send_header('Content-Length', str(len(msg)))
            self.end_headers()
            if not headOnly:
                self.wfile.write(msg)

        def do_HEAD(self):
            self.do_GET(headOnly=True)

        def do_GET(self, headOnly=False):
            if self.path=='/healthz':
                problems = mainController.checkForProblems()
                if problems is None:
                    self._sendMsg(200, 'OK\n', headOnly=headOnly)
                else:
                    kubetools.logBold('Healthcheck failed: %s' % problems)
                    self._sendMsg(500, 'Not OK: %s\n' % problems, headOnly=headOnly)
                return
            self._sendMsg(404, 'Not found\n', headOnly=headOnly)

        def log_message(self, format, *args):
            pass

    return Handler


class ServerThread(threading.Thread):

    def __init__(self, mainController, port):
        threading.Thread.__init__(self)
        self.mainController = mainController
        self.port = port
        self.daemon = True
        self.start()

    def run(self):
        handler = HandlerFactory(self.mainController)
        httpd = BaseHTTPServer.HTTPServer(('', int(self.port)), handler)
        sa = httpd.socket.getsockname()
        kubetools.logBold('Healthcheck listening on %s:%d' % sa)
        httpd.serve_forever()
