"""
Tests for ISendClient
"""

import pytest
import responses
import requests
from unittest.mock import patch
from isend import ISendClient


class TestISendClient:
    """Test cases for ISendClient class"""
    
    def test_constructor_with_valid_api_key(self):
        """Test constructor with valid API key"""
        client = ISendClient("test-api-key")
        assert isinstance(client, ISendClient)
        assert client.api_key == "test-api-key"
        assert client.timeout == 30
    
    def test_constructor_with_empty_api_key(self):
        """Test constructor with empty API key raises ValueError"""
        with pytest.raises(ValueError, match="API key is required"):
            ISendClient("")
    
    def test_constructor_with_none_api_key(self):
        """Test constructor with None API key raises ValueError"""
        with pytest.raises(ValueError, match="API key is required"):
            ISendClient(None)
    
    def test_constructor_with_custom_config(self):
        """Test constructor with custom configuration"""
        config = {"timeout": 60}
        client = ISendClient("test-api-key", config)
        assert client.timeout == 60
    
    def test_send_email_method_exists(self):
        """Test that send_email method exists and has correct signature"""
        client = ISendClient("test-api-key")
        assert hasattr(client, "send_email")
        assert callable(client.send_email)
    
    @responses.activate
    def test_send_email_success(self):
        """Test successful email sending"""
        # Mock the API response
        mock_response = {"status": "success", "message_id": "12345"}
        responses.add(
            responses.POST,
            "https://www.isend.ai/api/send-email",
            json=mock_response,
            status=200
        )
        
        client = ISendClient("test-api-key")
        email_data = {
            "template_id": 124,
            "to": "test@example.com",
            "dataMapping": {"name": "Test"}
        }
        
        response = client.send_email(email_data)
        
        assert response == mock_response
        assert len(responses.calls) == 1
        assert responses.calls[0].request.headers["Authorization"] == "Bearer test-api-key"
        assert responses.calls[0].request.headers["Content-Type"] == "application/json"
        assert responses.calls[0].request.headers["User-Agent"] == "isend-ai-python-sdk/1.0.0"
    
    @responses.activate
    def test_send_email_http_error(self):
        """Test email sending with HTTP error"""
        responses.add(
            responses.POST,
            "https://www.isend.ai/api/send-email",
            json={"error": "Bad Request"},
            status=400
        )
        
        client = ISendClient("test-api-key")
        email_data = {"template_id": 124, "to": "test@example.com"}
        
        with pytest.raises(requests.exceptions.RequestException):
            client.send_email(email_data)
    
    @responses.activate
    def test_send_email_invalid_json_response(self):
        """Test email sending with invalid JSON response"""
        responses.add(
            responses.POST,
            "https://www.isend.ai/api/send-email",
            body="invalid json",
            status=200
        )
        
        client = ISendClient("test-api-key")
        email_data = {"template_id": 124, "to": "test@example.com"}
        
        with pytest.raises(ValueError, match="Invalid JSON response"):
            client.send_email(email_data)
    
    @responses.activate
    def test_send_email_network_error(self):
        """Test email sending with network error"""
        responses.add(
            responses.POST,
            "https://www.isend.ai/api/send-email",
            body=requests.exceptions.ConnectionError("Connection failed")
        )
        
        client = ISendClient("test-api-key")
        email_data = {"template_id": 124, "to": "test@example.com"}
        
        with pytest.raises(requests.exceptions.RequestException):
            client.send_email(email_data) 