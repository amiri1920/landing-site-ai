from app import app  # Import the Flask app instance
from vercel_wsgi import make_lambda_handler

handler = make_lambda_handler(app)