"""Unit tests for utils module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from cflabs_serverless import utils


class TestUtils:
    """Test cases for utility functions."""
    
    def test_get_project_root(self):
        """Test getting project root directory."""
        root = utils.get_project_root()
        assert isinstance(root, Path)
        assert root.exists()
    
    def test_detect_flask_app_success(self, tmp_path):
        """Test detecting Flask app when app.py exists."""
        with patch('cflabs_serverless.utils.get_project_root') as mock_root:
            mock_root.return_value = tmp_path
            
            # Create app.py
            app_file = tmp_path / "app.py"
            app_file.write_text("# Flask app")
            
            module, obj = utils.detect_flask_app()
            assert module == "app"
            assert obj == "app"
    
    def test_detect_flask_app_not_found(self, tmp_path):
        """Test detecting Flask app when app.py doesn't exist."""
        with patch('cflabs_serverless.utils.get_project_root') as mock_root:
            mock_root.return_value = tmp_path
            
            with pytest.raises(FileNotFoundError, match="app.py not found"):
                utils.detect_flask_app()
    
    def test_load_config_success(self, tmp_path):
        """Test loading configuration from YAML file."""
        config_file = tmp_path / "cflabs-config.yaml"
        config_content = """
app:
  module: app
  object: app
  port: 8000
deployment:
  stack_name: test-stack
  region: us-east-1
"""
        config_file.write_text(config_content)
        
        with patch('cflabs_serverless.utils.get_project_root') as mock_root:
            mock_root.return_value = tmp_path
            
            config = utils.load_config()
            assert config["app"]["module"] == "app"
            assert config["app"]["object"] == "app"
            assert config["app"]["port"] == 8000
            assert config["deployment"]["stack_name"] == "test-stack"
    
    def test_load_config_file_not_found(self, tmp_path):
        """Test loading configuration when file doesn't exist."""
        with patch('cflabs_serverless.utils.get_project_root') as mock_root:
            mock_root.return_value = tmp_path
            
            with pytest.raises(FileNotFoundError):
                utils.load_config()
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to YAML file."""
        config = {
            "app": {"module": "app", "object": "app"},
            "deployment": {"stack_name": "test-stack"}
        }
        
        with patch('cflabs_serverless.utils.get_project_root') as mock_root:
            mock_root.return_value = tmp_path
            
            utils.save_config(config)
            
            config_file = tmp_path / "cflabs-config.yaml"
            assert config_file.exists()
            
            # Verify content
            loaded_config = utils.load_config()
            assert loaded_config == config
    
    def test_get_ecr_repository_name(self):
        """Test generating ECR repository name."""
        repo_name = utils.get_ecr_repository_name("my-stack")
        assert repo_name == "my-stack-repo"
    
    def test_format_duration(self):
        """Test formatting duration in seconds."""
        assert utils.format_duration(30) == "30s"
        assert utils.format_duration(90) == "1m 30s"
        assert utils.format_duration(3661) == "1h 1m"
    
    @patch('cflabs_serverless.utils.run_command')
    def test_check_prerequisites_all_installed(self, mock_run):
        """Test prerequisites check when all tools are installed."""
        mock_run.return_value = MagicMock()
        
        result = utils.check_prerequisites()
        assert result is True
    
    @patch('cflabs_serverless.utils.run_command')
    def test_check_prerequisites_missing_tools(self, mock_run):
        """Test prerequisites check when tools are missing."""
        mock_run.side_effect = FileNotFoundError()
        
        result = utils.check_prerequisites()
        assert result is False
    
    @patch('boto3.client')
    def test_get_aws_account_id_success(self, mock_boto3):
        """Test getting AWS account ID successfully."""
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.return_value = {'Account': '123456789012'}
        mock_boto3.return_value = mock_sts
        
        account_id = utils.get_aws_account_id()
        assert account_id == '123456789012'
    
    @patch('boto3.client')
    def test_get_aws_account_id_failure(self, mock_boto3):
        """Test getting AWS account ID when it fails."""
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.side_effect = Exception("AWS error")
        mock_boto3.return_value = mock_sts
        
        with pytest.raises(Exception):
            utils.get_aws_account_id() 