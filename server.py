from app import app  # Import the Flask app instance

# Vercel expects a `handler` function
from vercel_wsgi import make_lambda_handler
handler = make_lambda_handler(app)
