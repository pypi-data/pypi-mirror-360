import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException
from adxp_sdk.auth import Credentials
from .model_utils import is_valid_uuid
import os


class AXModelHub:
    """
    A class for providing model hub-related functionality (model creation, retrieval, deletion, etc).

    How to use:
        >>> hub = AXModelHub(Credentials(base_url="https://api.sktaip.com", username="user", password="pw", client_id="cid"))
        >>> response = hub.create_model({"name": "my-model", ...})
        >>> all_models = hub.get_models()
        >>> one_model = hub.get_model_by_id("model_id")
        >>> hub.delete_model("model_id")
    """

    def __init__(self, credentials: Credentials):
        """
        Initialize the model hub object.

        Args:
            credentials: Authentication information
        """
        self.credentials = credentials
        self.base_url = credentials.base_url
        self.headers = credentials.get_headers()

    # ====================================================================
    # Model
    # ====================================================================

    # [Model] Create a new model
    def create_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new model via POST /api/v1/models

        Args:
            model_data (dict): The model creation payload

        Returns:
            dict: The API response
        """
        url = f"{self.base_url}/api/v1/models"
        try:
            response = requests.post(url, json=model_data, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Endpoint not found: {url}")
            else:
                raise RuntimeError(f"Failed to create model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create model: {str(e)}")

    # [Model] Retrieve all models
    def get_models(
        self,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
        ids: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve all models via GET /api/v1/models with optional query parameters.
        Args:
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'name:model_name' or 'tags[].name:abc')
            search (str): Search keyword
            ids (str): Comma-separated list of model IDs
        Returns:
            dict: The API response
        """
        url = f"{self.base_url}/api/v1/models"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        if ids:
            params["ids"] = ids
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Endpoint not found: {url}")
            else:
                raise RuntimeError(f"Failed to get models: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get models: {str(e)}")

    # [Model] Retrieve a single model by ID
    def get_model_by_id(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve a single model by ID via GET /api/v1/models/{model_id}
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to get model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model: {str(e)}")

    # [Model] Delete a model by ID
    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """
        Delete a model by ID via DELETE /api/v1/models/{model_id}
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                # Some APIs return 204 No Content, some return 200 with a body
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to delete model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model: {str(e)}")

    # [Model-Type] Retrieve all model types
    def get_model_types(self) -> Dict[str, Any]:
        """
        Retrieve model types via GET /api/v1/models/types
        """
        url = f"{self.base_url}/api/v1/models/types"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to get model types: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model types: {str(e)}")

    # [Model-Tag] Retrieve all model tags
    def get_model_tags(self) -> Dict[str, Any]:
        """
        Retrieve model tags via GET /api/v1/models/tags
        """
        url = f"{self.base_url}/api/v1/models/tags"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to get model tags: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model tags: {str(e)}")
        
    # [Model] Recover a deleted model by ID
    def recover_model(self, model_id: str) -> Dict[str, Any]:
        """
        Recover a deleted model via PUT /api/v1/models/{model_id}/recovery
        Args:
            model_id (str): The model ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/recovery"
        try:
            response = requests.put(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "recovered"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to recover model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to recover model: {str(e)}")
        
    # [Model] Upload a local LLM model file
    def upload_model_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a local LLM model file via POST /api/v1/models/files
        Args:
            file_path (str): Path to the local file to upload
        Returns:
            dict: The API response, e.g. {"file_name": ..., "temp_file_path": ...}
        """
        url = f"{self.base_url}/api/v1/models/files"
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(f.name), f, "application/octet-stream")}
                response = requests.post(url, files=files, headers={k: v for k, v in self.headers.items() if k.lower() != "content-type"})
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to upload model file: {response.status_code}, {response.text}")
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {file_path}")
        except RequestException as e:
            raise RuntimeError(f"Failed to upload model file: {str(e)}")

    # [Model] Update a model by ID
    def update_model(self, model_id: str, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model by ID via PUT /api/v1/models/{model_id}

        Args:
            model_id (str): The model ID (UUID)
            model_data (dict): The model update payload (all fields optional)

        Returns:
            dict: The API response (updated model info)
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}"
        try:
            response = requests.put(url, json=model_data, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            elif response.status_code == 400:
                raise RuntimeError(f"Bad request: {response.text}")
            else:
                raise RuntimeError(f"Failed to update model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to update model: {str(e)}")

    # ====================================================================
    # Model-Provider
    # ====================================================================

    # [Model-Provider] Create a new model provider
    def create_model_provider(self, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new model provider via POST /api/v1/models/providers
        """
        url = f"{self.base_url}/api/v1/models/providers"
        try:
            response = requests.post(url, json=provider_data, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to create model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create model provider: {str(e)}")

    # [Model-Provider] Retrieve all model providers
    def get_model_providers(
        self,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve all model providers via GET /api/v1/models/providers with optional query parameters.
        Args:
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'name:provider_name')
            search (str): Search keyword
        Returns:
            dict: The API response
        """
        url = f"{self.base_url}/api/v1/models/providers"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            else:
                raise RuntimeError(f"Failed to get model providers: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model providers: {str(e)}")

    # [Model-Provider] Retrieve a single model provider by ID
    def get_model_provider_by_id(self, provider_id: str) -> Dict[str, Any]:
        """
        Retrieve a single model provider by ID via GET /api/v1/models/providers/{provider_id}
        """
        if not is_valid_uuid(provider_id):
            raise ValueError(f"provider_id must be a valid UUID string, got: {provider_id}")
        url = f"{self.base_url}/api/v1/models/providers/{provider_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Provider not found: {provider_id}")
            else:
                raise RuntimeError(f"Failed to get model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model provider: {str(e)}")

    # [Model-Provider] Update a model provider
    def update_model_provider(self, provider_id: str, provider_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a model provider via PUT /api/v1/models/providers/{provider_id}
        """
        if not is_valid_uuid(provider_id):
            raise ValueError(f"provider_id must be a valid UUID string, got: {provider_id}")
        url = f"{self.base_url}/api/v1/models/providers/{provider_id}"
        try:
            response = requests.put(url, json=provider_data, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "updated"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Provider not found: {provider_id}")
            else:
                raise RuntimeError(f"Failed to update model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to update model provider: {str(e)}")

    # [Model-Provider] Delete a model provider
    def delete_model_provider(self, provider_id: str) -> Dict[str, Any]:
        """
        Delete a model provider via DELETE /api/v1/models/providers/{provider_id}
        """
        if not is_valid_uuid(provider_id):
            raise ValueError(f"provider_id must be a valid UUID string, got: {provider_id}")
        url = f"{self.base_url}/api/v1/models/providers/{provider_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Provider not found: {provider_id}")
            else:
                raise RuntimeError(f"Failed to delete model provider: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model provider: {str(e)}")

    # ====================================================================
    # Model-Tag
    # ====================================================================

    # [Model] Add tags to a specific model
    def add_tags_to_model(self, model_id: str, tags: list) -> Dict[str, Any]:
        """
        Add tags to a specific model via PUT /api/v1/models/{model_id}/tags
        Args:
            model_id (str): The model ID (UUID)
            tags (list): List of tag dicts, e.g. [{"name": "tag"}]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/tags"
        try:
            response = requests.put(url, json=tags, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tags added"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to add tags to model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to add tags to model: {str(e)}")

    # [Model] Remove tags from a specific model
    def remove_tags_from_model(self, model_id: str, tags: list) -> Dict[str, Any]:
        """
        Remove tags from a specific model via DELETE /api/v1/models/{model_id}/tags
        Args:
            model_id (str): The model ID (UUID)
            tags (list): List of tag dicts, e.g. [{"name": "tag"}]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/tags"
        try:
            response = requests.delete(url, json=tags, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tags removed"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to remove tags from model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to remove tags from model: {str(e)}")

    # ====================================================================
    # Model-Language
    # ====================================================================

    # [Model] Add languages to a specific model
    def add_languages_to_model(self, model_id: str, languages: list) -> Dict[str, Any]:
        """
        Add languages to a specific model via PUT /api/v1/models/{model_id}/languages
        Args:
            model_id (str): The model ID (UUID)
            languages (list): List of language dicts, e.g. [{"name": "Korean"}]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/languages"
        try:
            response = requests.put(url, json=languages, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "languages added"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to add languages to model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to add languages to model: {str(e)}")

    # [Model] Remove languages from a specific model
    def remove_languages_from_model(self, model_id: str, languages: list) -> Dict[str, Any]:
        """
        Remove languages from a specific model via DELETE /api/v1/models/{model_id}/languages
        Args:
            model_id (str): The model ID (UUID)
            languages (list): List of language dicts, e.g. [{"name": "Korean"}]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/languages"
        try:
            response = requests.delete(url, json=languages, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "languages removed"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to remove languages from model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to remove languages from model: {str(e)}")
    
    # ====================================================================
    # Model-Task
    # ====================================================================

    # [Model] Add tasks to a specific model
    def add_tasks_to_model(self, model_id: str, tasks: list) -> Dict[str, Any]:
        """
        Add tasks to a specific model via PUT /api/v1/models/{model_id}/tasks
        Args:
            model_id (str): The model ID (UUID)
            tasks (list): List of task dicts, e.g. [{"name": "completion"}]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/tasks"
        try:
            response = requests.put(url, json=tasks, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tasks added"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to add tasks to model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to add tasks to model: {str(e)}")

    # [Model] Remove tasks from a specific model
    def remove_tasks_from_model(self, model_id: str, tasks: list) -> Dict[str, Any]:
        """
        Remove tasks from a specific model via DELETE /api/v1/models/{model_id}/tasks
        Args:
            model_id (str): The model ID (UUID)
            tasks (list): List of task dicts, e.g. [{"name": "completion"}]
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/tasks"
        try:
            response = requests.delete(url, json=tasks, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "tasks removed"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to remove tasks from model: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to remove tasks from model: {str(e)}")

    # ====================================================================
    # Model-Version
    # There is no registration api of model version. 
    # Because the model version is automatically created when the fine-tuning is finished.
    # ====================================================================

    # [Model-Version] Retrieve versions of a model
    def get_model_versions(
        self,
        model_id: str,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
        ids: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve versions of a model via GET /api/v1/models/{model_id}/versions with optional query parameters.
        Args:
            model_id (str): The model ID (UUID)
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'description:desc')
            search (str): Search keyword
            ids (str): Comma-separated list of version IDs
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        if ids:
            params["ids"] = ids
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to get model versions: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model versions: {str(e)}")

    # [Model-Version] Retrieve a specific version of a model
    def get_model_version_by_id(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific version of a model via GET /api/v1/models/{model_id}/versions/{version_id}
        Args:
            model_id (str): The model ID (UUID)
            version_id (str): The version ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions/{version_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or version not found: {model_id}, {version_id}")
            else:
                raise RuntimeError(f"Failed to get model version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model version: {str(e)}")

    # [Model-Version] Retrieve a specific version by version_id only
    def get_version_by_id(self, version_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific version by version_id via GET /api/v1/models/versions/{version_id}
        Args:
            version_id (str): The version ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/versions/{version_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Version not found: {version_id}")
            else:
                raise RuntimeError(f"Failed to get version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get version: {str(e)}")

    # [Model-Version] Delete a specific version of a model
    def delete_model_version_by_id(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Delete a specific version of a model via DELETE /api/v1/models/{model_id}/versions/{version_id}
        Args:
            model_id (str): The model ID (UUID)
            version_id (str): The version ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions/{version_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or version not found: {model_id}, {version_id}")
            else:
                raise RuntimeError(f"Failed to delete model version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model version: {str(e)}")

    # [Model-Version] Update a specific version of a model
    def update_model_version_by_id(self, model_id: str, version_id: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a specific version of a model via PUT /api/v1/models/{model_id}/versions/{version_id}
        Args:
            model_id (str): The model ID (UUID)
            version_id (str): The version ID (UUID)
            version_data (dict): The version update payload
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/versions/{version_id}"
        try:
            response = requests.put(url, json=version_data, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "updated"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or version not found: {model_id}, {version_id}")
            else:
                raise RuntimeError(f"Failed to update model version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to update model version: {str(e)}")

    # [Model-Version] Promote a specific version to a model
    def promote_version(self, version_id: str, promotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Promote a specific version to a model via POST /api/v1/models/versions/{version_id}/promote
        Args:
            version_id (str): The version ID (UUID)
            promotion_data (dict): The promotion payload (e.g., {"display_name": ..., "description": ...})
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(version_id):
            raise ValueError(f"version_id must be a valid UUID string, got: {version_id}")
        url = f"{self.base_url}/api/v1/models/versions/{version_id}/promote"
        try:
            response = requests.post(url, json=promotion_data, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Version not found: {version_id}")
            else:
                raise RuntimeError(f"Failed to promote version: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to promote version: {str(e)}") 
    
    # ====================================================================
    # Model-Endpoint
    # ====================================================================

    # [Model-Endpoint] Register an endpoint for a specific model
    def create_model_endpoint(self, model_id: str, endpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an endpoint for a specific model via POST /api/v1/models/{model_id}/endpoints
        Args:
            model_id (str): The model ID (UUID)
            endpoint_data (dict): The endpoint registration payload (e.g., {"url": ..., "identifier": ..., "key": ..., "description": ...})
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints"
        try:
            response = requests.post(url, json=endpoint_data, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to create model endpoint: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create model endpoint: {str(e)}")

    # [Model-Endpoint] Retrieve multiple endpoints for a specific model
    def get_model_endpoints(
        self,
        model_id: str,
        page: int = 1,
        size: int = 10,
        sort: str = None,
        filter: str = None,
        search: str = None,
    ) -> Dict[str, Any]:
        """
        Retrieve multiple endpoints for a specific model via GET /api/v1/models/{model_id}/endpoints with optional query parameters.
        Args:
            model_id (str): The model ID (UUID)
            page (int): Page number (default: 1)
            size (int): Items per page (default: 10)
            sort (str): Sort field and order (e.g., 'updated_at,desc')
            filter (str): Filter string (e.g., 'description:desc')
            search (str): Search keyword
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints"
        params = {"page": page, "size": size}
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model not found: {model_id}")
            else:
                raise RuntimeError(f"Failed to get model endpoints: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model endpoints: {str(e)}")

    # [Model-Endpoint] Retrieve a single endpoint for a specific model
    def get_model_endpoint_by_id(self, model_id: str, endpoint_id: str) -> Dict[str, Any]:
        """
        Retrieve a single endpoint for a specific model via GET /api/v1/models/{model_id}/endpoints/{endpoint_id}
        Args:
            model_id (str): The model ID (UUID)
            endpoint_id (str): The endpoint ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(endpoint_id):
            raise ValueError(f"endpoint_id must be a valid UUID string, got: {endpoint_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints/{endpoint_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or endpoint not found: {model_id}, {endpoint_id}")
            else:
                raise RuntimeError(f"Failed to get model endpoint: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get model endpoint: {str(e)}")

    # [Model-Endpoint] Delete a single endpoint for a specific model
    def delete_model_endpoint_by_id(self, model_id: str, endpoint_id: str) -> Dict[str, Any]:
        """
        Delete a single endpoint for a specific model via DELETE /api/v1/models/{model_id}/endpoints/{endpoint_id}
        Args:
            model_id (str): The model ID (UUID)
            endpoint_id (str): The endpoint ID (UUID)
        Returns:
            dict: The API response
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        if not is_valid_uuid(endpoint_id):
            raise ValueError(f"endpoint_id must be a valid UUID string, got: {endpoint_id}")
        url = f"{self.base_url}/api/v1/models/{model_id}/endpoints/{endpoint_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return response.json() if response.content else {"status": "deleted"}
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError(f"Model or endpoint not found: {model_id}, {endpoint_id}")
            else:
                raise RuntimeError(f"Failed to delete model endpoint: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete model endpoint: {str(e)}")
            
    # ====================================================================
    # Model-Custom-Runtime
    # ====================================================================
    # [Model-Custom-Runtime] Create a new custom runtime for a specific model
    def create_custom_runtime(self, runtime_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new custom runtime via POST /api/v1/custom-runtimes

        Args:
            runtime_data (dict): The custom runtime creation payload

        Returns:
            dict: The API response (created custom runtime info)
        """
        url = f"{self.base_url}/api/v1/custom-runtimes"
        try:
            response = requests.post(url, json=runtime_data, headers=self.headers)
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Model not found.")
            elif response.status_code == 409:
                raise RuntimeError("A custom runtime configuration for this model already exists.")
            elif response.status_code == 400:
                raise RuntimeError(f"Bad request: {response.text}")
            else:
                raise RuntimeError(f"Failed to create custom runtime: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to create custom runtime: {str(e)}")

    # [Model-Custom-Runtime] Retrieve custom runtime for a specific model
    def get_custom_runtime_by_model(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve custom runtime configuration by model ID via GET /api/v1/custom-runtimes/model/{model_id}

        Args:
            model_id (str): The model ID (UUID)

        Returns:
            dict: The API response (custom runtime info)
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/custom-runtimes/model/{model_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Model or custom runtime configuration not found.")
            else:
                raise RuntimeError(f"Failed to get custom runtime: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to get custom runtime: {str(e)}")

    # [Model-Custom-Runtime] Delete a custom runtime for a specific model
    def delete_custom_runtime_by_model(self, model_id: str) -> Dict[str, Any]:
        """
        Delete custom runtime configuration by model ID via DELETE /api/v1/custom-runtimes/model/{model_id}

        Args:
            model_id (str): The model ID (UUID)

        Returns:
            dict: The API response (status or empty dict)
        """
        if not is_valid_uuid(model_id):
            raise ValueError(f"model_id must be a valid UUID string, got: {model_id}")
        url = f"{self.base_url}/api/v1/custom-runtimes/model/{model_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in (200, 204):
                return {}  # 성공 시 빈 dict 반환
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 404:
                raise RuntimeError("Model or custom runtime configuration not found.")
            else:
                raise RuntimeError(f"Failed to delete custom runtime: {response.status_code}, {response.text}")
        except RequestException as e:
            raise RuntimeError(f"Failed to delete custom runtime: {str(e)}")

    # [Model-Custom-Runtime] Upload code files
    def upload_custom_code_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a custom code file via POST /api/v1/custom-runtimes/code/files
        Args:
            file_path (str): Path to the local file to upload (zip, tar, etc)
        Returns:
            dict: The API response, e.g. {"file_name": ..., "temp_file_path": ...}
        """
        url = f"{self.base_url}/api/v1/custom-runtimes/code/files"
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(f.name), f, "application/octet-stream")}
                response = requests.post(url, files=files, headers={k: v for k, v in self.headers.items() if k.lower() != "content-type"})
            if response.status_code in (200, 201):
                return response.json()
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed. The token may have expired or is invalid.")
            elif response.status_code == 400:
                raise RuntimeError(f"Bad request: {response.text}")
            else:
                raise RuntimeError(f"Failed to upload custom code file: {response.status_code}, {response.text}")
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {file_path}")
        except RequestException as e:
            raise RuntimeError(f"Failed to upload custom code file: {str(e)}") 
    