"""cflabs-serverless: Deploy Flask apps to AWS Lambda + API Gateway with zero code changes."""

__version__ = "0.1.4"
__author__ = "CosmicFusionLabs"
__email__ = "hello@cosmicfusionlabs.com"

from .cli import app

__all__ = ["app"] 