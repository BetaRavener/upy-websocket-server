import os
import websocket_helper
from time import sleep

from ws_server import WebSocketServer
from ws_connection import WebSocketConnection


class WebSocketMultiServer(WebSocketServer):
    http_codes = {
        200: "OK",
        404: "Not Found",
        500: "Internal Server Error",
        503: "Service Unavailable"
    }

    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "html": "text/html",
        "htm": "text/html",
        "css": "text/css",
        "js": "application/javascript"
    }

    def __init__(self, index_page, max_connections=1):
        super().__init__(index_page, max_connections)
        dir_idx = index_page.rfind("/")
        self._web_dir = index_page[0:dir_idx] if dir_idx > 0 else "/"

    def _accept_conn(self, listen_sock):
        cl, remote_addr = self._listen_s.accept()
        print("Client connection from:", remote_addr)

        if len(self._clients) >= self._max_connections:
            # Maximum connections limit reached
            cl.setblocking(True)
            self._generate_static_page(cl, 503, "503 Too Many Connections")
            return

        requested_file = None
        data = cl.recv(64).decode()
        if data and "Upgrade: websocket" not in data.split("\r\n") and "GET" == data.split(" ")[0]:
            # data should looks like GET /index.html HTTP/1.1\r\nHost: 19"
            # requested file is on second position in data, ignore all get parameters after question mark
            requested_file = data.split(" ")[1].split("?")[0]
            requested_file = self._page if requested_file in [None, "/"] else requested_file

        try:
            websocket_helper.server_handshake(cl)
            self._clients.append(self._make_client(WebSocketConnection(remote_addr, cl, self.remove_connection)))
        except OSError:
            if requested_file:
                cl.setblocking(True)
                self._serve_file(requested_file, cl)
            else:
                self._generate_static_page(cl, 500, "500 Internal Server Error [2]")

    def _serve_file(self, requested_file, c_socket):
        print("### Serving file: {}".format(requested_file))
        try:
            # check if file exists in web directory
            path = requested_file.split("/")
            filename = path[-1]
            subdir = "/" + "/".join(path[1:-1]) if len(path) > 2 else ""

            if filename not in os.listdir(self._web_dir + subdir):
                self._generate_static_page(c_socket, 404, "404 Not Found")
                return

            # Create path based on web root directory
            file_path = self._web_dir + requested_file
            length = os.stat(file_path)[6]
            c_socket.sendall(self._generate_headers(200, file_path, length))
            # Send file by chunks to prevent large memory consumption
            chunk_size = 1024
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(chunk_size)
                    c_socket.sendall(data)
                    if len(data) < chunk_size:
                        break
            sleep(0.1)
            c_socket.close()
        except OSError:
            self._generate_static_page(c_socket, 500, "500 Internal Server Error [2]")

    @staticmethod
    def _generate_headers(code, filename=None, length=None):
        content_type = "text/html"

        if filename:
            ext = filename.split(".")[1]
            if ext in WebSocketMultiServer.mime_types:
                content_type = WebSocketMultiServer.mime_types[ext]

        # Close connection after completing the request
        return "HTTP/1.1 {} {}\n" \
               "Content-Type: {}\n" \
               "Content-Length: {}\n" \
               "Server: ESPServer\n" \
               "Connection: close\n\n".format(
                code, WebSocketMultiServer.http_codes[code], content_type, length)

    @staticmethod
    def _generate_static_page(sock, code, message):
        sock.sendall(WebSocketMultiServer._generate_headers(code))
        sock.sendall("<html><body><h1>" + message + "</h1></body></html>")
        sleep(0.1)
        sock.close()
