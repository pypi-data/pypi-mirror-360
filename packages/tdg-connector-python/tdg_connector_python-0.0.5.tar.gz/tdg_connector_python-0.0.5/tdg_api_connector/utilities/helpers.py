import json
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_data(base_url: str, endpoint: str, headers: dict, request_type: str = 'GET', params: dict = {}, payload: dict = {}) -> dict:
    """
    A function that extracts data uniformly for all endpoints, with custom
    configuration passed to them.

    Parameters:
    - endpoint (str): The endpoint to send the request to.
    - request_type (str): The type of request to send (default is 'GET').
    - params (dict): Additional parameters to include in the request 
      (default is an empty dictionary).
    - payload (dict): Data payload to send with the request (default is an empty dictionary).

    Attributes:
    - BASE_URL: A class variable to store the base URL.
    - headers (dict): Stores the API key in the form of a dictionary.
    
    Returns:
    - dict: The response data received from the request.
    """

    url = ''.join([base_url, endpoint])
    session = requests.Session()
    retries = Retry(total=3,
                    backoff_factor=0.1,
                    status_forcelist=[502, 503, 504, 404, 400, 429])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    try:
        response = session.request(
            url=url,
            method=request_type,
            headers=headers,
            params=params,
            data=json.dumps(payload)
        )

        logger.info(f"Request sent to {url} with status code {response.status_code}")

        try:
            response.raise_for_status()
        except Exception:
            logger.error(f"Error: {response.text}")
            return eval(response.text)['message']

        if response.status_code == 204:
            logger.info('No Content')
            return {}
        return response.json()

    except requests.exceptions.ConnectionError:
        logger.error("Error Occured, You're not connected with internet")
        raise Exception("Error Occured, You're not connected with internet")


def get_all_keys(data):
    """
    Recursively iterates through a nested dictionary to retrieve all keys.
    """
    keys = []
    if isinstance(data, dict):
        for key, value in data.items():
            keys.append(key)
            keys.extend(get_all_keys(value))
    keys.sort()
    return keys

