import json
import requests
import urllib3
import warnings
from copy import deepcopy

from .content_config import ContentConfig

from urllib.parse import quote

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentRepository:
    
    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_url = content_config.repo_url
            self.repo_id = content_config.repo_id
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
        else:
            raise TypeError("ContentConfig class object expected")


    def get_content_classes(self, output_file="content_classes.json"):
        """
        Retrieves the content classes from the Mobius server and saves them to a JSON file.

        Args:
            output_file (str, optional): Output file name. Defaults to "content_classes.json".
        """
        # Make the GET request
        content_classes_url= self.repo_url + "/repositories/" + self.repo_id + "/recordtypes" 
         
        self.logger.info("--------------------------------")
        self.logger.info("Method : get_content_classes")
        self.logger.debug(f"URL : {content_classes_url}")
        self.logger.debug(f"File : {output_file}")

        return self.__get_cc_inx(content_classes_url, output_file)


    def get_indexes(self, output_file="index.json"):
        """
        Retrieves the index from the Mobius server and saves them to a JSON file.

        Args:
            output_file (str, optional): Output file name. Defaults to "index.json".
        """    
        indexes_url= self.repo_url + "/indexes?repositoryid=" + self.repo_id

        self.logger.info("--------------------------------")
        self.logger.info("Method : get_indexes")
        self.logger.debug(f"URL : {indexes_url}")
        self.logger.debug(f"File : {output_file}")

        return self.__get_cc_inx(indexes_url, output_file)

    def __get_cc_inx(self, url, output_file="content_classes.json", verify_ssl=False):
        """
        Performs a GET request to the provided URL and saves the JSON response to a file.

        Args:
            url (str): The URL to perform the GET request.
            output_file (str, optional): Output file name. Defaults to "content_classes.json".
            verify_ssl (bool, optional): Verify SSL certificate. Defaults to True.
        """
        try:
            response = requests.get(url, headers=self.headers, verify=False)  # Make a GET request to the specified URL
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()  # Parse the JSON response

            # Parse the JSON response
            data = response.json()

            # Save the JSON data to the output file
            with open(output_file, "w") as file:
                json.dump(data, file, indent=2)

        except requests.exceptions.RequestException as e:
            # Handle request exceptions
            self.logger.error(f"Doing the request: {e}")
        except json.JSONDecodeError:
            # Handle JSON decoding errors
            self.logger.error("Invalid JSON response.")
        except Exception as e:
            # Handle any other unexpected errors
            self.logger.error(f"An unexpected error occurred: {e}")         
