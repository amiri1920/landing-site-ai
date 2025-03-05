# api/vercel_wsgi.py
from app import app
from io import BytesIO
import sys
from urllib.parse import urlparse

def handler(request, context):
    # Build a basic WSGI environ dictionary from the Vercel request
    environ = {}
    environ['REQUEST_METHOD'] = request.method
    environ['SCRIPT_NAME'] = ''
    parsed_url = urlparse(request.url)
    environ['PATH_INFO'] = parsed_url.path
    environ['QUERY_STRING'] = parsed_url.query
    environ['SERVER_NAME'] = 'localhost'
    environ['SERVER_PORT'] = '80'
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.url_scheme'] = 'https'
    environ['wsgi.input'] = BytesIO(request.body)
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = False
    environ['wsgi.run_once'] = False

    response_body = []
    status = ""
    response_headers = []

    def start_response(s, h, exc_info=None):
        nonlocal status, response_headers
        status = s
        response_headers = h

    result = app(environ, start_response)
    for data in result:
        response_body.append(data)
    output = b"".join(response_body)

    return {
        "statusCode": int(status.split(" ")[0]),
        "headers": dict(response_headers),
        "body": output.decode('utf-8')
    }
