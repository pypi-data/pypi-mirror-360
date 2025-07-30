import json
import os
import time
import threading
from dataclasses import asdict
from queue import Queue, Empty
from typing import List, Dict, Any, Union
import requests
import re

from uspto_data.response.patent_file_wrapper import __endpoint__ as patent_fw_endpoint
from uspto_data.response.bulk_dataset import __endpoint__ as bulk_data_endpoint
from uspto_data.response.response_interface import ResponseParser

BASE_URL = "https://api.uspto.gov/api/v1/"
url_parser_mapping = patent_fw_endpoint.urls + bulk_data_endpoint.urls
defualt_api_key = os.getenv("USPTO_API_KEY", "")


def get_methods_for_endpoint(endpoint: str) -> Union[List[str], None]:
    """
    Returns the HTTP methods associated with the given endpoint.

    :param endpoint: The endpoint to search for.
    :return: A list of HTTP methods associated with the endpoint, or None if not found.
    """
    for url_pattern, methods, parser in url_parser_mapping:
        if url_pattern == endpoint:
            return methods
    return None


def get_first_method_for_endpoint(endpoint: str) -> Union[str, None]:
    methods = get_methods_for_endpoint(endpoint)
    if methods and len(methods) > 0:
        return methods[0]


class USPTOClient:
    # Example usage:
    #   client = USPTOClient(api_key="YOUR_API_KEY")
    #   client.call_api(
    #   endpoint="patent/applications/{applicationNumberText}/meta-data",
    #       url_params={"applicationNumberText": "17099900"}
    #   )
    # [Main Thread] calls call_api() ───> Adds request to queue
    # [Worker Thread] picks up request from queue
    # [Worker Thread] waits if needed (rate limiting)
    # [Worker Thread] sends API request (requests.Session.request)
    # [USPTO API] processes request & sends JSON response
    # [Worker Thread] puts response in result_queue
    # [Main Thread] retrieves response, parses it, and returns result

    def __init__(self, api_key: str, interval: float = 1.0):
        """
        Initialize the USPTOClient with your API key, parser mapping, and rate-limiting interval.

        :param api_key: Your USPTO ODP API key.
        :param interval: Minimum interval (in seconds) between API requests.
        """
        if not api_key:
            raise ValueError("An API key must be provided")

        self.BASE_URL = BASE_URL
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "X-API-KEY": self.api_key
        })
        self.parser_mapping = url_parser_mapping
        self.interval = interval
        self.queue = Queue()
        self._stop_event = threading.Event()
        self._last_request_time = 0

        # Start a worker thread to process the request queue
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def _process_queue(self):
        """Worker thread to process requests in the queue while enforcing rate-limiting."""
        while not self._stop_event.is_set():
            try:
                func, args, kwargs, result_queue = self.queue.get(timeout=0.1)
                elapsed = time.time() - self._last_request_time
                if elapsed < self.interval:
                    time.sleep(self.interval - elapsed)
                try:
                    result = func(*args, **kwargs)
                    result_queue.put(result)
                except Exception as e:
                    print(f"Error processing request: {e}")
                    result_queue.put(e)
                finally:
                    self._last_request_time = time.time()
                    self.queue.task_done()
            except Empty:
                continue

    def _enqueue_request(self, func, *args, **kwargs):
        """
        Add a request to the queue and wait for the result.

        :param func: The function to execute.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        :return: The result of the function execution.
        """
        result_queue = Queue()
        self.queue.put((func, args, kwargs, result_queue))
        result = result_queue.get()
        if isinstance(result, Exception):
            raise result
        self.queue.join()
        return result

    def _get_response_parser(self, api_url: str) -> ResponseParser:
        """
        Returns the response parser for a given API URL.

        :param api_url: The API URL to look up.
        :return: The associated response parser function or `None` if not found.
        """

        def match_url_pattern(api_url: str, url_pattern: str) -> bool:
            """Matches a given API URL to a URL pattern, handling dynamic parameters like `{param}`."""
            pattern = re.sub(r"{[^}]+}", r"[^/]+", url_pattern)  # Replace {param} with a wildcard
            return re.match(pattern, api_url) is not None

        for url_pattern, methods, parser in self.parser_mapping:
            if url_pattern == api_url:
                return parser() if callable(parser) else parser
        for url_pattern, methods, parser in self.parser_mapping:
            if match_url_pattern(api_url, url_pattern):
                return parser() if callable(parser) else parser
        return None

    def call_api(self, endpoint: str, query_params: Dict[str, Any] = None,
                 payload_data: Dict[str, Any] = None, url_params: Dict[str, str] = None,
                 method: str = None) -> Any:
        """
        Makes an API call to the given endpoint, processes the response, and parses it.
        :param endpoint: The API endpoint to call (relative to the BASE_URL).
        :param method: HTTP method (default is "GET"). Use "POST" for endpoints requiring a JSON payload.
        :param query_params: Query parameters for GET requests.
        :param payload_data: JSON body for POST requests.
        :param url_params: for filling out the endpoint when dynamic endpoint
        :return: Parsed response object.
        """
        if not self.api_key:
            self.api_key = os.getenv("USPTO_API_KEY", "")
        if not method and query_params:
            method = "GET"
        elif not method and payload_data:
            method = "POST"
        elif not method:
            method = get_first_method_for_endpoint(endpoint)
        if method == "GET" and payload_data:
            raise ValueError("`payload_data` cannot be used with GET requests")
        if method == "POST" and query_params:
            raise ValueError("`query_params` cannot be used with POST requests")
        if not method:
            method = "POST"
        response_parser = self._get_response_parser(endpoint)
        if url_params:
            endpoint = endpoint.format(**url_params)
        if "{" in endpoint or "}" in endpoint:
            raise ValueError("Invalid endpoint for call: '{' or '}' in endpoint string. If there is a dynamic endpoint,"
                             " include dictionary 'query_params' in fn call_api with value for each placeholder set.")
        url = f"{self.BASE_URL}{endpoint}"
        if not response_parser:
            raise ValueError(f"No parser available for the endpoint: {endpoint}")

        response = self._enqueue_request(self.session.request, method, url, params=query_params, json=payload_data)
        response.raise_for_status()
        json_response = response.json()
        return response_parser.parse_response(json_response)

    def get_file(self, file_url: str, save_path: str, url_params: dict = None, allow_redirects: bool = True, headers: dict = None) -> str:
        """
        Downloads a file from the given URL and saves it to the specified path.

        :param file_url: The URL to fetch the file from.
        :param save_path: The path where the file should be saved.
        """
        try:
            # Send GET request to fetch the file
            if not file_url.startswith("http"):
                file_url = BASE_URL + file_url
            if url_params:
                file_url = file_url.format(**url_params)
            response = self._enqueue_request(self.session.request, "GET", file_url, allow_redirects=allow_redirects, stream=True, headers=headers)
            response.raise_for_status()  # Raise exception for bad responses (4xx, 5xx)
            save_dir = os.path.dirname(save_path)
            os.makedirs(save_dir, exist_ok=True)
            # Write the file content to the specified path
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            print(f"File successfully downloaded and saved to {save_path}")
            return save_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading the file: {e}")


    def stop(self):
        """Stop the worker thread gracefully."""
        self._stop_event.set()
        self._worker_thread.join()


# Example usage
if __name__ == "__main__":

    # Initialize the USPTOClient with your API key and endpoint mappings
    api_key = ""
    client = USPTOClient(api_key=api_key)

    try:
        # Call an API and parse the response
        endpoint = "patent/applications/{applicationNumberText}/meta-data"
        url_params = {"applicationNumberText": "17099900"}
        parsed_response = client.call_api(endpoint, url_params=url_params)
        print(json.dumps(asdict(parsed_response), indent=2))
    finally:
        client.stop()


def get_default_client() -> USPTOClient:
    return USPTOClient(api_key=defualt_api_key)
