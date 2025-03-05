from vercel_wsgi import run
from app import app

def handler(request, context):
    return run(app, request, context)
