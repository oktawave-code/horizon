#!/usr/bin/env python

import os
import BaseHTTPServer
import argparse
import urllib3
import kubetools
import controller

def HandlerFactory(args, mainController):

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
            if self.path=='/metrics':
                stats = mainController.getStats()
                msg = ''
                for rec in stats:
                    msg += '%s{' % rec['metric']
                    first = True
                    for label in rec['labels']:
                        if not first:
                            msg += ','
                        first = False
                        msg += '%s="%s"' % (label, rec['labels'][label])
                    msg += '} %s\n' % rec['value']
                self._sendMsg(200, msg, headOnly=headOnly)
                return
            self._sendMsg(404, 'Not found', headOnly=headOnly)

    return Handler


def parseArgs():
    parser = argparse.ArgumentParser(description='Horizon kubernetes flow monitor')
    parser.add_argument('--verbose', '-v', action='count', help='Verbosity level')
    parser.add_argument('--defsYaml', default='defs.yaml', help='Defs file')
    parser.add_argument('--port', '-p', default='80', help='HTTP port')
    return parser.parse_args()

def main():
    urllib3.disable_warnings() # Temporary workaround
    args = parseArgs()
    kubetools.logLevel = args.verbose
    kubetools.loadKubernetesConfig()
    mainController = controller.Controller(args)
    handler = HandlerFactory(args, mainController)
    httpd = BaseHTTPServer.HTTPServer(('', int(args.port)), handler)
    sa = httpd.socket.getsockname()
    kubetools.logBold('Monitor listening on %s:%d' % sa)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
