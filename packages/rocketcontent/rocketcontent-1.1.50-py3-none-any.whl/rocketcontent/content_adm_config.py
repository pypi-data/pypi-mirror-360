import requests
import logging
import urllib3
import warnings
import os
from urllib.parse import quote
from .content_config import ContentConfig

from .util import copy_file_with_timestamp, calculate_md5, verify_md5

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentAdmConfig (ContentConfig):

    def __init__(self, yaml_file):
        super().__init__(yaml_file)  # Calls the parent constructor to initialize common attributes
        self._get_initial_client_id()

    
    def _get_initial_client_id(self):
        try:
            response = requests.get(f"{self.repo_url}/repositories", headers={}, verify=False)  # Disable SSL verification for localhost
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Extract client-id from response headers
            client_id = response.headers.get("client-id")
            if client_id:
                logging.info(f"Received client-id: {client_id[:10]}...{client_id[-10:]}")
                return client_id
            else:
                logging.error("No client-id received in response")
                return None
        except requests.RequestException as e:
            logging.error(f"Error during initial request: {e}")
            return None    
    