from app import app  # Import your Flask app from app.py
from werkzeug.wrappers import Request, Response

# Define the handler Vercel expects
def handler(event, context):
    # Convert Vercel's event into a WSGI-compatible request
    request = Request(event)
    
    # Create a response object
    response = Response()
    
    # Pass the request to Flask and get the response
    with app.request_context(request.environ):
        wsgi_response = app.full_dispatch_request()
        response.status_code = wsgi_response.status_code
        response.headers = wsgi_response.headers
        response.data = wsgi_response.get_data()

    # Return the response in Vercel’s expected format
    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": response.get_data(as_text=True)
    }