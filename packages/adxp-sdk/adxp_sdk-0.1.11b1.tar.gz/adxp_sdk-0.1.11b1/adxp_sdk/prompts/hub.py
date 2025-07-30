import ast
import requests
from typing import Union, Literal, Optional, List, Tuple
from requests.exceptions import RequestException
from langchain_core.prompts import ChatPromptTemplate
from adxp_sdk.auth import Credentials
from adxp_sdk.prompts.utils import replace_braces_for_prompt


PromptVersionType = Union[Literal["latest"], Literal["release"], str]


class AXPromptHub:
    """
    A class for providing prompt hub-related functionality.

    How to use:
        >>> hub = AXPromptHub(Credentials(base_url="https://api.sktaip.com", token="your_token"))
        >>> prompt_template = hub.get_prompt("prompt_id", "release")
    """

    def __init__(self, credentials: Credentials):
        """
        Initialize the hub object.

        Args:
            credentials: Authentication information
        """
        self.credentials = credentials
        self.base_url = credentials.base_url
        self.headers = credentials.get_headers()

    def _parse_prompt_string(self, prompt_str: str) -> List[Tuple[str, str]]:
        try:
            # convert to list of tuples
            parsed = ast.literal_eval(prompt_str)
            if not isinstance(parsed, list):
                raise ValueError("Parsed result is not a list.")
            return parsed
        except (SyntaxError, ValueError) as e:
            raise ValueError(f"Failed to parse prompt string: {str(e)}")

    def get_release_prompt(self, prompt_id: str) -> List[Tuple[str, str]]:
        url = f"{self.base_url}/api/v1/agent/inference-prompts/test/{prompt_id}"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                prompt_str = response.json()["data"]
                return self._parse_prompt_string(prompt_str)

            elif response.status_code == 404:
                raise RuntimeError(f"Cannot find prompt: {prompt_id} (version: latest)")
            elif response.status_code == 401:
                raise RuntimeError(
                    "Authentication failed. The token may have expired or is invalid."
                )
            else:
                raise RuntimeError(
                    f"Failed to get prompt: {response.status_code}, {response.text}"
                )

        except RequestException as e:
            raise RuntimeError(f"Failed to get prompt: {str(e)}")

    def get_prompt(
        self, prompt_id: str, version: PromptVersionType = "release"
    ) -> ChatPromptTemplate:
        """
        Get a prompt from the prompt hub.

        Args:
            prompt_id (str): Prompt ID
            version (PromptVersionType): version ("latest", "release")

        Example:
            >>> hub = AXPromptHub(credentials)
            >>> prompt_template = hub.get_prompt("prompt_id", "release")

        """
        if version == "release":
            template_contents = self.get_release_prompt(prompt_id)
            template_contents = [
                (role, replace_braces_for_prompt(content))
                for role, content in template_contents
            ]
            prompt_template = ChatPromptTemplate(template_contents)
            return prompt_template
        elif version == "latest":
            raise RuntimeError("latest version is not supported")
        else:
            raise ValueError(f"Invalid version: {version}")
