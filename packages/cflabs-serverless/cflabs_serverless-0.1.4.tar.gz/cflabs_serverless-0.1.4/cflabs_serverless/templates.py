"""Jinja2 templates for cflabs-serverless: container-based Flask Lambda deployment (no app.py changes required)."""

from jinja2 import Template

# Dockerfile for AWS Lambda Python container using aws_lambda_wsgi and lambda_entry.py
DOCKERFILE_TEMPLATE = Template("""
# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port for local testing (Lambda ignores this)
EXPOSE {{ port }}

# Build with: docker buildx build --platform linux/amd64 -t <your-image-name> .
                               
# install aws_lambda_wsgi
RUN pip install aws_lambda_wsgi

# Set the Lambda handler to the wrapper
CMD ["lambda_entry.lambda_handler"]
""")

# lambda_entry.py: wrapper to expose Flask app as Lambda handler (no app.py changes needed)
LAMBDA_ENTRY_TEMPLATE = Template("""
import aws_lambda_wsgi
from {{ app_module }} import {{ app_object }}

def lambda_handler(event, context):
    return aws_lambda_wsgi.response({{ app_object }}, event, context)
""")

# AWS SAM template for Lambda container deployment
SAM_TEMPLATE = Template("""AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Flask application deployed with cflabs-serverless

Parameters:
  ImageUri:
    Type: String
    Description: URI of the container image

Globals:
  Function:
    Timeout: {{ timeout }}
    MemorySize: {{ memory_size }}
    Environment:
      Variables:
        PORT: {{ port }}

Resources:
  FlaskFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      CodeUri: .
      ImageUri: !Ref ImageUri
      Architectures:
        - x86_64
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
        RootEvent:
          Type: Api
          Properties:
            Path: /
            Method: ANY

Outputs:
  FlaskApi:
    Description: "API Gateway endpoint URL for Flask function"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/prod/"
    Export:
      Name: !Sub "${AWS::StackName}-ApiUrl"

  FlaskFunction:
    Description: "Flask Lambda Function ARN"
    Value: !GetAtt FlaskFunction.Arn
    Export:
      Name: !Sub "${AWS::StackName}-FunctionArn"

  FlaskFunctionRole:
    Description: "Implicit IAM Role created for Flask function"
    Value: !GetAtt FlaskFunctionRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-FunctionRoleArn"
""")

# cflabs-serverless config template
default_config_yaml = """# cflabs-serverless configuration
app:
  module: {{ app_module }}
  object: {{ app_object }}
  port: {{ port }}

deployment:
  stack_name: {{ stack_name }}
  region: {{ region }}
  memory_size: {{ memory_size }}
  timeout: {{ timeout }}

container:
  base_image: {{ base_image }}
  working_dir: {{ working_dir }}
"""
CONFIG_TEMPLATE = Template(default_config_yaml)

# requirements.txt template (Flask + aws_lambda_wsgi)
REQUIREMENTS_TEMPLATE = Template("""# Flask application dependencies
Flask>=2.3.0
aws_lambda_wsgi

# Add your other dependencies below
# requests>=2.31.0
# boto3>=1.26.0
# sqlalchemy>=2.0.0
""")

# .dockerignore template
DOCKERIGNORE_TEMPLATE = Template("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Git
.git/
.gitignore

# cflabs-serverless
cflabs-config.yaml
template.yaml
.aws-sam/

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
""")

# samconfig.toml template
SAM_CONFIG_TEMPLATE = Template("""version = 0.1
[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "{{ stack_name }}"
region = "{{ region }}"
confirm_changeset = false
capabilities = "CAPABILITY_NAMED_IAM"
parameter_overrides = "ImageUri={{ image_uri }}"
no_fail_on_empty_changeset = true
""")

# GitHub Actions workflow template for CI/CD
GITHUB_ACTIONS_TEMPLATE = Template("""name: Deploy to AWS Lambda

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

env:
  AWS_REGION: [[ region ]]
  STACK_NAME: [[ stack_name ]]
  LAMBDA_NAME: [[ lambda_name ]]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2
    
    - name: Build, tag, and push image to Amazon ECR
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: [[ ecr_repository ]]
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker buildx build --platform linux/amd64 -t ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${{ env.IMAGE_TAG }} .
        docker push ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${{ env.IMAGE_TAG }}
    
    - name: Install AWS SAM CLI
      run: |
        curl -L https://github.com/aws/aws-sam-cli/releases/latest/download/sam-linux-x86_64.zip -o sam.zip
        unzip sam.zip -d sam-installation
        sudo mv sam-installation/sam /usr/local/bin/sam
        rm -rf sam-installation sam.zip
    
    - name: Deploy to AWS Lambda
      run: |
        sam deploy --template-file template.yaml --stack-name ${{ env.STACK_NAME }} --region ${{ env.AWS_REGION }} --capabilities CAPABILITY_IAM --no-confirm-changeset --parameter-overrides ImageUri=${{ env.ECR_REGISTRY }}/${{ env.ECR_REPOSITORY }}:${{ env.IMAGE_TAG }}
    
    - name: Get API Gateway URL
      run: |
        API_URL=$(aws cloudformation describe-stacks --stack-name ${{ env.STACK_NAME }} --region ${{ env.AWS_REGION }} --query 'Stacks[0].Outputs[?OutputKey==`FlaskApi`].OutputValue' --output text)
        echo "API Gateway URL: $API_URL"
        echo "API_URL=$API_URL" >> $GITHUB_OUTPUT
    
    - name: Comment PR with deployment info
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const apiUrl = process.env.API_URL;
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `🚀 **Deployment Successful!**
          
          **API Gateway URL:** ${apiUrl}
          
          Your Flask app has been deployed to AWS Lambda + API Gateway.
          
          ---
          *Deployed by cflabs-serverless*`
          });
""", variable_start_string='[[', variable_end_string=']]') 