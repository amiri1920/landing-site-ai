from http.server import BaseHTTPRequestHandler
from app import app  # Import your Flask app from app.py

class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        # Create a WSGI environment from the HTTP request
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': self.path,
            'QUERY_STRING': self.path.split('?', 1)[1] if '?' in self.path else '',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'wsgi.input': self.rfile,
            'wsgi.errors': self.wfile,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        # Add HTTP headers to the environment
        for key, value in self.headers.items():
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value

        # Call the Flask app with the WSGI environment
        response = app(environ, self.start_response)

        # Send the response back to the client
        self.wfile.write(b''.join(response))

    def start_response(self, status, headers, exc_info=None):
        # Set the HTTP status code and headers
        self.send_response(int(status.split()[0]))
        for key, value in headers:
            self.send_header(key, value)
        self.end_headers()

# Export the handler class (no instantiation needed)
handler = VercelHandler