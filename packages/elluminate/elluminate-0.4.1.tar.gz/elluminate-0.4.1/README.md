# Elluminate SDK

Elluminate SDK is a Software Development Kit that provides a convenient way to interact with the Elluminate platform programmatically. It enables developers to evaluate and optimize prompts, manage experiments, and integrate Elluminate's powerful evaluation capabilities directly into their applications.

## Installation

Install the Elluminate SDK using pip:

```bash
pip install elluminate
```

## 📚 Full Documentation

The full documentation of Elluminate including the SDK can be found at: <https://docs.elluminate.de/>

## Quick Start

### Prerequisites

Before you begin, you'll need to set up your API key:

1. Visit your project's "Keys" dashboard to create a new API key
2. Export your API key and service address as environment variables:

```bash
export ELLUMINATE_API_KEY=<your_api_key>
export ELLUMINATE_BASE_URL=<your_elluminate_service_address>
```

Never commit your API key to version control. For detailed information about API key management and security best practices, see our [API Key Management Guide](https://docs.elluminate.de/get_started/api_keys/).

### Basic Usage

Here's a simple example to evaluate your first prompt:

```python
from elluminate import Client

# Initialize the client
client = Client()

# Create a prompt template
template = client.create_prompt_template(
    "Explain the concept of {{concept}} in simple terms."
)

# Generate evaluation criteria
criteria = client.generate_criteria(template)

# Create and evaluate a response
response = client.create_response(
    template=template,
    variables={"concept": "recursion"}
)

# Get the evaluation results
ratings = client.evaluate_response(response, criteria)
```

### Alternative Client Initialization

You can also initialize the client by directly passing the API key and/or base url:

```python
client = Client(api_key="your-api-key", base_url="your-base-url")
```

## Advanced Features

### Working with Collections

For more complex use cases, refer to our example with collections:

```python
from elluminate import Client

client = Client()

# Create a collection of related prompts
collection = client.create_collection("Math Teaching Prompts")

# Add multiple templates to the collection
templates = [
    client.create_prompt_template(
        "Explain {{math_concept}} to a {{grade_level}} student",
        collection=collection
    ),
    client.create_prompt_template(
        "Provide practice problems for {{math_concept}}",
        collection=collection
    )
]

# Generate and evaluate responses for multiple templates
for template in templates:
    criteria = client.generate_criteria(template)
    response = client.create_response(
        template=template,
        variables={
            "math_concept": "fractions",
            "grade_level": "5th grade"
        }
    )
    ratings = client.evaluate_response(response, criteria)
```

## Additional Resources

- [General Documentation](https://docs.elluminate.de/)
- [Key Concepts Guide](https://docs.elluminate.de/get_started/key_concepts/)
- [API Documentation](https://docs.elluminate.de/elluminate/client/)
