
import aws_lambda_wsgi
from app import app

def lambda_handler(event, context):
    return aws_lambda_wsgi.response(app, event, context)