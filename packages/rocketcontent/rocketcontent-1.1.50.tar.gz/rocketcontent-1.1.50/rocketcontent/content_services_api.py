import urllib3
import warnings

from .content_config import ContentConfig
from .content_search import ContentSearch, SearchSimpleBuilder
from .content_smart_chat import ContentSmartChat
from .content_archive_metadata import ContentArchiveMetadata
from .content_archive_policy import ContentArchivePolicy 
from .content_archive_policy_plus import ContentArchivePolicyPlus 
from .content_document import ContentDocument

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentServicesApi:
    """
    ContentServicesApi is the main class for interacting with Mobius REST content_obj.

    Attributes:
        config: is a ContentConfig object with information about connection, and logging ,etc.
    """
    def __init__(self, yaml_file):
        """
        Initializes the ContentServicesApi class from YAML file.
        
        Args:
            yaml_file: [Mandatory] Path to the YAML configuration 
        """
        self.config = ContentConfig(yaml_file)
 

    # Execute a search using the SimpleSearch object
    def search(self, search_payload):
        """
        The 'search' method performs a search in Content Repository using a 'SearchSimpleBuilder' object and returns a list of matching documents.

        Args:
            search_payload: [Mandatory] is a SearchSimpleBuilder object representing the search.
        """

        if not isinstance(search_payload, SearchSimpleBuilder):
           raise TypeError("SearchSimpleBuilder class object expected")
  
        search_obj= ContentSearch(self.config)
        return search_obj.search(search_payload)
    

    #--------------------------------------------------------------
    def smart_chat(self, user_query, document_ids=None, conversation=""):
        """
        Interrogate Content Repository with Smart Chat

        Args:
            question    : [Mandatory] The query to send to the Smart Chat content_obj.
            document_ids: [Optional] An array of document IDs to limit the query scope.
            conversation: [Optional] A conversation ID to maintain context            
        """
        smart_obj = ContentSmartChat(self.config)
        return smart_obj.smart_chat(user_query, document_ids, conversation)
 

    #--------------------------------------------------------------
    def archive_metadata(self, document_collection):
        """
        Archives a document using metadata.

        Args:
            document_collection: [Mandatory] is a ArchiveDocumentCollection object containing list of documents with metadata.
        """
        archive_obj = ContentArchiveMetadata(self.config)
        return archive_obj.archive_metadata(document_collection)

    #--------------------------------------------------------------
    # Archive based on policy
    def archive_policy(self, file_path, policy_name):
        """
        Archives a document using an archiving policy.

        Args:
            file_path: [Mandatory] Path to the file to archive.
            policy_name: [Mandatory] Name of an existing archiving policy in rocketcontent.
        """
        archive_obj = ContentArchivePolicy(self.config)
        return archive_obj.archive_policy(file_path, policy_name)

    #--------------------------------------------------------------
    # Archive based on policy
    def archive_policy_plus(self, file_path, policy_name):
        """
        Archives a document using an archiving policy.

        Args:
            file_path: [Mandatory] Path to the file to archive.
            policy_name: [Mandatory] Name of an existing archiving policy in rocketcontent.
        """
        archive_obj = ContentArchivePolicyPlus(self.config)
        return archive_obj.archive_policy(file_path, policy_name)


    #--------------------------------------------------------------
    # Archive based on policy
    def archive_policy_from_str(self, str_content, policy_name):
        """
        Archives a document using an archiving policy.

        Args:
            str_content: [Mandatory] string to archive.
            policy_name: [Mandatory] Name of an existing archiving policy in rocketcontent.
        """
        archive_obj = ContentArchivePolicy(self.config)
        return archive_obj.archive_policy_from_str(str_content, policy_name)
    
    #--------------------------------------------------------------
    # Create Content Class definition
    #def create_content_class(self, content_class_json):
    #    admin_obj = ContentRepository(self.config)
    #    return admin_obj.create_content_class(content_class_json)
    
    #--------------------------------------------------------------
    # Create Index Group Definition
    #def create_index_group(self, index_group_json):
    #    admin_obj = ContentRepository(self.config)
    #    return admin_obj.create_index_group(index_group_json)
    

    def delete(self, document_id):
        """"
        Delete in Content Repository a document by ID.

        Args:
            document_id: [Mandatory] Document ID.
        """
        doc_obj= ContentDocument(self.config)
        return doc_obj.delete(document_id)
