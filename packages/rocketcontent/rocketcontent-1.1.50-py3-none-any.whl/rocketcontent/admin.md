# Python Library for Content Repository Administration
[Back to Readme](README.md)

`ContentAdmServicesApi` Python library offers a primary class designed to facilitate interaction with the Content Repository Administration REST Api. This class encompasses a wide range of operations, including:

- Create Content Classes.
- Create Indexes.
- Import Archiving Policies.

>**Disclaimer: This Python library is provided for demonstration purposes only to illustrate the use of the Content Repository Administration API. It is explicitly stated that this library does not constitute an official Rocket Software product and lacks official support. Rocket Software assumes no responsibility for the use, performance, or any consequences arising from the use of this library. Users are advised to consult the official Rocket Software documentation for information and support regarding the Content Repository API.**

## Table of Contents

- [Installation](#installation)
    - [Configuration File](#configuration-file)
- [Class Initialization](#class-initialization)
- [Methods](#methods)
    - [Import Archiving Policy](#import-archiving-policy)
[Back to Readme](README.md)

<hr style="border: 2px solid grey; background-color: grey;">

## Installation

The `ContentAdmServicesApi` class requires **Python 3.9+**. To install the necessary dependencies and the Content Repository library, run the following commands:

```bash
## From cmd.exe
pip install rocketcontent
```

### Configuration file

* Create a YAML configuration file (e.g., `rocketcontent.yaml`) to store your Content Repository ID, credentials and settings. For the first connection, leave the `repo_id` field blank—it will be populated automatically.

    ```yaml
    # <python-content-services-api-dir>/conf/rocketcontent.yaml
    repository:
        log_level: DEBUG     # Valid log Levels: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE"
        repo_id: 
        repo_name: myRepo
        repo_server_user: ADMIN
        repo_server_pass: ''
        repo_pass: admin
        repo_user: $admin$
        repo_url: https://contentrepo.rocket.com        
    ```

    > **Note: Ensure the configuration file is placed in the appropriate directory (e.g., `<python-content-services-api-dir>/conf/`).**

## Class Initialization
[Table of Contents](#table-of-contents)

The `ContentAdmServicesApi` class is the primary interface for interacting with the Content Repository Administration REST Api. It is instantiated by providing a YAML configuration file that contains essential settings for Api communication. Once initialized, it exposes methods for performing various operations against the Content Repository Administration REST Api.

The class uses the YAML configuration file to persistently store key attributes, such as the repository ID (`repo_id`), which are required for many Api methods. Upon initial data retrieval from Content Repository, an MD5 checksum file is generated alongside the configuration. If the YAML file is modified, a refresh mechanism triggers a re-fetch of the `repo_id` from Content Repository to ensure consistency.

> **Note:** Use `try:` and `except:` blocks for robust error handling.

* **Parameter**:
    - `yaml_config_file`: **[Mandatory]** Path to the YAML configuration file. 

* **Returns**:
    - A `ContentAdmServicesApi` object. 

* **Example**:
    - The `50_repository.py` program illustrates the initialization process of this object and displays its key attributes.

    ```python
    import os
    from rocketcontent.content_adm_services_api import ContentAdmServicesApi
    
    try:
        cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'conf'))
        config_file = cfg_path + '/rocketcontent.yaml'  
        content_adm_obj = ContentAdmServicesApi(config_file)

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")    
    ```