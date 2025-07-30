# isend.ai Python SDK

A simple Python SDK for sending emails through isend.ai using various email connectors like AWS SES, SendGrid, Mailgun, and more.

## Installation

### Using pip

```bash
pip install isend-ai
```

### From source

```bash
git clone https://github.com/isend-ai/python-sdk.git
cd python-sdk
pip install -e .
```

## Quick Start

```python
from isend import ISendClient

# Initialize the client
client = ISendClient('your-api-key-here')

# Send email using template
email_data = {
    'template_id': 124,
    'to': 'hi@isend.ai',
    'dataMapping': {
        'name': 'ISend'
    }
}

response = client.send_email(email_data)
print(response)
```

## Usage

### Send Email Using Template

```python
from isend import ISendClient

client = ISendClient('your-api-key-here')

email_data = {
    'template_id': 124,
    'to': 'hi@isend.ai',
    'dataMapping': {
        'name': 'ISend'
    }
}

response = client.send_email(email_data)
```

### Custom Configuration

```python
from isend import ISendClient

# Initialize with custom timeout
client = ISendClient('your-api-key-here', config={'timeout': 60})

email_data = {
    'template_id': 124,
    'to': 'hi@isend.ai',
    'dataMapping': {
        'name': 'ISend'
    }
}

response = client.send_email(email_data)
```

## API Reference

### ISendClient

#### Constructor
```python
ISendClient(api_key: str, config: Optional[Dict[str, Any]] = None)
```

**Parameters:**
- `api_key` (str): Your isend.ai API key
- `config` (dict, optional): Additional configuration options
  - `timeout` (int): Request timeout in seconds (default: 30)

#### Methods

##### send_email(email_data: Dict[str, Any]) -> Dict[str, Any]
Sends an email using the provided template and data.

**Parameters:**
- `email_data` (dict): Email data including:
  - `template_id` (int): The template ID to use
  - `to` (str): Recipient email address
  - `dataMapping` (dict): Data mapping for template variables

**Returns:**
- `dict`: Response from the API

## Error Handling

The SDK raises exceptions for any errors:

```python
from isend import ISendClient
import requests

try:
    client = ISendClient('your-api-key-here')
    response = client.send_email({
        'template_id': 124,
        'to': 'hi@isend.ai',
        'dataMapping': {
            'name': 'ISend'
        }
    })
    print("Email sent successfully!")
    print(response)
except ValueError as e:
    print(f"Validation error: {e}")
except requests.RequestException as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Examples

See the `examples/` directory for complete usage examples.

## Development

### Setup Development Environment

```bash
git clone https://github.com/isend-ai/python-sdk.git
cd python-sdk
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=isend

# Run tests with verbose output
pytest -v
```

### Code Formatting

```bash
# Format code with black
black .

# Check code style with flake8
flake8 .

# Type checking with mypy
mypy .
```

## Requirements

- Python 3.6 or higher
- requests library

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## Support

For support, email support@isend.ai or create an issue on GitHub.
