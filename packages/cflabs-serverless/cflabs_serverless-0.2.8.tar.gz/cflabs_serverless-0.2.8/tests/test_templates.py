"""Unit tests for templates module."""

import pytest
from cflabs_serverless import templates


class TestTemplates:
    """Test cases for Jinja2 templates."""
    
    def test_dockerfile_template(self):
        """Test Dockerfile template rendering."""
        rendered = templates.DOCKERFILE_TEMPLATE.render(
            base_image="public.ecr.aws/lambda/python:3.11",
            working_dir="/var/task",
            port=8000,
            app_module="app",
            app_object="app"
        )
        
        assert "FROM public.ecr.aws/lambda/python:3.11" in rendered
        assert "WORKDIR /var/task" in rendered
        assert "ENV PORT=8000" in rendered
        assert "CMD [\"gunicorn\"" in rendered
        assert "app:app" in rendered
    
    def test_sam_template(self):
        """Test SAM template rendering."""
        rendered = templates.SAM_TEMPLATE.render(
            timeout=30,
            memory_size=512,
            port=8000
        )
        
        assert "AWSTemplateFormatVersion" in rendered
        assert "Transform: AWS::Serverless-2016-10-31" in rendered
        assert "Timeout: 30" in rendered
        assert "MemorySize: 512" in rendered
        assert "PORT: 8000" in rendered
        assert "AWS::Serverless::Function" in rendered
        assert "AWS::Serverless::Api" in rendered
    
    def test_config_template(self):
        """Test configuration template rendering."""
        rendered = templates.CONFIG_TEMPLATE.render(
            app_module="app",
            app_object="app",
            port=8000,
            stack_name="my-stack",
            region="us-east-1",
            memory_size=512,
            timeout=30,
            base_image="public.ecr.aws/lambda/python:3.11",
            working_dir="/var/task"
        )
        
        assert "module: app" in rendered
        assert "object: app" in rendered
        assert "port: 8000" in rendered
        assert "stack_name: my-stack" in rendered
        assert "region: us-east-1" in rendered
        assert "memory_size: 512" in rendered
        assert "timeout: 30" in rendered
    
    def test_requirements_template(self):
        """Test requirements template rendering."""
        rendered = templates.REQUIREMENTS_TEMPLATE.render()
        
        assert "Flask>=" in rendered
        assert "gunicorn>=" in rendered
        assert "# Add your other dependencies below" in rendered
    
    def test_dockerignore_template(self):
        """Test .dockerignore template rendering."""
        rendered = templates.DOCKERIGNORE_TEMPLATE.render()
        
        assert "__pycache__/" in rendered
        assert "*.py[cod]" in rendered
        assert ".env" in rendered
        assert ".git/" in rendered
        assert "cflabs-config.yaml" in rendered
        assert "template.yaml" in rendered
    
    def test_sam_config_template(self):
        """Test SAM config template rendering."""
        rendered = templates.SAM_CONFIG_TEMPLATE.render(
            stack_name="my-stack",
            account_id="123456789012",
            region="us-east-1",
            image_uri="123456789012.dkr.ecr.us-east-1.amazonaws.com/my-stack-repo:latest"
        )
        
        assert "stack_name = \"my-stack\"" in rendered
        assert "region = \"us-east-1\"" in rendered
        assert "123456789012" in rendered
        assert "my-stack-repo:latest" in rendered 