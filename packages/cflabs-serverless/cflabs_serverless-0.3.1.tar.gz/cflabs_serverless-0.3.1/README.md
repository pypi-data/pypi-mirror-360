# cflabs-serverless

Deploy Flask apps to AWS Lambda + API Gateway with **zero code changes**.

## 🚀 Features

- **Zero-touch deployment**: Your Flask app stays unchanged
- **Single command deployment**: `cflabs-serverless deploy`
- **CI/CD ready**: Generate GitHub Actions workflows for automated deployment
- **AWS Lambda Web Adapter**: Runs Gunicorn inside Lambda containers
- **Automatic scaffolding**: Generates Dockerfile and SAM template
- **Simple CLI**: Intuitive commands for the full deployment lifecycle
- **Image tag control**: Specify custom Docker image tags for deployments

## 📦 Installation

```bash
pip install cflabs-serverless
```

## 🎯 Quick Start

**Deploy** your Flask app to AWS with a single command:

```bash
cflabs-serverless deploy
```

That's it! Your Flask app is now running on AWS Lambda + API Gateway.

The `deploy` command automatically:
- Detects your Flask app (`app.py`)
- Generates all necessary files (Dockerfile, SAM template, etc.)
- Builds and pushes the Docker container
- Deploys to AWS Lambda + API Gateway

## 📋 Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate permissions
- Docker installed and running
- AWS SAM CLI installed

## 🔧 CLI Commands

### `deploy`
Deploy Flask app to AWS Lambda + API Gateway (all-in-one command):

```bash
cflabs-serverless deploy
```

**Options:**
- `--name, -n`: Name for your Lambda function (prompts if not provided)
- `--region, -r`: AWS region (default: us-east-1)
- `--port, -p`: Application port (default: 8000)
- `--memory`: Lambda memory size in MB (default: 512)
- `--timeout, -t`: Lambda timeout in seconds (default: 30)
- `--image-tag, -i`: Docker image tag to use for deployment (default: latest)

**Examples:**
```bash
# Deploy with default settings (will prompt for function name)
cflabs-serverless deploy

# Deploy with custom name and region
cflabs-serverless deploy --name my-awesome-app --region us-west-2

# Deploy with custom configuration
cflabs-serverless deploy --name my-app --memory 1024 --timeout 60

# Deploy with specific image tag
cflabs-serverless deploy --name my-app --image-tag v1.0.0

# Deploy with commit SHA (like CI/CD)
cflabs-serverless deploy --name my-app --image-tag $(git rev-parse --short HEAD)
```

The deploy command automatically:
- Detects your Flask app (`app.py`)
- Generates Dockerfile, SAM template, and configuration files
- Creates ECR repository and builds Docker container
- Deploys to AWS Lambda + API Gateway
- Shows real-time progress with progress bars

### `logs`
Stream logs from your deployed function:

```bash
cflabs-serverless logs
```

### `delete`
Remove the deployed stack and clean up ECR:

```bash
cflabs-serverless delete
```

### `status`
Show deployment status and information:

```bash
cflabs-serverless status
```

### `doctor`
Diagnose and fix common issues:

```bash
cflabs-serverless doctor
```

### `generate`
Generate deployment files (Dockerfile, template.yaml, etc.) without deploying:

```bash
cflabs-serverless generate
```

**Options:**
- `--name, -n`: Name for your Lambda function (prompts if not provided)
- `--region, -r`: AWS region (default: us-east-1)
- `--port, -p`: Application port (default: 8000)
- `--memory`: Lambda memory size in MB (default: 512)
- `--timeout, -t`: Lambda timeout in seconds (default: 30)
- `--image-tag, -i`: Docker image tag to use for deployment (default: latest)
- `--config, -c`: Path to config file
- `--force, -f`: Overwrite existing files

**Examples:**
```bash
# Generate files with default settings
cflabs-serverless generate

# Generate files with custom name and force overwrite
cflabs-serverless generate --name my-app --force

# Generate files for CI/CD (using commit SHA)
cflabs-serverless generate --name my-app --image-tag $(git rev-parse --short HEAD)
```

### `create-workflow`
Generate GitHub Actions workflow for CI/CD deployment:

```bash
cflabs-serverless create-workflow
```

**Options:**
- `--name, -n`: Name for your Lambda function
- `--region, -r`: AWS region (default: us-east-1)
- `--stack-name, -s`: Name of the CloudFormation stack
- `--ecr-repo`: ECR repository name
- `--config, -c`: Path to config file
- `--force, -f`: Overwrite existing workflow file

**Examples:**
```bash
# Generate workflow with default settings
cflabs-serverless create-workflow

# Generate workflow with custom options
cflabs-serverless create-workflow --name my-app --region us-west-2 --force

# Generate workflow using existing config
cflabs-serverless create-workflow --config cflabs-config.yaml
```

The generated workflow will:
- Run tests on every push and pull request
- Build and push Docker image with unique tags
- Deploy to AWS Lambda automatically
- Verify Lambda is using the latest image
- Comment deployment info on pull requests

