from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class TrueHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f'Received POST data: {post_data.decode()}')
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_data = {"status": True}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

def run_server(port=8079):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TrueHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()