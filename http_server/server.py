import socket
import os

HOST = '127.0.0.1'
PORT = 8080
WEB_ROOT = './www'  # folder where static files are stored


def handle_request(conn):
    request = conn.recv(1024).decode()
    print(f"[REQUEST]\n{request}")

    lines = request.split('\r\n')
    if not lines:
        return

    # Extract method and path
    request_line = lines[0]
    method, path, _ = request_line.split()

    if path == '/':
        path = '/index.html'

    file_path = WEB_ROOT + path

    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        response = b"HTTP/1.1 200 OK\r\n"
        response += b"Content-Type: text/html\r\n\r\n"
        response += content
    else:
        response = b"HTTP/1.1 404 Not Found\r\n\r\n<h1>404 Not Found</h1>"

    conn.sendall(response)


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"Server running on http://{HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Connected by {addr}")
                handle_request(conn)


if __name__ == "__main__":
    run_server()
