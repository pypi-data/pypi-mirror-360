# DynaRoute API Client

This package provides a convenient Python client for interacting with the DynaRoute API, allowing you to easily integrate its chat completion features into your applications.

## Installation

Install the package directly from the source or using pip:

```bash
pip install .
```

## Usage

To get started, initialize the `DynaRouteClient` with your API key. The API endpoint is always set to `https://api.dynaroute.vizuara.com` by default.

### Basic Chat Completion

Here’s how to make a simple, non-streaming chat completion request:

```python
from dynaroute import DynaRouteClient, APIError

try:
    client = DynaRouteClient(api_key="YOUR_API_KEY")
    
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    response = client.chat(messages)
    print(response['choices'][0]['message']['content'])
    
except APIError as e:
    print(f"An API error occurred: {e}")
```

### Streaming Chat Completion

For real-time responses, you can stream the output from the API:

```python
from dynaroute import DynaRouteClient, APIError

try:
    client = DynaRouteClient(api_key="YOUR_API_KEY")
    
    messages = [
        {"role": "user", "content": "Tell me a short story."}
    ]
    
    stream = client.chat(messages, stream=True)
    
    for chunk in stream:
        content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
        if content:
            print(content, end='', flush=True)
            
except APIError as e:
    print(f"An API error occurred: {e}")
```