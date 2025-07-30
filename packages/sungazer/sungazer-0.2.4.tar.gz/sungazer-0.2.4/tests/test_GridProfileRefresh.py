# type: ignore  # noqa: N999, PGH003
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest  # noqa: F401

from sungazer.models import GridProfile, GridProfileRefreshResponse, Zipcode


def test_grid_profile_refresh_response_from_json():
    """Test GridProfileRefreshResponse parsing from real JSON data."""
    # Load test data from GridProfileRefresh.json
    data_path = (
        Path(__file__).parent
        / "fixtures"
        / "GridProfileRefresh"
        / "GridProfileRefresh.json"
    )
    with Path(data_path).open() as f:
        test_data = json.load(f)

    # Parse the response
    response = GridProfileRefreshResponse(**test_data)

    # Verify the response was parsed correctly
    assert isinstance(response, GridProfileRefreshResponse)
    assert response.result == "succeed"
    assert response.success is True
    assert isinstance(response.creation, datetime)
    assert response.creation == datetime.fromtimestamp(1600704253, tz=ZoneInfo("UTC"))
    assert response.profiles is not None
    assert len(response.profiles) > 0

    # Verify we have multiple profiles
    profiles = response.profiles
    assert len(profiles) == 63  # The fixture contains many profiles

    # Test specific profiles from the fixture
    heco_profile = next(p for p in profiles if p.name == "HECO OMH R14H (Legacy)")
    assert heco_profile.selfsupply is True
    assert heco_profile.default is False
    assert heco_profile.filename == "8c9c4170.meta"
    assert heco_profile.id == "8c9c4170457c88f6dcee7216357681d580a3b9bd"
    assert heco_profile.zipcodes is not None
    assert len(heco_profile.zipcodes) == 1
    assert heco_profile.zipcodes[0].min == 96701
    assert heco_profile.zipcodes[0].max == 96898

    # Test IEEE profile
    ieee_profile = next(p for p in profiles if p.name == "IEEE-1547a-2014")
    assert ieee_profile.selfsupply is False
    assert ieee_profile.default is False
    assert ieee_profile.filename == "471080f6.meta"
    assert ieee_profile.id == "471080f62a24d8be88f58864c398717c11bb876b"
    assert ieee_profile.zipcodes is not None
    assert len(ieee_profile.zipcodes) == 1
    assert ieee_profile.zipcodes[0].min == 0
    assert ieee_profile.zipcodes[0].max == 999999


def test_zipcode_model_parsing():
    """Test Zipcode model parsing with various values."""
    # Test normal zipcode range
    zipcode_data = {"min": 96701, "max": 96898}
    zipcode = Zipcode(**zipcode_data)
    assert zipcode.min == 96701
    assert zipcode.max == 96898

    # Test with None values
    zipcode_none_data = {"min": None, "max": None}
    zipcode_none = Zipcode(**zipcode_none_data)
    assert zipcode_none.min is None
    assert zipcode_none.max is None

    # Test with negative values (some profiles use -1 for "no restriction")
    zipcode_negative_data = {"min": -1, "max": -1}
    zipcode_negative = Zipcode(**zipcode_negative_data)
    assert zipcode_negative.min == -1
    assert zipcode_negative.max == -1

    # Test with large values
    zipcode_large_data = {"min": 0, "max": 999999}
    zipcode_large = Zipcode(**zipcode_large_data)
    assert zipcode_large.min == 0
    assert zipcode_large.max == 999999


def test_grid_profile_model_parsing():
    """Test GridProfile model parsing with various configurations."""
    # Test complete profile
    profile_data = {
        "selfsupply": True,
        "zipcodes": [{"min": 96701, "max": 96898}],
        "default": False,
        "filename": "test.meta",
        "id": "test-id-123",
        "name": "Test Profile",
    }
    profile = GridProfile(**profile_data)
    assert profile.selfsupply is True
    assert profile.default is False
    assert profile.filename == "test.meta"
    assert profile.id == "test-id-123"
    assert profile.name == "Test Profile"
    assert profile.zipcodes is not None
    assert len(profile.zipcodes) == 1
    assert profile.zipcodes[0].min == 96701
    assert profile.zipcodes[0].max == 96898

    # Test profile with None values
    profile_none_data = {
        "selfsupply": None,
        "zipcodes": None,
        "default": None,
        "filename": None,
        "id": None,
        "name": None,
    }
    profile_none = GridProfile(**profile_none_data)
    assert profile_none.selfsupply is None
    assert profile_none.zipcodes is None
    assert profile_none.default is None
    assert profile_none.filename is None
    assert profile_none.id is None
    assert profile_none.name is None

    # Test profile with empty zipcodes list
    profile_empty_zipcodes = {
        "selfsupply": False,
        "zipcodes": [],
        "default": True,
        "filename": "default.meta",
        "id": "default-id",
        "name": "Default Profile",
    }
    profile_empty = GridProfile(**profile_empty_zipcodes)
    assert profile_empty.selfsupply is False
    assert profile_empty.default is True
    assert profile_empty.zipcodes == []


