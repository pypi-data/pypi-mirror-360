"""
Python SDK for isend.ai

A simple Python SDK for sending emails through isend.ai using various email connectors
like AWS SES, SendGrid, Mailgun, and more.
"""

from .client import ISendClient

__version__ = "1.0.0"
__author__ = "isend.ai"
__email__ = "support@isend.ai"

__all__ = ["ISendClient"] 