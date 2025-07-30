# ragagent-client

Python client for the Ragagent API.

## Installation

```bash
pip install ragagent-client
```

## Usage

```python
import ragagent_client
from ragagent_client.rest import ApiException

# Configure the client
configuration = ragagent_client.Configuration(
    host="https://your-ragagent-instance.com"
)

# Create API client
with ragagent_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ragagent_client.DefaultApi(api_client)
    
    try:
        # Health check endpoint
        api_response = api_instance.health_health_get()
        print("Health check response:", api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->health_health_get: %s\n" % e)
```

## Requirements

- Python >= 3.9

## Development

### Setup

```bash
# Install in development mode
pip install -e .

# Install test dependencies
pip install -r test-requirements.txt
```

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy ragagent_client
```

### Linting

```bash
flake8 ragagent_client
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

See [LICENSE](LICENSE) file for details.
