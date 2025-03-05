from app import app  # Import your Flask app instance

def handler(request, response):
    # Vercel expects a handler function that processes the request and returns a response
    from wsgiref.handlers import CGIHandler
    from io import StringIO

    # Create a StringIO object for output
    output = StringIO()
    CGIHandler().run(app, {'wsgi.input': StringIO(request.body.decode('utf-8')), 'wsgi.errors': output})

    # Return the response
    response.status = 200
    response.body = output.getvalue().encode('utf-8')
    response.headers['Content-Type'] = 'text/html'