def test_grid_profile_refresh_response_minimal():
    """Test GridProfileRefreshResponse with minimal data."""
    minimal_data = {
        "result": "succeed",
    }
    response = GridProfileRefreshResponse(**minimal_data)
    assert response.result == "succeed"
    assert response.success is True  # Default value
    assert response.creation is None
    assert response.profiles == []  # Default factory list

    # Test with explicit values
    explicit_data = {
        "result": "succeed",
        "success": False,
        "creation": 1600704253,
        "profiles": [],
    }
    response_explicit = GridProfileRefreshResponse(**explicit_data)
    assert response_explicit.result == "succeed"
    assert response_explicit.success is False
    assert isinstance(response_explicit.creation, datetime)
    assert response_explicit.creation == datetime.fromtimestamp(
        1600704253, tz=ZoneInfo("UTC")
    )
    assert response_explicit.profiles == []


def test_grid_profile_various_zipcode_formats():
    """Test GridProfile with various zipcode formats from the fixture."""
    # Test profile with range zipcodes (min/max objects)
    range_zipcode_data = {
        "selfsupply": True,
        "zipcodes": [{"min": 96701, "max": 96898}],
        "default": False,
        "filename": "range.meta",
        "id": "range-id",
        "name": "Range Zipcode Profile",
    }
    range_profile = GridProfile(**range_zipcode_data)
    assert len(range_profile.zipcodes) == 1
    assert range_profile.zipcodes[0].min == 96701
    assert range_profile.zipcodes[0].max == 96898

    # Test profile with negative zipcodes (no restriction)
    negative_zipcode_data = {
        "selfsupply": False,
        "zipcodes": [{"min": -1, "max": -1}],
        "default": False,
        "filename": "negative.meta",
        "id": "negative-id",
        "name": "Negative Zipcode Profile",
    }
    negative_profile = GridProfile(**negative_zipcode_data)
    assert len(negative_profile.zipcodes) == 1
    assert negative_profile.zipcodes[0].min == -1
    assert negative_profile.zipcodes[0].max == -1

    # Test profile with universal zipcodes (0 to 999999)
    universal_zipcode_data = {
        "selfsupply": False,
        "zipcodes": [{"min": 0, "max": 999999}],
        "default": False,
        "filename": "universal.meta",
        "id": "universal-id",
        "name": "Universal Zipcode Profile",
    }
    universal_profile = GridProfile(**universal_zipcode_data)
    assert len(universal_profile.zipcodes) == 1
    assert universal_profile.zipcodes[0].min == 0
    assert universal_profile.zipcodes[0].max == 999999


def test_creation_timestamp_parsing():
    """Test creation timestamp parsing in GridProfileRefreshResponse."""
    # Test with Unix timestamp
    timestamp_data = {
        "result": "succeed",
        "creation": 1600704253,
    }
    response = GridProfileRefreshResponse(**timestamp_data)
    assert isinstance(response.creation, datetime)
    assert response.creation == datetime.fromtimestamp(1600704253, tz=ZoneInfo("UTC"))

    # Test with string timestamp
    string_timestamp_data = {
        "result": "succeed",
        "creation": "1600704253",
    }
    response_string = GridProfileRefreshResponse(**string_timestamp_data)
    assert isinstance(response_string.creation, datetime)
    assert response_string.creation == datetime.fromtimestamp(
        1600704253, tz=ZoneInfo("UTC")
    )

    # Test with None creation
    none_timestamp_data = {
        "result": "succeed",
        "creation": None,
    }
    response_none = GridProfileRefreshResponse(**none_timestamp_data)
    assert response_none.creation is None

    # Test with missing creation field
    missing_timestamp_data = {
        "result": "succeed",
    }
    response_missing = GridProfileRefreshResponse(**missing_timestamp_data)
    assert response_missing.creation is None

    # Test with already parsed datetime object
    dt = datetime.fromtimestamp(1600704253, tz=ZoneInfo("UTC"))
    datetime_data = {
        "result": "succeed",
        "creation": dt,
    }
    response_dt = GridProfileRefreshResponse(**datetime_data)
    assert isinstance(response_dt.creation, datetime)
    assert response_dt.creation == dt
