"""Tests for the GridProfileGetResponse model."""  # noqa: N999

import json
from pathlib import Path

import pytest

from sungazer.models.grid import GridProfileGetResponse


class TestGridProfileGetResponse:
    """Test cases for the GridProfileGetResponse model."""

    @pytest.fixture
    def sample_data(self) -> dict:
        """Load sample data from fixture file."""
        fixture_path = (
            Path(__file__).parent
            / "fixtures"
            / "GridProfileGet"
            / "GridProfileGet.json"
        )
        with Path(fixture_path).open(encoding="utf-8") as f:
            return json.load(f)

    def test_grid_profile_get_response_from_fixture(self, sample_data: dict) -> None:
        """Test GridProfileGetResponse parsing from fixture data."""
        response = GridProfileGetResponse(**sample_data)

        assert response.result == "succeed"
        assert response.active_name == "IEEE-1547a-2014 + 2020 CA Rule21"
        assert response.active_id == "816bf3302d337a42680b996227ddbc46abf9cd05"
        assert response.pending_name == "IEEE-1547a-2014 + 2020 CA Rule21"
        assert response.pending_id == "816bf3302d337a42680b996227ddbc46abf9cd05"
        assert response.percent == 100
        assert response.supported_by == "ALL"
        assert response.status == "success"

    def test_grid_profile_get_response_with_minimal_data(self) -> None:
        """Test GridProfileGetResponse with only required fields."""
        data = {"result": "succeed"}
        response = GridProfileGetResponse(**data)  # type: ignore[arg-type]

        assert response.result == "succeed"
        assert response.active_name is None
        assert response.active_id is None
        assert response.pending_name is None
        assert response.pending_id is None
        assert response.percent is None
        assert response.supported_by is None
        assert response.status is None

    def test_grid_profile_get_response_with_all_fields(self) -> None:
        """
        Test GridProfileGetResponse with all fields populated.

        Note:
            We don't actually know all the valid values for supported_by.
            We've only seen ALL so far, but might as well test with other values.

        """
        data = {
            "result": "succeed",
            "active_name": "Test Active Profile",
            "active_id": "active123456789",
            "pending_name": "Test Pending Profile",
            "pending_id": "pending123456789",
            "percent": 75,
            "supported_by": "INVERTER",
            "status": "in_progress",
        }
        response = GridProfileGetResponse(**data)

        assert response.result == "succeed"
        assert response.active_name == "Test Active Profile"
        assert response.active_id == "active123456789"
        assert response.pending_name == "Test Pending Profile"
        assert response.pending_id == "pending123456789"
        assert response.percent == 75
        assert response.supported_by == "INVERTER"
        assert response.status == "in_progress"

    def test_grid_profile_get_response_with_none_values(self) -> None:
        """Test GridProfileGetResponse with explicit None values."""
        data = {
            "result": "succeed",
            "active_name": None,
            "active_id": None,
            "pending_name": None,
            "pending_id": None,
            "percent": None,
            "supported_by": None,
            "status": None,
        }
        response = GridProfileGetResponse(**data)

        assert response.result == "succeed"
        assert response.active_name is None
        assert response.active_id is None
        assert response.pending_name is None
        assert response.pending_id is None
        assert response.percent is None
        assert response.supported_by is None
        assert response.status is None

    def test_grid_profile_get_response_missing_required_field(self) -> None:
        """Test GridProfileGetResponse with missing required result field."""
        data = {"active_name": "Test Profile", "active_id": "test123"}

        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            GridProfileGetResponse(**data)  # type: ignore[arg-type]

        assert "result" in str(exc_info.value)

    def test_grid_profile_get_response_with_zero_percent(self) -> None:
        """Test GridProfileGetResponse with 0 percent completion."""
        data = {"result": "succeed", "percent": 0}
        response = GridProfileGetResponse(**data)

        assert response.result == "succeed"
        assert response.percent == 0

    def test_grid_profile_get_response_with_high_percent(self) -> None:
        """Test GridProfileGetResponse with 100 percent completion."""
        data = {"result": "succeed", "percent": 100}
        response = GridProfileGetResponse(**data)

        assert response.result == "succeed"
        assert response.percent == 100

    def test_grid_profile_get_response_with_different_supported_by_values(self) -> None:
        """Test GridProfileGetResponse with different supported_by values."""
        test_cases = ["ALL", "INVERTER", "BATTERY", "GATEWAY"]

        for supported_by in test_cases:
            data = {"result": "succeed", "supported_by": supported_by}
            response = GridProfileGetResponse(**data)  # type: ignore[arg-type]

            assert response.result == "succeed"
            assert response.supported_by == supported_by

    def test_grid_profile_get_response_with_different_status_values(self) -> None:
        """Test GridProfileGetResponse with different status values."""
        test_cases = ["success", "in_progress", "failed", "pending"]

        for status in test_cases:
            data = {"result": "succeed", "status": status}
            response = GridProfileGetResponse(**data)  # type: ignore[arg-type]

            assert response.result == "succeed"
            assert response.status == status

    def test_grid_profile_get_response_with_long_profile_names(self) -> None:
        """Test GridProfileGetResponse with long profile names."""
        long_name = "Very Long Grid Profile Name That Exceeds Normal Length " * 5
        data = {
            "result": "succeed",
            "active_name": long_name,
            "pending_name": long_name,
        }
        response = GridProfileGetResponse(**data)  # type: ignore[arg-type]

        assert response.result == "succeed"
        assert response.active_name == long_name
        assert response.pending_name == long_name

    def test_grid_profile_get_response_with_special_characters(self) -> None:
        """Test GridProfileGetResponse with special characters in names."""
        special_name = "Profile with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        data = {
            "result": "succeed",
            "active_name": special_name,
            "pending_name": special_name,
        }
        response = GridProfileGetResponse(**data)  # type: ignore[arg-type]

        assert response.result == "succeed"
        assert response.active_name == special_name
        assert response.pending_name == special_name
