import logging
import sys
import time
from http import HTTPStatus
from logging import StreamHandler
from threading import Lock
from typing import Any, Callable, Dict, Optional, TextIO

import requests
from requests import Response
from requests.auth import AuthBase
from requests.exceptions import RequestException
from requests.sessions import Session

from tenyks_sdk.sdk.config import API_MAX_RETRIES
from tenyks_sdk.sdk.exceptions import ClientError


class TokenAuth(AuthBase):

    def __init__(self, get_token: Callable[[], str]):
        self.get_token = get_token

    def __call__(self, response: Response) -> Response:
        response.headers["Authorization"] = f"Bearer {self.get_token()}"
        return response


class Client:

    def __init__(
        self,
        api_base_url: str,
        token: str,
        session: Optional[Session] = None,
        logger: Optional[logging.Logger] = None,
        logger_stream: Optional[TextIO] = sys.stdout,
        logger_level: int = logging.INFO,
    ):
        self.api_base_url = api_base_url
        self._token = token
        self.session = session or requests.Session()
        self.token_lock = Lock()
        self.session.auth = TokenAuth(lambda: self.token)

        self.logger: logging.Logger = logger or logging.getLogger("Tenyks")
        if not logger and not self.logger.handlers:
            handler = StreamHandler(stream=logger_stream)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logger_level)

        self.api_key: Optional[str] = None
        self.api_secret: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    @property
    def token(self) -> str:
        with self.token_lock:
            return self._token

    @token.setter
    def token(self, value: str) -> None:
        with self.token_lock:
            self._token = value

    @classmethod
    def authenticate_with_api_key(
        cls,
        api_base_url: str,
        api_key: str,
        api_secret: str,
    ) -> "Client":

        url = f"{api_base_url}/auth/apikey"
        response = requests.post(
            url, json={"api_key": api_key, "api_secret": api_secret}
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        client = cls(
            api_base_url,
            token,
        )
        client.api_key = api_key
        client.api_secret = api_secret
        return client

    @classmethod
    def authenticate_with_login(
        cls,
        api_base_url: str,
        username: str,
        password: str,
    ) -> "Client":
        url = f"{api_base_url}/auth/login"
        response = requests.post(url, json={"username": username, "password": password})
        response.raise_for_status()
        token = response.json().get("access_token")
        client = cls(api_base_url, token)
        client.username = username
        client.password = password
        return client

    def refresh_token(self) -> None:
        if self.api_key and self.api_secret:
            url = f"{self.api_base_url}/auth/apikey"
            response = requests.post(
                url, json={"api_key": self.api_key, "api_secret": self.api_secret}
            )
            if response.status_code == 401:
                self.logger.error(
                    "Failed to refresh token. API secret could be expired."
                )
        elif self.username and self.password:
            url = f"{self.api_base_url}/auth/login"
            response = requests.post(
                url, json={"username": self.username, "password": self.password}
            )
        else:
            raise Exception(
                "No authentication credentials stored in the Client object."
            )

        response.raise_for_status()
        self.token = response.json().get("access_token")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict]:
        return self._api_request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict]:
        return self._api_request(
            "POST",
            endpoint,
            json=body,
            files=files,
            data=data,
            params=params,
        )

    def put(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict]:
        return self._api_request(
            "PUT",
            endpoint,
            json=body,
            files=files,
            data=data,
        )

    def patch(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict]:
        return self._api_request(
            "PATCH",
            endpoint,
            json=body,
            files=files,
            data=data,
            params=params,
        )

    def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict]:
        return self._api_request("DELETE", endpoint, params=params)

    def _api_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        attempt: int = 0,
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.api_base_url}{endpoint}"
        try:
            response = self._http_request(method, url, params, json, files, data)
            return response.json() if response.content else None
        except RequestException as e:
            if (
                e.response.status_code == HTTPStatus.UNAUTHORIZED
                and attempt < API_MAX_RETRIES
            ):
                self.logger.info("Unauthorized request. Trying to refresh the token.")
                self.refresh_token()  # Attempt to refresh the token
                time.sleep((attempt + 1) ** 2)
                return self._api_request(
                    method, endpoint, params, json, files, data, attempt + 1
                )
            else:
                self._raise_on_response(e.response)
        except Exception as err:
            raise ClientError(f"Error during {method} request to {endpoint}: {err}")

    def _http_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Response:
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            files=files,
            data=data,
        )
        response.raise_for_status()
        return response

    def _raise_on_response(self, response: Response) -> None:
        try:
            json_error = response.json()
            message = json_error.get("message", response.text)
        except ValueError:
            message = response.text

        raise ClientError(
            f"({response.status_code}) Error from {response.request.url}: {message}"
        )
