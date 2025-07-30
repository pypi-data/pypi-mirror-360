import json
from pathlib import Path
import requests
import urllib3
import warnings
import os
from typing import List, Dict, Any, Optional
from copy import deepcopy
from .content_config import ContentConfig
from urllib.parse import quote
import time
import datetime
from rocketcontent.util import validate_id

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


class Topic:
    id: str
    name: str
    details: str
    topicVersionDisplay: str
    allowAccess: bool
    dataType: str
    maxLength: str
    category: str
    enableIndex: bool

    def __init__(self, id: str, name: str, dataType: str = "Character", maxLength: str = "30"):

        if dataType not in ["Character", "Date", "Number"]:
            raise ValueError("dataType must be one of 'Character', 'Date', or 'Number'.")
        
        if maxLength not in ["30", "255"]:
            raise ValueError("maxLength must be one of '30', or '255'.")

        if not validate_id(id):
            raise ValueError(f"Invalid ID: {id}. ID must be alphanumeric and can include underscores.")

        if len(id) > 10:
            raise ValueError(f"ID lenght must be less than 10. Current length: {len(id)}")
          
        self.id = id
        self.name = name
        self.details = name
        self.dataType = dataType
        self.maxLength = maxLength
        self.topicVersionDisplay = "All"
        self.allowAccess = True
        self.category = "Document metadata"
        self.enableIndex = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':
        """Create a Topic instance from a dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            details=data.get("details", ""),
            dataType=data.get("dataType", "Character"),
            maxLength=data.get("maxLength", "30")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "details": self.details,
            "topicVersionDisplay": self.topicVersionDisplay,
            "allowAccess": self.allowAccess,
            "dataType": self.dataType,
            "maxLength": self.maxLength,
            "category": self.category,
            "enableIndex": self.enableIndex
        }


class IndexGroup:
    id: str
    name: str
    scope: str
    topics: List[Topic]

    def __init__(self, id: str, name: str):

        if not validate_id(id):
            raise ValueError(f"Invalid ID: {id}. ID must be alphanumeric and can include underscores.")

        if len(id) > 10:
            raise ValueError(f"ID lenght must be less than 10. Current length: {len(id)}")
                  
        self.id = id
        self.name = name
        self.scope = "Page"
        self.topics = []

    def addTopic(self, topic: Topic) -> None:
        """Add a Topic object to the topics list."""
        self.topics.append(topic)

    @classmethod
    def from_json(cls, json_str: str) -> 'IndexGroup':
        """Create an IndexGroup instance from a JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {str(e)}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndexGroup':
        """Create an IndexGroup instance from a dictionary."""
        id = data.get("id", "")

        if not validate_id(id):
            raise ValueError(f"Invalid ID: {id}. ID must be alphanumeric and can include underscores.")

        if len(id) > 10:
            raise ValueError(f"ID lenght must be less than 10. Current length: {len(id)}")

        index_group = cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            scope=data.get("scope", "Page")
        )
        for topic_data in data.get("topics", []):
            index_group.addTopic(Topic.from_dict(topic_data))
        return index_group

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.scope,
            "topics": [topic.to_dict() for topic in self.topics]
        }
    
