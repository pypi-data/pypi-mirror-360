import json
from rocketcontent.content_config import ContentConfig
import json
import requests
import urllib3
import warnings
from copy import deepcopy

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class SearchSimpleBuilder:
    def __init__(self, index_name, index_value, operator="EQ", distinct=False, conjunction="AND", exit_on_error=True):
        self.index_name = index_name
        self.index_value = index_value
        self.operator = operator
        self.constraints = []
        self.repo_id = ""
        self.distinct = distinct
        self.conjunction = conjunction
        self.exitOnError = exit_on_error
        self.returnedIndexes = [{"name": self.index_name, "sort": None}]
        self.repositories = [{"id": self.repo_id}]

    def add_constraint(self):
        builder = SimpleSearchBuilder(self.index_name, self.index_value, self.operator)
        self.constraints.append(builder.build())

    def build(self):
        self.add_constraint()
        return {
            "indexSearch": {
                "name": f"Find {self.index_value} on Index {self.index_name}",
                "distinct": self.distinct,
                "conjunction": self.conjunction,
                "exitOnError": self.exitOnError,
                "constraints": self.constraints,
                "returnedIndexes": self.returnedIndexes,
                "repositories": self.repositories,
            }
        }

    def __json__(self):
        """
        Returns a JSON-serializable representation of the object.
        """
        return self.build()

    def to_json(self, indent=4):
        """
        Converts the JSON dictionary to a formatted JSON string.
        """
        return json.dumps(self.__json__(), indent=indent)

    def to_dict(self):
        return self.build() # build returns a dictionary.


class SimpleSearchBuilder:
    def __init__(self, index_name, index_value, operator="EQ"):
        """
        Initializes the SimpleSearchBuilder with index name, value, and operator.
        
        :param index_name: The name of the index to search.
        :param index_value: The value to search for in the index.
        :param operator: The operator to use for the search. Default is "EQ".
            Operator meanings:
            BT - Is between (requires two value fields)
            NB - Is not between (requires two value fields)
            LK - Is like (Allowable wildcard values are * and ?)
            LT - Is less than
            LE - Is less than or equal to
            GT - Is greater than
            GE - Is greater than or equal to
            EQ - Equals
            NE - Is not equal
            NU - Is not defined; the result includes content where the searched index is present but null.
            NN - Is defined; the result includes content where the searched index has a value.
        """
        
        # Define valid operators
        valid_operators = ["BT", "NB", "LK", "LT", "LE", "GT", "GE", "EQ", "NE", "NU", "NN"]
        
        if operator not in valid_operators:
            raise ValueError(f"Invalid operator '{operator}'. Valid operators are: {', '.join(valid_operators)}")
      
        self.index_name = index_name
        self.index_value = index_value
        self.operator = operator

    def build(self):
        return {
            "name": self.index_name,
            "operator": self.operator,
            "values": [{"value": self.index_value}],
            "subexpression": None,
        }

    def __json__(self):
        """
        Returns a JSON-serializable representation of the object.
        """
        return self.build()

    def to_json(self, indent=4):
        """
        Converts the JSON dictionary to a formatted JSON string.
        """
        return json.dumps(self.__json__(), indent=indent)

    def to_dict(self):
        """
        Returns a dictionary representation of the object.
        """
        return self.build()
    
class ContentSearch:

    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_url = content_config.repo_url
            self.repo_id = content_config.repo_id
            self.logger = content_config.logger
            self.headers = deepcopy(content_config.headers)
        else:
            raise TypeError("ContentConfig class object expected")

    # Execute a search using the SimpleSearch object
    def search(self, search_payload: SearchSimpleBuilder, search_payload2: SearchSimpleBuilder =  None, operator: str = "AND") -> list:
        
        operator = operator.upper()
        if operator != "AND" and operator != "OR":
            self.logger.error("Invalid operator. Only 'AND' or 'OR' are allowed.")
            raise ValueError("Invalid operator. Only 'AND' or 'OR' are allowed.")
        
        if search_payload2 is not None:
            search_payload.constraints.append(search_payload2.build())
            search_payload.conjunction = operator

        search_payload.repositories = [{"id": self.repo_id}]

        search_url = self.repo_url + "/searches?returnresults=true&limit=200"

        # Headers
        self.headers['Content-Type'] = 'application/vnd.asg-mobius-search.v1+json'
        self.headers['Accept'] = 'application/vnd.asg-mobius-search.v1+json'

        self.logger.info("--------------------------------")
        self.logger.info("Method : search")
        self.logger.debug(f"URL : {search_url}")
        self.logger.debug(f"Headers : {json.dumps(self.headers)}")
        self.logger.debug(f"Payload : {search_payload.to_json()}")

        response = requests.post(search_url, json=search_payload.to_dict(), headers=self.headers, verify=False)

        try:
            json_data = response.json()
        except json.JSONDecodeError:
            self.logger.error("JSON Decode Error. Returning empty list.")
            return []

        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError:
                self.logger.error("JSON Decode Error. Returning empty list.")
                return []
        elif isinstance(json_data, dict):
            data = json_data
        else:
            self.logger.warning("Returning empty list.")
            return []

        object_ids = []
        if "results" in data and isinstance(data["results"], list):
            for result in data["results"]:
                if "objectId" in result:
                    object_ids.append(result["objectId"])

        self.logger.info(f"Search Results : {len(object_ids)}")    
                
        return object_ids



def main():

    # Validates if the SimpleSearch class is serializable.

    try:
        search = SimpleSearchBuilder( "fieldName", "fieldValue", "EQ")
        # CORRECTED LINE: Use search.to_json() instead of json.dumps(search)
        json_string = search.to_json(indent=4)
        print("SimpleSearch is serializable:")
        print(json_string)

        deserialized_search = json.loads(json_string)
        print("\nDeserialized JSON:")
        print(deserialized_search)

    except TypeError as e:
        print(f"SimpleSearch is not serializable: {e}")
    except json.JSONDecodeError as e:
        print(f"Error while deserializing: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
