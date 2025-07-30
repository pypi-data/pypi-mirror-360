import requests
import json
from .exceptions import AuthenticationError, APIError, InvalidRequestError

class DynaRouteClient:
    def __init__(self, api_key):
        if not api_key:
            raise AuthenticationError("An API key is required for authentication.")
        
        self.api_key = api_key
        self.base_url = "https://api.dynaroute.vizuara.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            
            if 'stream' in kwargs and kwargs['stream']:
                return response
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {e.response.text}")
            elif 400 <= e.response.status_code < 500:
                raise InvalidRequestError(f"Invalid request: {e.response.text}")
            else:
                raise APIError(f"API error: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

    def chat(self, messages, stream=False, **kwargs):
        """
        Sends a chat request to the DynaRoute API.

        Args:
            messages (list): A list of message dictionaries.
            stream (bool): If True, streams the response.
            **kwargs: Additional parameters for the API.

        Returns:
            dict or iterator: The API response or a stream iterator.
        """
        endpoint = "chat/completions"
        payload = {
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        response = self._make_request('post', endpoint, json=payload, stream=stream)
        
        if stream:
            def stream_generator():
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            content = decoded_line[len("data: "):]
                            if content.strip() and content != "[DONE]":
                                yield json.loads(content)
            return stream_generator()
        
        return response