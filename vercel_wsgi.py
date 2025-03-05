from app import app  # Import your Flask app instance

def handler(request):
    # Vercel expects a handler function that takes a request object and returns a response object
    from werkzeug.wrappers import Request, Response

    # Create a Werkzeug Request object from the Vercel request
    req = Request.from_values(
        input_stream=request.body,
        content_length=len(request.body),
        method=request.method,
        headers=request.headers
    )

    # Use Flask's WSGI app to handle the request
    response = Response()
    app(req.environ, response.start_response)

    # Prepare the response for Vercel
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=False).decode('utf-8')
    }