### `troubleshoot`
Show comprehensive AWS troubleshooting guide:

```bash
cflabs-serverless troubleshoot
```

## 📁 Project Structure

After running `deploy`, your project will have:

```
your-flask-app/
├── app.py                 # Your existing Flask app (unchanged)
├── requirements.txt       # Python dependencies (auto-generated if missing)
├── Dockerfile            # Generated container config
├── template.yaml         # Generated SAM template
├── .dockerignore         # Docker ignore file (auto-generated if missing)
├── cflabs-config.yaml    # Configuration file
└── .github/
    └── workflows/
        └── deploy.yml    # GitHub Actions workflow (if using CI/CD)
```

**Note:** All files except `app.py` are automatically generated during deployment.

## ⚙️ Configuration

The `cflabs-config.yaml` file contains your deployment settings:

```yaml
app:
  module: app
  object: app
  port: 8000

deployment:
  stack_name: my-flask-app
  region: us-east-1
  memory_size: 512
  timeout: 30
  image_uri: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app-repo:latest
  image_tag: latest

container:
  base_image: public.ecr.aws/lambda/python:3.11
  working_dir: /var/task
```

## 🏷️ Image Tag Strategies

### Manual Deployment
```bash
# Use latest tag (default)
cflabs-serverless deploy

# Use specific version
cflabs-serverless deploy --image-tag v1.0.0

# Use commit SHA
cflabs-serverless deploy --image-tag $(git rev-parse --short HEAD)

# Use timestamp
cflabs-serverless deploy --image-tag $(date +%Y%m%d-%H%M%S)
```

### CI/CD Deployment
The GitHub Actions workflow automatically uses:
- **Unique tags**: `${{ github.sha }}` (commit SHA)
- **Force updates**: `--force-upload` ensures Lambda updates
- **Verification**: Confirms Lambda uses the correct image

This ensures:
- **Reproducible deployments**: Each commit has a unique image
- **Rollback capability**: Deploy previous versions by tag
- **No conflicts**: Lambda always updates to the latest image

## 🔍 How It Works

1. **AWS Lambda Web Adapter**: Uses the binary at `/lambda-adapter` to handle HTTP requests
2. **Gunicorn**: Runs your Flask app with Gunicorn inside the Lambda container
3. **Zero Code Changes**: Your Flask app runs exactly as it does locally
4. **SAM Template**: Automatically generated with proper API Gateway integration

## 🚀 CI/CD with GitHub Actions

Set up automated deployment with GitHub Actions:

### 1. Generate Workflow

```bash
cflabs-serverless create-workflow --name my-flask-app
```

This creates `.github/workflows/deploy.yml` with:
- **Test job**: Runs your tests and coverage
- **Deploy job**: Builds, pushes, and deploys to AWS Lambda
- **Verification**: Ensures Lambda uses the latest image
- **PR comments**: Posts deployment info on pull requests

### 2. Add AWS Credentials

Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### 3. Push to Deploy

Every push to `main` or `master` will:
1. Run tests
2. Build Docker image with unique tag (`${{ github.sha }}`)
3. Push to ECR
4. Deploy to AWS Lambda
5. Verify deployment

### 4. Workflow Features

- **Unique Image Tags**: Uses commit SHA for reproducible deployments
- **Force Updates**: Ensures Lambda always uses the latest image
- **Error Handling**: Fails if Lambda doesn't update correctly
- **PR Integration**: Comments deployment URLs on pull requests
- **Test Coverage**: Runs tests and uploads coverage reports

## 🛠️ Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/cosmicfusionlabs/cflabs-serverless.git
cd cflabs-serverless

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```

### Building for Distribution

```bash
# Build the package
python -m build

# Install from local build
pip install dist/cflabs_serverless-*.whl
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🐛 Issues

Found a bug? Please [open an issue](https://github.com/cosmicfusionlabs/cflabs-serverless/issues) with:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior

## 🔧 Troubleshooting

### Common AWS Errors

If you encounter AWS-related errors, try these steps:

1. **Run diagnostics:**
   ```bash
   cflabs-serverless doctor
   ```

2. **View troubleshooting guide:**
   ```bash
   cflabs-serverless troubleshoot
   ```

3. **Check AWS permissions:**
   - Ensure your AWS user has the required permissions
   - For testing, attach the `AdministratorAccess` managed policy
   - Or create a custom policy with minimum required permissions

4. **Common solutions:**
   - **Access Denied**: Check IAM permissions
   - **No Such Bucket**: SAM will create S3 bucket automatically
   - **Repository Already Exists**: Normal, deployment will continue
   - **Image Not Found**: Run `cflabs-serverless build` first
   - **Credentials Error**: Run `aws configure`

### Getting Help

- Check the [troubleshooting guide](https://github.com/cosmicfusionlabs/cflabs-serverless#troubleshooting)
- Run `cflabs-serverless doctor` for automated diagnostics
- Review AWS CloudFormation console for stack errors
- Check CloudWatch logs: `cflabs-serverless logs`

## 📚 Examples

### Basic Flask App

```python
# app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Lambda!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
```