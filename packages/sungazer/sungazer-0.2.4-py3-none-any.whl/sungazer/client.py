from __future__ import annotations

import json
from re import I
from typing import Any, TypeVar, cast

import httpx

from .models import (
    CheckFWResponse,
    DeviceDetailResponse,
    GetCommResponse,
    GridProfileGetResponse,
    GridProfileRefreshResponse,
    StartResponse,
    StopResponse,
)

T = TypeVar("T")


class BaseClient:
    """Base client with common HTTP methods."""

    def __init__(self, client: httpx.Client, serial: str | None = None):
        """
        Initialize with an httpx client.

        Args:
            client: The httpx client to use for requests
            serial: The serial number of the PVS6 device

        """
        self.client = client
        self.serial = serial

    def _handle_response(self, response: httpx.Response, model_class: type[T]) -> T:
        """
        Handle the API response.

        Args:
            response: The response from the API
            model_class: The Pydantic model class to deserialize the response to

        Returns:
            The deserialized response

        Raises:
            httpx.HTTPStatusError: If the response contains an error status code

        """
        response.raise_for_status()

        # If the response is empty, return an empty instance of the model
        if not response.content:
            return model_class()

        _content = response.text
        content = []
        # for some reason we get the http headers in the response.text sometimes
        # so we have to remove them
        for line in _content.splitlines():
            if not line.startswith(("{", "\t", "}")):
                continue
            content.append(line)
        _content = "\n".join(content)
        return model_class(**json.loads(_content))  # type: ignore[attr-defined]

    def _get(
        self,
        path: str,
        model_class: type[T] | None = None,
        params: dict[str, Any] | None = None,
    ) -> T | dict:
        """
        Send a GET request to the API.

        Args:
            path: The path to append to the base URL
            model_class: The Pydantic model class to deserialize the response to
            params: Optional query parameters

        Returns:
            The deserialized response

        """
        response = self.client.get(path, params=params)
        if model_class is None:
            return cast("dict", json.loads(response.text))
        return self._handle_response(response, model_class)


class SessionClient(BaseClient):
    """Client for session operations."""

    def start(self) -> StartResponse:
        """
        Start a new session.

        """
        try:
            return cast(
                "StartResponse",
                self._get("/dl_cgi", StartResponse, params={"Command": "Start"}),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                msg = f"Start failed: {e.response!s}"
                raise ValueError(msg) from e
            raise

    def stop(self) -> StopResponse:
        """
        Stop the current session.

        """
        try:
            return cast(
                "StopResponse",
                self._get("/dl_cgi", StopResponse, params={"Command": "Stop"}),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                msg = f"Stop failed: {e.response.json()}"
                raise ValueError(msg) from e
            raise


class NetworkClient(BaseClient):
    """Client for network operations."""

    def list(self) -> GetCommResponse:
        """
        Get the list of network interfaces.

        Returns:
            The list of network interfaces

        Raises:
            ValueError: If the operation fails

        """
        try:
            return cast(
                "GetCommResponse",
                self._get(
                    "/dl_cgi",
                    GetCommResponse,
                    params={"Command": "Get_Comm", "SerialNumber": self.serial},
                ),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                msg = f"Failed to list interfaces: {e.response.json()}"
                raise ValueError(msg) from e
            raise


class DeviceClient(BaseClient):
    """Client for device operations."""

    def list(self) -> DeviceDetailResponse:
        """
        Get the discovery progress.

        Returns:
            The discovery progress

        """
        response: dict = self._get("/dl_cgi", params={"Command": "DeviceList"})
        return DeviceDetailResponse.new(response)


class FirmwareClient(BaseClient):
    """Client for firmware operations."""

    def check(self) -> CheckFWResponse:
        """
        See if we need new firmware.

        Returns:
            The firmware information

        Raises:
            ValueError: If the operation fails

        """
        try:
            return cast(
                "CheckFWResponse",
                self._get("/dl_cgi", CheckFWResponse, params={"Command": "CheckFW"}),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                msg = f"Failed to get firmware info: {e.response.json()}"
                raise ValueError(msg) from e
            raise


class GridProfileClient(BaseClient):
    """Client for grid profile operations."""

    def get(self) -> GridProfileGetResponse:
        """
        Get the list of grid profiles.

        Returns:
            The current grid profile

        Raises:
            ValueError: If the operation fails

        """
        try:
            return cast(
                "GridProfileGetResponse",
                self._get(
                    "/dl_cgi",
                    GridProfileGetResponse,
                    params={"Command": "GridProfileGet"},
                ),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                msg = f"Failed to get grid profiles: {e.response.json()}"
                raise ValueError(msg) from e
            raise

    def refresh(self) -> GridProfileRefreshResponse:
        """
        Refresh the list of grid profiles.

        Returns:
            The grid profile refresh response

        Raises:
            ValueError: If the operation fails

        """
        try:
            return cast(
                "GridProfileRefreshResponse",
                self._get(
                    "/dl_cgi",
                    GridProfileRefreshResponse,
                    params={"Command": "GridProfileRefreshResponse"},
                ),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                msg = f"Failed to get grid profile status: {e.response.json()}"
                raise ValueError(msg) from e
            raise


class SungazerClient:
    """Client for interacting with the Sungazer PVS6 API."""

    def __init__(
        self,
        base_url: str = "http://sunpowerconsole.com/cgi-bin",
        timeout: int = 30,
        serial: str | None = None,
    ):
        """
        Initialize the Sungazer client.

        Args:
            base_url: The base URL for the API
            timeout: Request timeout in seconds
            serial: The serial number of the PVS6 device

        """
        self.base_url = base_url
        self.serial = serial
        self.client = httpx.Client(base_url=base_url, timeout=timeout, verify=False)  # noqa: S501

        # Initialize specialized clients
        self.session = SessionClient(self.client, serial=serial)
        self.network = NetworkClient(self.client, serial=serial)
        self.devices = DeviceClient(self.client, serial=serial)
        self.firmware = FirmwareClient(self.client, serial=serial)
        self.grid_profiles = GridProfileClient(self.client, serial=serial)

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager and close the client."""
        self.close()

    def close(self):
        """Close the client."""
        self.client.close()
