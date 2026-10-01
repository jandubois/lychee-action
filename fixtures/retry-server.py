"""HTTP server for the action's retry tests.

Usage: retry-server.py PORT LOG_FILE

Logs every request path to LOG_FILE. /fails-once answers 404 on its first
request and 200 afterwards, /always-fails always answers 404, and every
other path answers 200.
"""

import http.server
import socketserver
import sys

port, log_path = int(sys.argv[1]), sys.argv[2]
seen = set()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        with open(log_path, "a") as log:
            log.write(self.path + "\n")
        failing = self.path == "/always-fails" or (
            self.path == "/fails-once" and self.path not in seen
        )
        seen.add(self.path)
        self.send_response(404 if failing else 200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    do_GET = do_HEAD


# HTTPServer resolves the bound address back to a host name before it
# listens, which can take longer than the test waits for it.
socketserver.TCPServer(("127.0.0.1", port), Handler).serve_forever()
