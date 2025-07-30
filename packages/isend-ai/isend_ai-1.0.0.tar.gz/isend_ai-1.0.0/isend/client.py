"""
ISendClient - Main client class for the isend.ai Python SDK
"""

import json
from typing import Dict, Any, Optional
import requests


class ISendClient:
    """
    Simple Python SDK for isend.ai
    
    This client provides methods to send emails through isend.ai using various
    email connectors like AWS SES, SendGrid, Mailgun, and more.
    """
    
    API_BASE_URL = "https://www.isend.ai/api"
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a new ISendClient instance
        
        Args:
            api_key: Your isend.ai API key
            config: Additional configuration options (timeout, etc.)
            
        Raises:
            ValueError: If API key is empty or None
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.timeout = config.get("timeout", 30) if config else 30
        
    def send_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an email using isend.ai
        
        Args:
            email_data: Email data including template_id, to, dataMapping, etc.
            
        Returns:
            Response from the API
            
        Raises:
            requests.RequestException: For network or HTTP errors
            ValueError: For invalid JSON responses
        """
        url = f"{self.API_BASE_URL}/send-email"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "isend-ai-python-sdk/1.0.0"
        }
        
        try:
            response = requests.post(
                url,
                json=email_data,
                headers=headers,
                timeout=self.timeout
            )
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"HTTP error: {e.response.status_code if hasattr(e, 'response') and e.response else 'Unknown'} - {str(e)}"
            ) from e
        
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}") from e 