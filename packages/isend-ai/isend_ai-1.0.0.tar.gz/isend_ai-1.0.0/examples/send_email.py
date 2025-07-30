#!/usr/bin/env python3
"""
Example: Send email using isend.ai Python SDK

This example demonstrates how to use the ISendClient to send emails
using templates and data mapping.
"""

from isend import ISendClient


def main():
    """Main function demonstrating email sending"""
    
    # Initialize the client with your API key
    client = ISendClient("your-api-key-here")
    
    # Example: Send email using template
    try:
        email_data = {
            "template_id": 124,
            "to": "hi@isend.ai",
            "dataMapping": {
                "name": "ISend"
            }
        }
        
        response = client.send_email(email_data)
        
        print("Email sent successfully!")
        print("Response:", response)
        
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    main() 