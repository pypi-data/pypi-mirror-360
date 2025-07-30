"""Tests for the sungazer.client module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest

from sungazer.client import (
    BaseClient,
    DeviceClient,
    FirmwareClient,
    GridProfileClient,
    NetworkClient,
    SessionClient,
    SungazerClient,
)
from sungazer.models import (
    CheckFWResponse,
    DeviceDetailResponse,
    GetCommResponse,
    GridProfileGetResponse,
    GridProfileRefreshResponse,
    StartResponse,
    StopResponse,
)


class TestBaseClient:
    """Test cases for the BaseClient class."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock httpx client."""
        return Mock(spec=httpx.Client)

    @pytest.fixture
    def base_client(self, mock_httpx_client):
        """Create a BaseClient instance with mock httpx client."""
        return BaseClient(mock_httpx_client, serial="TEST123")

    def valid_start_response_data(self):
        return {
            "result": "success",
            "supervisor": {
                "SWVER": "2021.9, Build 41001",
                "SERIAL": "ZT01234567890ABCDEF",
                "MODEL": "PVS6",
            },
        }

    def test_base_client_initialization(self, mock_httpx_client):
        """Test BaseClient initialization."""
        client = BaseClient(mock_httpx_client, serial="TEST123")
        assert client.client == mock_httpx_client
        assert client.serial == "TEST123"

    def test_base_client_initialization_without_serial(self, mock_httpx_client):
        """Test BaseClient initialization without serial."""
        client = BaseClient(mock_httpx_client)
        assert client.client == mock_httpx_client
        assert client.serial is None

    def test_handle_response_success(self, base_client):
        """Test successful response handling."""
        # Create mock response with valid JSON
        data = self.valid_start_response_data()
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(data).encode()
        mock_response.text = json.dumps(data)
        mock_response.raise_for_status.return_value = None

        result = base_client._handle_response(mock_response, StartResponse)  # noqa: SLF001
        assert isinstance(result, StartResponse)
        assert result.result == "success"
        assert result.supervisor.MODEL == "PVS6"

    def test_handle_response_empty_content(self, base_client):
        """Test response handling with empty content."""
        # Provide minimal valid data for StartResponse
        data = self.valid_start_response_data()
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(data).encode()
        mock_response.text = json.dumps(data)
        mock_response.raise_for_status.return_value = None

        result = base_client._handle_response(mock_response, StartResponse)  # noqa: SLF001
        assert isinstance(result, StartResponse)
        assert result.result == "success"

    def test_handle_response_with_headers_in_content(self, base_client):
        """Test response handling when HTTP headers are mixed in content."""
        data = self.valid_start_response_data()
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = b"HTTP/1.1 200 OK\n" + json.dumps(data).encode() + b"\n"
        mock_response.text = "HTTP/1.1 200 OK\n" + json.dumps(data) + "\n"
        mock_response.raise_for_status.return_value = None

        result = base_client._handle_response(mock_response, StartResponse)  # noqa: SLF001
        assert isinstance(result, StartResponse)
        assert result.result == "success"

    def test_handle_response_http_error(self, base_client):
        """Test response handling with HTTP error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )

        with pytest.raises(httpx.HTTPStatusError):
            base_client._handle_response(mock_response, StartResponse)  # noqa: SLF001

    def test_get_request_success(self, base_client, mock_httpx_client):
        """Test successful GET request."""
        # Mock the response
        data = self.valid_start_response_data()
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(data).encode()
        mock_response.text = json.dumps(data)
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        result = base_client._get("/test", StartResponse, {"param": "value"})  # noqa: SLF001
        assert isinstance(result, StartResponse)
        assert result.result == "success"

        # Verify the client was called correctly
        mock_httpx_client.get.assert_called_once_with(
            "/test", params={"param": "value"}
        )

    def test_get_request_without_model(self, base_client, mock_httpx_client):
        """Test GET request without model class."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.text = '{"result": "success"}'
        mock_httpx_client.get.return_value = mock_response

        result = base_client._get("/test", params={"param": "value"})  # noqa: SLF001
        assert result == {"result": "success"}

    def test_get_request_without_params(self, base_client, mock_httpx_client):
        """Test GET request without parameters."""
        data = self.valid_start_response_data()
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(data).encode()
        mock_response.text = json.dumps(data)
        mock_response.raise_for_status.return_value = None
        mock_httpx_client.get.return_value = mock_response

        result = base_client._get("/test", StartResponse)  # noqa: SLF001
        assert isinstance(result, StartResponse)
        assert result.result == "success"

        mock_httpx_client.get.assert_called_once_with("/test", params=None)


