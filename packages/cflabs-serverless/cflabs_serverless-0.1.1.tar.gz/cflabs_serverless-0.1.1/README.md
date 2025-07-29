# cflabs-serverless

Deploy Flask apps to AWS Lambda + API Gateway with **zero code changes**.

## 🚀 Features

- **Zero-touch deployment**: Your Flask app stays unchanged
- **Single command deployment**: `cflabs-serverless deploy`
- **AWS Lambda Web Adapter**: Runs Gunicorn inside Lambda containers
- **Automatic scaffolding**: Generates Dockerfile and SAM template
- **Simple CLI**: Intuitive commands for the full deployment lifecycle

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

**Examples:**
```bash
# Deploy with default settings (will prompt for function name)
cflabs-serverless deploy

# Deploy with custom name and region
cflabs-serverless deploy --name my-awesome-app --region us-west-2

# Deploy with custom configuration
cflabs-serverless deploy --name my-app --memory 1024 --timeout 60
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
└── cflabs-config.yaml    # Configuration file
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

container:
  base_image: public.ecr.aws/lambda/python:3.11
  working_dir: /var/task
```

## 🔍 How It Works

1. **AWS Lambda Web Adapter**: Uses the binary at `/lambda-adapter` to handle HTTP requests
2. **Gunicorn**: Runs your Flask app with Gunicorn inside the Lambda container
3. **Zero Code Changes**: Your Flask app runs exactly as it does locally
4. **SAM Template**: Automatically generated with proper API Gateway integration

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