class ContentAdmIndexGroup:
    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_admin_url = content_config.repo_admin_url
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
        else:
            raise TypeError("ContentConfig class object expected")


    #--------------------------------------------------------------
    # Extract Index Groups from JSON
    # This method extracts topic group objects from a JSON structure and saves them to a file
    def extract_index_groups(self, json_data, output_dir="output") -> Optional[str]:
        """
        Extracts topic group objects from a JSON structure and saves them to a file
        with a timestamp in the filename.
        
        Args:
            json_data (dict): JSON object containing 'items' with topic group data
            output_dir (str): Directory where the output file will be saved
            
        Returns:
            str: Path to the saved file
        """
        
        # Generate timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"index_groups_{timestamp}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        # Extract topic groups
        if not isinstance(json_data, dict) or 'items' not in json_data:
           raise ValueError("Invalid JSON data: 'items' key not found or JSON is not a dictionary")
        
        result = []
        for item in json_data['items']:
            topic_group = {
                'id': item.get('id', ''),
                'name': item.get('name', ''),
                'scope': item.get('scope', ''),
                'topics': item.get('topics', [])
            }
            result.append(topic_group)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(result, file, indent=2)
        
        return output_path

    #--------------------------------------------------------------
    # Verify if Index Group definition exists
    # This method checks if a index group with the specified id exists.
    # It returns True if the index group exists, otherwise returns False.
    # If an error occurs during the request or JSON parsing, it logs the error and returns False.
    def verify_index_group(self, ig_id) -> bool:
        """
        Verifies if a index group the specified name exists by querying the admin reports API.
        Args:
            ig_id (str): The ID of the index group to verify.
        Returns:
            bool: True if an item with the given ID exists in the response, False otherwise.
        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            json.JSONDecodeError: If the response cannot be parsed as JSON.
        Logs:
            - Method name, request URL, and headers for debugging purposes.
        """
        try:
            local_headers = deepcopy(self.headers)
            local_headers['Accept'] = 'application/vnd.asg-mobius-admin-topic-groups.v1+json'

            tm = str(int(time.time() * 1000))
            index_group_get_url = self.repo_admin_url + f"/topicgroups?limit=5&&groupid={ig_id}&timestamp={tm}"

            self.logger.info("--------------------------------")
            self.logger.info("Method : verify_index_group")
            self.logger.debug(f"URL : {index_group_get_url}")
            self.logger.debug(f"Headers : {json.dumps(local_headers)}")
                         
            # Send the request
            response = requests.get(index_group_get_url, headers=local_headers, verify=False)
            
            # Check if the HTTP request was successful
            response.raise_for_status()
            
            # Parse JSON from response
            data = response.json()
          
            # Get items list, default to empty list if not found
            items = data.get("items", [])
            
            # Check each item for id == "AAA01"
            for item in items:
                if item.get("id") == ig_id:
                    return True
            return False
        
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False       
        
    #--------------------------------------------------------------
    # Create Index Group Definition
    def create_index_group(self, index_group: IndexGroup) -> int:
        """
        Creates a new index group by sending a POST request to the repository admin API.
        Args:
            index_group_json (dict): The JSON payload containing the index group definition.
        Returns:
            int: The HTTP status code returned by the API.
        Logs:
            - Method entry and exit points.
            - Request URL, headers, and body.
            - Response text.
            - Errors encountered during the process.
        Raises:
            Logs any exceptions that occur during the request.
        """
        try:

            if self.verify_index_group(index_group.id):
                self.logger.error(f"Index Group with name '{index_group.id}' already exists.")
                return 409
               
            index_group_definition_url= self.repo_admin_url + "/topicgroups"
    
            self.headers['Content-Type'] = 'application/vnd.asg-mobius-admin-topic-group.v1+json'
            self.headers['Accept'] = 'application/vnd.asg-mobius-admin-topic-group.v1+json'

            self.logger.info("--------------------------------")
            self.logger.info("Method : create_index_group")
            self.logger.debug(f"URL : {index_group_definition_url}")
            self.logger.debug(f"Headers : {json.dumps(self.headers)}")
            self.logger.debug(f"Payload : {json.dumps(index_group.to_dict(),indent=2)}")
               
            # Send the request
            response = requests.post(index_group_definition_url, headers=self.headers, json=index_group.to_dict(), verify=False)
            
            json_data = response.json()
            if 'tableName' in json_data and json_data['tableName'].strip() != '':
                self.logger.info(f"Index Group '{index_group.id}' created successfully with table name: {json_data['tableName']}")
                return response.status_code
            else:
                self.logger.error(f"Failed to create Index Group '{index_group.id}'. Response: {json_data}")
                return 409
        
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    #--------------------------------------------------------------    
    # Export Index Group Definitions
    # This method exports the index groups definitions to a file.
    # It retrieves the index group by its id, extracts the topics, and saves them to a JSON file.
    # If an error occurs during the request or JSON parsing, it logs the error and returns False.
    def export_index_groups(self, ig_id, output_dir) -> Optional[str]:
        """
        Export to a file the index groups filtered by ig_id.
        Args:
            ig_id (str): The ID (or part) of the index group.
        Returns:
            filename: generated.
        Raises:
            requests.HTTPError: If the HTTP request to the API fails.
            json.JSONDecodeError: If the response cannot be parsed as JSON.
            FileNotFoundError: If the output directory does not exist
            ValueError: if the JSON data is invalid.
        Logs:
            - Method name, request URL, and headers for debugging purposes.
        """
        try:
            # Check if output directory exists
            if not os.path.exists(output_dir):
                raise FileNotFoundError(f"Output directory '{output_dir}' does not exist")

            local_headers = deepcopy(self.headers)
            local_headers['Accept'] = 'application/vnd.asg-mobius-admin-topic-groups.v1+json'

            tm = str(int(time.time() * 1000))
            index_group_get_url = self.repo_admin_url + f"/topicgroups?limit=200&&groupid={ig_id}*&timestamp={tm}"

            self.logger.info("--------------------------------")
            self.logger.info("Method : export_index_groups")
            self.logger.debug(f"URL : {index_group_get_url}")
            self.logger.debug(f"Headers : {json.dumps(local_headers)}")
                         
            # Send the request
            response = requests.get(index_group_get_url, headers=local_headers, verify=False)
            
            # Check if the HTTP request was successful
            response.raise_for_status()
            
            # Parse JSON from response
            data = response.json()

            saved_file = self.extract_index_groups(data, output_dir=output_dir)
        
            self.logger.info(f"Data saved to: {saved_file}")

            return saved_file
    
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error occurred: {e}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON: {e}")
            return False
        except FileNotFoundError as e:
            self.logger.error(f"Directory error: {e}")
            return False
        except ValueError as e:
            self.logger.error(f"Data error: {e}")
            return False
        
    #--------------------------------------------------------------
    # Import Index Group Definition
    def import_index_group(self, index_group_json) -> int:
        """
        Imports an index group from a JSON object.
        This method attempts to create a new index group in the repository by sending a POST request
        with the provided JSON data. If an index group with the same ID already exists, it logs an error
        and returns a 409 status code. Otherwise, it sends the request to the repository admin URL and
        returns the HTTP status code from the response.
        Args:
            index_group_json (dict): The JSON object representing the index group to import.
        Returns:
            int: The HTTP status code resulting from the import operation. Returns 409 if the index group
                 already exists, or the status code from the POST request otherwise.
        Logs:
            - Information and debug logs for the request details and response.
            - Error logs if the index group already exists or if an exception occurs.
        """

        try:
            if isinstance(index_group_json, str):
                index_group = IndexGroup.from_json(index_group_json)
            elif isinstance(index_group_json, dict):
                index_group = IndexGroup.from_dict(index_group_json)
            else:
                raise ValueError("index_group_json must be a string or dictionary")

            if self.verify_index_group(index_group.id):
                self.logger.error(f"Index Group with name '{index_group.id}' already exists.")
                return 409
               
            index_group_definition_url= self.repo_admin_url + "/topicgroups"
    
            self.headers['Content-Type'] = 'application/vnd.asg-mobius-admin-topic-group.v1+json'
            self.headers['Accept'] = 'application/vnd.asg-mobius-admin-topic-group.v1+json'

            self.logger.info("--------------------------------")
            self.logger.info("Method : import_index_group")
            self.logger.debug(f"URL : {index_group_definition_url}")
            self.logger.debug(f"Headers : {json.dumps(self.headers)}")
            self.logger.debug(f"Payload : {json.dumps(index_group.to_dict(),indent=2)}")
               
            # Send the request
            response = requests.post(index_group_definition_url, headers=self.headers, json=index_group.to_dict(), verify=False)

            if response.status_code != 201:
                self.logger.error(f"Failed to import index '{index_group.id}'. Response: {response.text}")
                return response.status_code 
            else:
                json_data = response.json()
                if 'tableName' in json_data and json_data['tableName'].strip() != '':
                    self.logger.info(f"Index Group '{index_group.id}' created successfully with table name: {json_data['tableName']}")
                else:
                    self.logger.error(f"Failed to create Index Group '{index_group.id}'. Response: {json_data}")
                    return 409
            self.logger.info(f"Response: {response.status_code} - Index Group '{index_group.id}' imported successfully.")
            return response.status_code
        
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")        

    #--------------------------------------------------------------
    # Import Index Groups from file
    def import_index_groups(self, file_path: str) -> None:
        """
        Imports index groups from a JSON file.
        Args:
            file_path (str): The path to the JSON file containing an array of index group objects.
        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file does not contain a JSON array.
        The method reads the specified JSON file, validates that it contains a list of index group objects,
        and imports each index group by calling `self.import_index_group`. Errors encountered during the process
        are logged using the class logger.
        """

        if not Path(file_path).exists():
            raise FileNotFoundError(f"Error: File '{file_path}' does not exist")

        try:
            with open(file_path, 'r') as file:
                json_array = json.load(file)

                if not isinstance(json_array, list):
                    raise ValueError("Error: File does not contain a JSON array")
                    
                for index, index_group_json_obj in enumerate(json_array):
                    self.import_index_group(index_group_json_obj)

        except FileNotFoundError:
            self.logger.error(f"Error: File '{file_path}' not found")
        except json.JSONDecodeError:
            self.logger.error("Error: Invalid JSON format in file")
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")                