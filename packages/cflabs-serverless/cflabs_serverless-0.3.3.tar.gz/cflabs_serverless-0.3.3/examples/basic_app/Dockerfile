
# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port for local testing (Lambda ignores this)
EXPOSE 8000

# Build with: docker buildx build --platform linux/amd64 -t <your-image-name> .
                               
# install aws_lambda_wsgi
RUN pip install aws_lambda_wsgi

# Set the Lambda handler to the wrapper
CMD ["lambda_entry.lambda_handler"]