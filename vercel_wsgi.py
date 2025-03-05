from app import app  # Import your Flask app from app.py

def handler(event, context):
    # Create WSGI environment from the event
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', '') or '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.input': event.get('body', '').encode('utf-8') if event.get('body') else b'',
        'wsgi.errors': None,
        'wsgi.version': (1, 0),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'CONTENT_LENGTH': str(len(event.get('body', ''))) if event.get('body') else '0',
        'CONTENT_TYPE': event['headers'].get('Content-Type', ''),
    }
    # Add HTTP headers to the environment
    for key, value in event['headers'].items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value

    # Start response callback
    status = None
    headers = []

    def start_response(status_code, response_headers, exc_info=None):
        nonlocal status
        status = status_code
        headers.extend(response_headers)

    # Call the Flask app
    app_response = app(environ, start_response)

    # Collect the body
    body = ''.join([chunk.decode('utf-8') for chunk in app_response])

    # Return the response in Vercel's expected format
    return {
        'statusCode': int(status.split()[0]),
        'headers': dict(headers),
        'body': body
    }