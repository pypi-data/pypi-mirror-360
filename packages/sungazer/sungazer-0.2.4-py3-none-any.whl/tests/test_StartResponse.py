"""Tests for the StartResponse model."""  # noqa: N999

import json
from pathlib import Path

import pytest

from sungazer.models.session import StartResponse, Supervisor


class TestStartResponse:
    """Test cases for the StartResponse model."""

    @pytest.fixture
    def sample_data(self) -> dict:
        """Load sample data from fixture file."""
        fixture_path = Path(__file__).parent / "fixtures" / "Start" / "Start.json"
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    def test_start_response_from_fixture(self, sample_data: dict) -> None:
        """Test StartResponse parsing from fixture data."""
        response = StartResponse(**sample_data)  # type: ignore[arg-type]

        assert response.result == "succeed"
        assert response.supervisor is not None
        assert response.supervisor.SWVER == "2025.06, Build 61839"
        assert response.supervisor.SERIAL == "ZT214285000549A0621"
        assert response.supervisor.MODEL == "PVS6"
        assert response.supervisor.FWVER == "1.0.0"
        assert response.supervisor.SCVER == 1630652920
        assert response.supervisor.EASICVER == 131329
        assert response.supervisor.SCBUILD == 1188
        assert response.supervisor.WNMODEL == 400
        assert response.supervisor.WNVER == 3000
        assert response.supervisor.WNSERIAL == 16
        assert response.supervisor.BUILD == 61839

    def test_start_response_with_minimal_data(self) -> None:
        """Test StartResponse with minimal data."""
        supervisor_data = {
            "SWVER": "2021.9, Build 41001",
            "SERIAL": "ZT01234567890ABCDEF",
            "MODEL": "PVS6",
        }
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SWVER == "2021.9, Build 41001"
        assert response.supervisor.SERIAL == "ZT01234567890ABCDEF"
        assert response.supervisor.MODEL == "PVS6"
        assert response.supervisor.FWVER is None
        assert response.supervisor.SCVER is None
        assert response.supervisor.EASICVER is None
        assert response.supervisor.SCBUILD is None
        assert response.supervisor.WNMODEL is None
        assert response.supervisor.WNVER is None
        assert response.supervisor.WNSERIAL is None
        assert response.supervisor.BUILD is None

    def test_start_response_with_all_fields(self) -> None:
        """Test StartResponse with all supervisor fields populated."""
        supervisor_data = {
            "SWVER": "2022.3, Build 52000",
            "SERIAL": "ZT9876543210FEDCBA",
            "MODEL": "PVS6",
            "FWVER": "2.1.0",
            "SCVER": 18000,
            "EASICVER": 140000,
            "SCBUILD": 2000,
            "WNMODEL": 500,
            "WNVER": 3500,
            "WNSERIAL": 20,
            "BUILD": 52000,
        }
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SWVER == "2022.3, Build 52000"
        assert response.supervisor.SERIAL == "ZT9876543210FEDCBA"
        assert response.supervisor.MODEL == "PVS6"
        assert response.supervisor.FWVER == "2.1.0"
        assert response.supervisor.SCVER == 18000
        assert response.supervisor.EASICVER == 140000
        assert response.supervisor.SCBUILD == 2000
        assert response.supervisor.WNMODEL == 500
        assert response.supervisor.WNVER == 3500
        assert response.supervisor.WNSERIAL == 20
        assert response.supervisor.BUILD == 52000

    def test_start_response_with_none_supervisor_values(self) -> None:
        """Test StartResponse with explicit None values in supervisor."""
        supervisor_data = {
            "SWVER": None,
            "SERIAL": None,
            "MODEL": None,
            "FWVER": None,
            "SCVER": None,
            "EASICVER": None,
            "SCBUILD": None,
            "WNMODEL": None,
            "WNVER": None,
            "WNSERIAL": None,
            "BUILD": None,
        }
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SWVER is None
        assert response.supervisor.SERIAL is None
        assert response.supervisor.MODEL is None
        assert response.supervisor.FWVER is None
        assert response.supervisor.SCVER is None
        assert response.supervisor.EASICVER is None
        assert response.supervisor.SCBUILD is None
        assert response.supervisor.WNMODEL is None
        assert response.supervisor.WNVER is None
        assert response.supervisor.WNSERIAL is None
        assert response.supervisor.BUILD is None

    def test_start_response_with_empty_strings(self) -> None:
        """Test StartResponse with empty string values in supervisor."""
        supervisor_data = {"SWVER": "", "SERIAL": "", "MODEL": "", "FWVER": ""}
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SWVER == ""
        assert response.supervisor.SERIAL == ""
        assert response.supervisor.MODEL == ""
        assert response.supervisor.FWVER == ""

    def test_start_response_with_zero_values(self) -> None:
        """Test StartResponse with zero numeric values in supervisor."""
        supervisor_data = {
            "SCVER": 0,
            "EASICVER": 0,
            "SCBUILD": 0,
            "WNMODEL": 0,
            "WNVER": 0,
            "WNSERIAL": 0,
            "BUILD": 0,
        }
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SCVER == 0
        assert response.supervisor.EASICVER == 0
        assert response.supervisor.SCBUILD == 0
        assert response.supervisor.WNMODEL == 0
        assert response.supervisor.WNVER == 0
        assert response.supervisor.WNSERIAL == 0
        assert response.supervisor.BUILD == 0

    def test_start_response_with_large_numbers(self) -> None:
        """Test StartResponse with large numeric values in supervisor."""
        supervisor_data = {
            "SCVER": 999999,
            "EASICVER": 999999,
            "SCBUILD": 999999,
            "WNMODEL": 999999,
            "WNVER": 999999,
            "WNSERIAL": 999999,
            "BUILD": 999999,
        }
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SCVER == 999999
        assert response.supervisor.EASICVER == 999999
        assert response.supervisor.SCBUILD == 999999
        assert response.supervisor.WNMODEL == 999999
        assert response.supervisor.WNVER == 999999
        assert response.supervisor.WNSERIAL == 999999
        assert response.supervisor.BUILD == 999999

    def test_start_response_with_special_characters_in_strings(self) -> None:
        """Test StartResponse with special characters in supervisor string fields."""
        supervisor_data = {
            "SWVER": "2021.9, Build 41001 (Stable)",
            "SERIAL": "ZT01234567890ABCDEF_2023",
            "MODEL": "PVS6-Pro",
            "FWVER": "1.0.0-beta+rc1",
        }
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SWVER == "2021.9, Build 41001 (Stable)"
        assert response.supervisor.SERIAL == "ZT01234567890ABCDEF_2023"
        assert response.supervisor.MODEL == "PVS6-Pro"
        assert response.supervisor.FWVER == "1.0.0-beta+rc1"

    def test_start_response_with_long_strings(self) -> None:
        """Test StartResponse with long string values in supervisor."""
        long_string = "Very Long String Value " * 10
        supervisor_data = {
            "SWVER": long_string,
            "SERIAL": long_string,
            "MODEL": long_string,
            "FWVER": long_string,
        }
        data = {"result": "success", "supervisor": supervisor_data}
        response = StartResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"
        assert response.supervisor is not None
        assert response.supervisor.SWVER == long_string
        assert response.supervisor.SERIAL == long_string
        assert response.supervisor.MODEL == long_string
        assert response.supervisor.FWVER == long_string

    def test_start_response_missing_required_result_field(self) -> None:
        """Test StartResponse with missing required result field."""
        supervisor_data = {
            "SWVER": "2021.9, Build 41001",
            "SERIAL": "ZT01234567890ABCDEF",
            "MODEL": "PVS6",
        }
        data = {"supervisor": supervisor_data}

        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            StartResponse(**data)  # type: ignore[arg-type]

        assert "result" in str(exc_info.value)

    def test_start_response_missing_required_supervisor_field(self) -> None:
        """Test StartResponse with missing required supervisor field."""
        data = {"result": "success"}

        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            StartResponse(**data)  # type: ignore[arg-type]

        assert "supervisor" in str(exc_info.value)

    def test_start_response_with_different_result_values(self) -> None:
        """Test StartResponse with different result values."""
        supervisor_data = {
            "SWVER": "2021.9, Build 41001",
            "SERIAL": "ZT01234567890ABCDEF",
            "MODEL": "PVS6",
        }
        test_cases = ["success", "succeed", "failed", "error"]

        for result in test_cases:
            data = {"result": result, "supervisor": supervisor_data}
            response = StartResponse(**data)  # type: ignore[arg-type]

            assert response.result == result
            assert response.supervisor is not None
            assert response.supervisor.SWVER == "2021.9, Build 41001"