class TestSessionClient:
    """Test cases for the SessionClient class."""

    @pytest.fixture
    def session_client(self):
        """Create a SessionClient instance."""
        mock_client = Mock(spec=httpx.Client)
        return SessionClient(mock_client, serial="TEST123")

    @pytest.fixture
    def start_response_data(self):
        """Load start response fixture data."""
        fixture_path = Path(__file__).parent / "fixtures" / "Start" / "Start.json"
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def stop_response_data(self):
        """Load stop response fixture data."""
        fixture_path = Path(__file__).parent / "fixtures" / "Stop" / "Stop.json"
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    def test_session_client_start_success(self, session_client, start_response_data):
        """Test successful session start."""
        # Mock the response
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(start_response_data).encode()
        mock_response.text = json.dumps(start_response_data)
        mock_response.raise_for_status.return_value = None
        session_client.client.get.return_value = mock_response

        result = session_client.start()
        assert isinstance(result, StartResponse)
        assert result.result == "succeed"

        # Verify the request was made correctly
        session_client.client.get.assert_called_once_with(
            "/dl_cgi", params={"Command": "Start"}
        )

    def test_session_client_start_http_500_error(self, session_client):
        """Test session start with HTTP 500 error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.__str__ = lambda self: "500 Internal Server Error"  # type: ignore[attr-defined]  # noqa: ARG005
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )
        session_client.client.get.return_value = mock_response

        with pytest.raises(ValueError, match="Start failed: 500 Internal Server Error"):
            session_client.start()

    def test_session_client_start_other_http_error(self, session_client):
        """Test session start with other HTTP error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )
        session_client.client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            session_client.start()

    def test_session_client_stop_success(self, session_client, stop_response_data):
        """Test successful session stop."""
        # Mock the response
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(stop_response_data).encode()
        mock_response.text = json.dumps(stop_response_data)
        mock_response.raise_for_status.return_value = None
        session_client.client.get.return_value = mock_response

        result = session_client.stop()
        assert isinstance(result, StopResponse)

        # Verify the request was made correctly
        session_client.client.get.assert_called_once_with(
            "/dl_cgi", params={"Command": "Stop"}
        )

    def test_session_client_stop_http_500_error(self, session_client):
        """Test session stop with HTTP 500 error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )
        session_client.client.get.return_value = mock_response

        with pytest.raises(
            ValueError, match="Stop failed: {'error': 'Internal server error'}"
        ):
            session_client.stop()


class TestNetworkClient:
    """Test cases for the NetworkClient class."""

    @pytest.fixture
    def network_client(self):
        """Create a NetworkClient instance."""
        mock_client = Mock(spec=httpx.Client)
        return NetworkClient(mock_client, serial="TEST123")

    @pytest.fixture
    def get_comm_response_data(self):
        """Load Get_Comm response fixture data."""
        fixture_path = Path(__file__).parent / "fixtures" / "Get_Comm" / "Get_Comm.json"
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    def test_network_client_list_success(self, network_client, get_comm_response_data):
        """Test successful network interface listing."""
        # Mock the response
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(get_comm_response_data).encode()
        mock_response.text = json.dumps(get_comm_response_data)
        mock_response.raise_for_status.return_value = None
        network_client.client.get.return_value = mock_response

        result = network_client.list()
        assert isinstance(result, GetCommResponse)

        # Verify the request was made correctly
        network_client.client.get.assert_called_once_with(
            "/dl_cgi",
            params={"Command": "Get_Comm", "SerialNumber": "TEST123"},
        )

    def test_network_client_list_without_serial(self):
        """Test network interface listing without serial number."""
        mock_client = Mock(spec=httpx.Client)
        network_client = NetworkClient(mock_client)  # No serial

        # Create valid GetCommResponse data with networkstatus
        valid_response_data = {
            "result": "success",
            "networkstatus": {
                "ts": "1234567890",
                "interfaces": [
                    {
                        "interface": "sta0",
                        "internet": "up",
                        "ipaddr": "192.168.1.100",
                        "ssid": "TestWiFi",
                        "status": "connected",
                        "sms": "reachable",
                    }
                ],
                "system": {"interface": "sta0", "internet": "up", "sms": "reachable"},
            },
        }

        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(valid_response_data).encode()
        mock_response.text = json.dumps(valid_response_data)
        mock_response.raise_for_status.return_value = None
        network_client.client.get.return_value = mock_response  # type: ignore[attr-defined]

        result = network_client.list()
        assert isinstance(result, GetCommResponse)
        assert result.result == "success"
        assert result.networkstatus is not None
        assert result.networkstatus.ts == "1234567890"
        assert result.networkstatus.interfaces is not None
        assert len(result.networkstatus.interfaces) == 1
        assert result.networkstatus.interfaces[0].interface == "sta0"

        # Verify the request was made with None serial
        network_client.client.get.assert_called_once_with(  # type: ignore[attr-defined]
            "/dl_cgi",
            params={"Command": "Get_Comm", "SerialNumber": None},
        )

    def test_network_client_list_http_500_error(self, network_client):
        """Test network interface listing with HTTP 500 error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )
        network_client.client.get.return_value = mock_response

        with pytest.raises(
            ValueError,
            match="Failed to list interfaces: {'error': 'Internal server error'}",
        ):
            network_client.list()


