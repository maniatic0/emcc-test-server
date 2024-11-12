from http import server # Python 3

# Based from https://stackoverflow.com/a/13354482
class MyHTTPRequestHandler(server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_my_headers()

        server.SimpleHTTPRequestHandler.end_headers(self)

    def send_my_headers(self):
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")


# From server.py
if __name__ == '__main__':
    import argparse
    import contextlib
    import socket
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind', metavar='ADDRESS',
                        help='bind to this address '
                             '(default: all interfaces)')
    parser.add_argument('-d', '--directory', default=os.getcwd(),
                        help='serve this directory '
                             '(default: current directory)')
    parser.add_argument('-p', '--protocol', metavar='VERSION',
                        default='HTTP/1.0',
                        help='conform to this HTTP version '
                             '(default: %(default)s)')
    parser.add_argument('port', default=8000, type=int, nargs='?',
                        help='bind to this port '
                             '(default: %(default)s)')
    args = parser.parse_args()
    handler_class = MyHTTPRequestHandler

    # ensure dual-stack is not disabled; ref #38907
    class DualStackServer(server.ThreadingHTTPServer):

        def server_bind(self):
            # suppress exception when protocol is IPv4
            with contextlib.suppress(Exception):
                self.socket.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            return super().server_bind()

        def finish_request(self, request, client_address):
            self.RequestHandlerClass(request, client_address, self,
                                     directory=args.directory)

    server.test(
        HandlerClass=handler_class,
        ServerClass=DualStackServer,
        port=args.port,
        bind=args.bind,
        protocol=args.protocol,
    )