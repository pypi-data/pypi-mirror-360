import json
import base64
import requests
from pathlib import Path
from copy import deepcopy

from .content_config import ContentConfig

class ContentArchivePolicyPlus:

    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_url = content_config.repo_url
            self.repo_id = content_config.repo_id
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
			
			# Constants for Content-Type and boundary strings
            self.METADATA_CONTENT_TYPE = "application/vnd.asg-mobius-archive-write-policy.v2+json"
            self.TXT_FILE_CONTENT_TYPE = "archive/file" # Or the specific MIME type for TXT
            self.PDF_FILE_CONTENT_TYPE = "application/pdf"
            self.DEFAULT_STR_CONTENT_TYPE = "archive/file" # Default type for string content
            self.BOUNDARY_STRING = "boundaryString"			
        else:
            raise TypeError("ContentConfig class object expected")

    #--------------------------------------------------------------
    # Helper function to get the uppercase file extension
    def _get_uppercase_extension(self, file_path):
        """Gets the file extension and returns it in uppercase."""
        return Path(file_path).suffix[1:].upper() if Path(file_path).suffix else ""

    #--------------------------------------------------------------
    # Helper function to read file content
    def _read_file_content(self, file_path, file_type):
        """
        Reads file content based on its type and returns the content,
        Content-Type, and Content-Transfer-Encoding (if applicable).
        """
        if file_type in ["TXT", "SYS", "LOG"]:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), self.TXT_FILE_CONTENT_TYPE, None
        elif file_type == "PDF":
            with open(file_path, "rb") as f:
                encoded_content = base64.b64encode(f.read()).decode("utf-8")
                return encoded_content, self.PDF_FILE_CONTENT_TYPE, "base64"
        else:
            self.logger.error(f"Invalid file extension: '{file_path}'. Only PDF and TXT are allowed.")
            raise ValueError(f"Invalid file extension: '{file_path}'. Only PDF and TXT are allowed.")

    #--------------------------------------------------------------
    # Archive based on policy
    def archive_policy(self, file_path, policy_name):
        """
        Archives a file (TXT or PDF) based on a specific policy.

        Args:
            file_path (str): Path to the file to archive.
            policy_name (str): Name of the archiving policy to apply.

        Returns:
            tuple: (status_code, response_text) from the HTTP request.
        """
        file_type = self._get_uppercase_extension(file_path)

        metadata_json = {
            "objects": [
                {
                    "policies": [f"{policy_name}"]
                }
            ]
        }
        metadata_str = json.dumps(metadata_json, indent=4)

        try:
            file_content, content_type_header, transfer_encoding_header = self._read_file_content(file_path, file_type)

            body_parts = [
                f"--{self.BOUNDARY_STRING}",
                f"Content-Type: {self.METADATA_CONTENT_TYPE}",
                "",
                metadata_str,
                f"--{self.BOUNDARY_STRING}",
                f"Content-Type: {content_type_header}",
            ]
            if transfer_encoding_header:
                body_parts.append(f"Content-Transfer-Encoding: {transfer_encoding_header}")
            body_parts.extend([
                "",
                file_content,
                "",
                f"--{self.BOUNDARY_STRING}--",
            ])

            body = "\n".join(body_parts)

        except FileNotFoundError:
            self.logger.error(f"File not found: '{file_path}'.")
            raise
        except ValueError as e: # Catches the invalid extension error from _read_file_content
            self.logger.error(f"Error reading file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error preparing file for archiving: {e}")
            raise ValueError(f"Error processing file: {e}")

        archive_write_url = f"{self.repo_url}/repositories/{self.repo_id}/documents?returnids=true"

        self.headers['Accept'] = 'application/vnd.asg-mobius-archive-write-status.v2+json'
        self.headers['Content-Type'] = f'multipart/mixed; TYPE=policy; boundary={self.BOUNDARY_STRING}'

        self.logger.info("--------------------------------")
        self.logger.info("Method: archive_policy")
        self.logger.debug(f"URL: {archive_write_url}")
        self.logger.debug(f"Headers: {json.dumps(self.headers, indent=4)}")
        self.logger.debug(f"Body: \n{body}")

        # Send the request
        try:
            response = requests.post(archive_write_url, headers=self.headers, data=body, verify=False)
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            self.logger.debug(f"HTTP Response: {response.text}")
            return response.status_code, response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request error: {e}")
            self.logger.debug(f"Response details: {e.response.text if e.response else 'No response available'}")
            raise

    #####
    #--------------------------------------------------------------
    # Archive based on policy from string
    def archive_policy_from_str(self, str_content, policy_name, content_type_str=None):
        """
        Archives content from a string based on a specific policy.

        Args:
            str_content (str): The string content to archive.
            policy_name (str): Name of the archiving policy to apply.
            content_type_str (str, optional): The MIME Content-Type for 'str_content'.
                                             Defaults to 'archive/file'.

        Returns:
            tuple: (status_code, response_text) from the HTTP request.
        """
        if not isinstance(str_content, str):
            self.logger.error("The provided content for archiving is not a string (str).")
            raise TypeError("Content to archive must be a string (str).")

        metadata_json = {
            "objects": [
                {
                    "policies": [f"{policy_name}"]
                }
            ]
        }

        metadata_str = json.dumps(metadata_json, indent=4)
        
        # Use the provided content_type_str or the default value
        file_part_content_type = content_type_str if content_type_str is not None else self.DEFAULT_STR_CONTENT_TYPE

        try:
            body_parts = [
                f"--{self.BOUNDARY_STRING}",
                f"Content-Type: {self.METADATA_CONTENT_TYPE}",
                "",
                metadata_str,
                f"--{self.BOUNDARY_STRING}",
                f"Content-Type: {file_part_content_type}", # Using the configurable content-type
                "",
                str_content,
                "",
                f"--{self.BOUNDARY_STRING}--",
            ]

            body = "\n".join(body_parts)

        except Exception as e:
            self.logger.error(f"Unexpected error building the request body: {e}")
            raise ValueError(f"Error preparing content for archiving: {e}")

        archive_write_url = f"{self.repo_url}/repositories/{self.repo_id}/documents?returnids=true"

        self.headers['Accept'] = 'application/vnd.asg-mobius-archive-write-status.v2+json'
        self.headers['Content-Type'] = f'multipart/mixed; TYPE=policy; boundary={self.BOUNDARY_STRING}'

        self.logger.info("--------------------------------")
        self.logger.info("Method: archive_policy_from_str")
        self.logger.debug(f"URL: {archive_write_url}")
        self.logger.debug(f"Headers: {json.dumps(self.headers, indent=4)}")
        self.logger.debug(f"Body: \n{body}")

        # Send the request
        try:
            response = requests.post(archive_write_url, headers=self.headers, data=body, verify=False)
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            self.logger.debug(f"HTTP Response: {response.text}")
            return response.status_code, response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request error: {e}")
            self.logger.debug(f"Response details: {e.response.text if e.response else 'No response available'}")
            raise