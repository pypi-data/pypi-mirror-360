from typing import Optional
from datetime import datetime, timedelta
import requests
from requests.exceptions import RequestException
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from typing_extensions import Self


class Credentials(BaseModel):
    """
    Authentication credentials for the A.X Platform API.

    Attributes:
        username (str): User name
        password (str): User password
        project (str): Project name. it is used as client_id in keycloak
        base_url (str): Base URL of the API

    Example:
        ```python
        credentials = Credentials(
            username="user",
            password="password",
            project="project_name",
            base_url="https://aip.sktai.io"
        )
        token = credentials.authenticate()
        headers = credentials.get_headers()
        ```
    """

    username: str
    password: str
    project: str
    base_url: str

    _token: Optional[str] = PrivateAttr(default=None)
    _auth_time: Optional[datetime] = PrivateAttr(default=None)
    _token_expiry_hours: int = PrivateAttr(default=48)
    _grant_type: str = PrivateAttr(default="password")

    @model_validator(mode="after")
    def auto_authenticate(self) -> Self:
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
        self.authenticate()
        return self
    

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def is_token_expired(self) -> bool:
        if not self._auth_time:
            return True
        expiry_time = self._auth_time + timedelta(hours=self._token_expiry_hours)
        return datetime.now() > expiry_time

    def _perform_auth(self) -> str:
        login_url = f"{self.base_url}/api/v1/auth/login"
        login_data = {
            "grant_type": self._grant_type,
            "username": self.username,
            "password": self.password,
            "client_id": self.project,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

        try:
            res = requests.post(login_url, data=login_data, headers=headers)
            if res.status_code == 201:
                self._token = res.json().get("access_token")
                self._auth_time = datetime.now()
                if self._token is None:
                    raise RuntimeError("Authentication failed: No token received")
                return self._token
            raise RuntimeError(f"Authentication failed: {res.status_code}, {res.text}")
        except RequestException as e:
            raise RuntimeError(
                f"Error occurred during authentication request: {str(e)}"
            )

    def authenticate(self) -> str:
        """
        Authenticates with the API server and retrieves a token.
        If the token is expired, it automatically attempts to refresh.

        Returns:
            str: Authentication token

        Raises:
            RuntimeError: If authentication fails
        """
        if self._token and not self.is_token_expired:
            return self._token

        else:
            return self._perform_auth()

    def get_headers(self) -> dict:
        """
        Returns the headers required for API requests.

        Returns:
            dict: Headers containing the authentication token
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self._token is None or self.is_token_expired:
            self.authenticate()

        headers["Authorization"] = f"Bearer {self._token}"

        return headers