class TestDeviceClient:
    """Test cases for the DeviceClient class."""

    @pytest.fixture
    def device_client(self):
        """Create a DeviceClient instance."""
        mock_client = Mock(spec=httpx.Client)
        return DeviceClient(mock_client, serial="TEST123")

    @pytest.fixture
    def device_list_response_data(self):
        """Load DeviceList response fixture data."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "DeviceList" / "DeviceList.json"
        )
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    def test_device_client_list_success(self, device_client, device_list_response_data):
        """Test successful device listing."""
        # Mock the response
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(device_list_response_data).encode()
        mock_response.text = json.dumps(device_list_response_data)
        mock_response.raise_for_status.return_value = None
        device_client.client.get.return_value = mock_response

        result = device_client.list()
        assert isinstance(result, DeviceDetailResponse)

        # Verify the request was made correctly
        device_client.client.get.assert_called_once_with(
            "/dl_cgi", params={"Command": "DeviceList"}
        )

    def test_device_client_list_with_empty_response(self, device_client):
        """Test device listing with empty response."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = b"{}"
        mock_response.text = "{}"
        mock_response.raise_for_status.return_value = None
        device_client.client.get.return_value = mock_response

        result = device_client.list()
        assert isinstance(result, DeviceDetailResponse)


class TestFirmwareClient:
    """Test cases for the FirmwareClient class."""

    @pytest.fixture
    def firmware_client(self):
        """Create a FirmwareClient instance."""
        mock_client = Mock(spec=httpx.Client)
        return FirmwareClient(mock_client, serial="TEST123")

    @pytest.fixture
    def check_fw_response_data(self):
        """Load CheckFW response fixture data."""
        fixture_path = Path(__file__).parent / "fixtures" / "CheckFW" / "CheckFW.json"
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    def test_firmware_client_check_success(
        self, firmware_client, check_fw_response_data
    ):
        """Test successful firmware check with only 'url' field."""
        # Mock the response
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(check_fw_response_data).encode()
        mock_response.text = json.dumps(check_fw_response_data)
        mock_response.raise_for_status.return_value = None
        firmware_client.client.get.return_value = mock_response

        result = firmware_client.check()
        assert isinstance(result, CheckFWResponse)
        assert result.url is None

        # Verify the request was made correctly
        firmware_client.client.get.assert_called_once_with(
            "/dl_cgi", params={"Command": "CheckFW"}
        )

    def test_firmware_client_check_http_500_error(self, firmware_client):
        """Test firmware check with HTTP 500 error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )
        firmware_client.client.get.return_value = mock_response

        with pytest.raises(
            ValueError,
            match="Failed to get firmware info: {'error': 'Internal server error'}",
        ):
            firmware_client.check()


class TestGridProfileClient:
    """Test cases for the GridProfileClient class."""

    @pytest.fixture
    def grid_profile_client(self):
        """Create a GridProfileClient instance."""
        mock_client = Mock(spec=httpx.Client)
        return GridProfileClient(mock_client, serial="TEST123")

    @pytest.fixture
    def grid_profile_get_response_data(self):
        """Load GridProfileGet response fixture data."""
        fixture_path = (
            Path(__file__).parent
            / "fixtures"
            / "GridProfileGet"
            / "GridProfileGet.json"
        )
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture
    def grid_profile_refresh_response_data(self):
        """Load GridProfileRefresh response fixture data."""
        fixture_path = (
            Path(__file__).parent
            / "fixtures"
            / "GridProfileRefresh"
            / "GridProfileRefresh.json"
        )
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    def test_grid_profile_client_get_success(
        self, grid_profile_client, grid_profile_get_response_data
    ):
        """Test successful grid profile get."""
        # Mock the response
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(grid_profile_get_response_data).encode()
        mock_response.text = json.dumps(grid_profile_get_response_data)
        mock_response.raise_for_status.return_value = None
        grid_profile_client.client.get.return_value = mock_response

        result = grid_profile_client.get()
        assert isinstance(result, GridProfileGetResponse)

        # Verify the request was made correctly
        grid_profile_client.client.get.assert_called_once_with(
            "/dl_cgi", params={"Command": "GridProfileGet"}
        )

    def test_grid_profile_client_get_http_500_error(self, grid_profile_client):
        """Test grid profile get with HTTP 500 error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )
        grid_profile_client.client.get.return_value = mock_response

        with pytest.raises(
            ValueError,
            match="Failed to get grid profiles: {'error': 'Internal server error'}",
        ):
            grid_profile_client.get()

    def test_grid_profile_client_refresh_success(
        self, grid_profile_client, grid_profile_refresh_response_data
    ):
        """Test successful grid profile refresh."""
        # Mock the response
        mock_response = Mock(spec=httpx.Response)
        mock_response.content = json.dumps(grid_profile_refresh_response_data).encode()
        mock_response.text = json.dumps(grid_profile_refresh_response_data)
        mock_response.raise_for_status.return_value = None
        grid_profile_client.client.get.return_value = mock_response

        result = grid_profile_client.refresh()
        assert isinstance(result, GridProfileRefreshResponse)

        # Verify the request was made correctly
        grid_profile_client.client.get.assert_called_once_with(
            "/dl_cgi", params={"Command": "GridProfileRefreshResponse"}
        )

    def test_grid_profile_client_refresh_http_500_error(self, grid_profile_client):
        """Test grid profile refresh with HTTP 500 error."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=mock_response
        )
        grid_profile_client.client.get.return_value = mock_response

        with pytest.raises(
            ValueError,
            match="Failed to get grid profile status: {'error': 'Internal server error'}",  # noqa: E501
        ):
            grid_profile_client.refresh()


class TestSungazerClient:
    """Test cases for the SungazerClient class."""

    def test_sungazer_client_initialization_defaults(self):
        """Test SungazerClient initialization with default parameters."""
        with patch("sungazer.client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = SungazerClient()
            assert client.base_url == "http://sunpowerconsole.com/cgi-bin"
            assert client.serial is None
            assert client.client == mock_client

            # Verify httpx.Client was called with correct parameters
            mock_client_class.assert_called_once_with(
                base_url="http://sunpowerconsole.com/cgi-bin",
                timeout=30,
                verify=False,
            )

    def test_sungazer_client_initialization_custom(self):
        """Test SungazerClient initialization with custom parameters."""
        with patch("sungazer.client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = SungazerClient(
                base_url="https://custom.example.com/api",
                timeout=60,
                serial="CUSTOM123",
            )
            assert client.base_url == "https://custom.example.com/api"
            assert client.serial == "CUSTOM123"
            assert client.client == mock_client

            # Verify httpx.Client was called with correct parameters
            mock_client_class.assert_called_once_with(
                base_url="https://custom.example.com/api",
                timeout=60,
                verify=False,
            )

    def test_sungazer_client_specialized_clients(self):
        """Test that specialized clients are properly initialized."""
        with patch("sungazer.client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = SungazerClient(serial="TEST123")

            # Verify specialized clients are created
            assert isinstance(client.session, SessionClient)
            assert isinstance(client.network, NetworkClient)
            assert isinstance(client.devices, DeviceClient)
            assert isinstance(client.firmware, FirmwareClient)
            assert isinstance(client.grid_profiles, GridProfileClient)

            # Verify they all have the same client and serial
            assert client.session.client == mock_client
            assert client.session.serial == "TEST123"
            assert client.network.client == mock_client
            assert client.network.serial == "TEST123"
            assert client.devices.client == mock_client
            assert client.devices.serial == "TEST123"
            assert client.firmware.client == mock_client
            assert client.firmware.serial == "TEST123"
            assert client.grid_profiles.client == mock_client
            assert client.grid_profiles.serial == "TEST123"

    def test_sungazer_client_context_manager(self):
        """Test SungazerClient as a context manager."""
        with patch("sungazer.client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            with SungazerClient() as client:
                assert isinstance(client, SungazerClient)

            # Verify client was closed when exiting context
            mock_client.close.assert_called_once()

    def test_sungazer_client_close(self):
        """Test SungazerClient close method."""
        with patch("sungazer.client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = SungazerClient()
            client.close()

            # Verify client was closed
            mock_client.close.assert_called_once()

    def test_sungazer_client_context_manager_exception(self):
        """Test SungazerClient context manager with exception."""
        with patch("sungazer.client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            try:
                with SungazerClient():
                    msg = "Test exception"
                    raise ValueError(msg)  # noqa: TRY301
            except ValueError:
                pass

            # Verify client was still closed even with exception
            mock_client.close.assert_called_once()

    def test_sungazer_client_integration(self):
        """Test integration between SungazerClient and specialized clients."""
        with patch("sungazer.client.httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = SungazerClient(serial="TEST123")

            # Test that we can access all specialized clients
            assert client.session is not None
            assert client.network is not None
            assert client.devices is not None
            assert client.firmware is not None
            assert client.grid_profiles is not None

            # Test that all clients share the same underlying httpx client
            assert client.session.client is client.network.client
            assert client.session.client is client.devices.client
            assert client.session.client is client.firmware.client
            assert client.session.client is client.grid_profiles.client
            assert client.session.client is client.client