class TestSupervisor:
    """Test cases for the Supervisor model."""

    def test_supervisor_with_all_fields(self) -> None:
        """Test Supervisor model with all fields populated."""
        data = {
            "SWVER": "2022.3, Build 52000",
            "SERIAL": "ZT9876543210FEDCBA",
            "MODEL": "PVS6",
            "FWVER": "2.1.0",
            "SCVER": 18000,
            "EASICVER": 140000,
            "SCBUILD": 2000,
            "WNMODEL": 500,
            "WNVER": 3500,
            "WNSERIAL": 20,
            "BUILD": 52000,
        }
        supervisor = Supervisor(**data)  # type: ignore[arg-type]

        assert supervisor.SWVER == "2022.3, Build 52000"
        assert supervisor.SERIAL == "ZT9876543210FEDCBA"
        assert supervisor.MODEL == "PVS6"
        assert supervisor.FWVER == "2.1.0"
        assert supervisor.SCVER == 18000
        assert supervisor.EASICVER == 140000
        assert supervisor.SCBUILD == 2000
        assert supervisor.WNMODEL == 500
        assert supervisor.WNVER == 3500
        assert supervisor.WNSERIAL == 20
        assert supervisor.BUILD == 52000

    def test_supervisor_with_minimal_data(self) -> None:
        """Test Supervisor model with minimal data."""
        data = {
            "SWVER": "2021.9, Build 41001",
            "SERIAL": "ZT01234567890ABCDEF",
            "MODEL": "PVS6",
        }
        supervisor = Supervisor(**data)  # type: ignore[arg-type]

        assert supervisor.SWVER == "2021.9, Build 41001"
        assert supervisor.SERIAL == "ZT01234567890ABCDEF"
        assert supervisor.MODEL == "PVS6"
        assert supervisor.FWVER is None
        assert supervisor.SCVER is None
        assert supervisor.EASICVER is None
        assert supervisor.SCBUILD is None
        assert supervisor.WNMODEL is None
        assert supervisor.WNVER is None
        assert supervisor.WNSERIAL is None
        assert supervisor.BUILD is None

    def test_supervisor_with_none_values(self) -> None:
        """Test Supervisor model with None values."""
        data = {
            "SWVER": None,
            "SERIAL": None,
            "MODEL": None,
            "FWVER": None,
            "SCVER": None,
            "EASICVER": None,
            "SCBUILD": None,
            "WNMODEL": None,
            "WNVER": None,
            "WNSERIAL": None,
            "BUILD": None,
        }
        supervisor = Supervisor(**data)  # type: ignore[arg-type]

        assert supervisor.SWVER is None
        assert supervisor.SERIAL is None
        assert supervisor.MODEL is None
        assert supervisor.FWVER is None
        assert supervisor.SCVER is None
        assert supervisor.EASICVER is None
        assert supervisor.SCBUILD is None
        assert supervisor.WNMODEL is None
        assert supervisor.WNVER is None
        assert supervisor.WNSERIAL is None
        assert supervisor.BUILD is None
