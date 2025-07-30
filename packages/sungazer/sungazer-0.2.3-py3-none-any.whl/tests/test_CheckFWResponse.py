"""Tests for the CheckFWResponse model."""  # noqa: N999

import pytest
from pydantic import AnyUrl, ValidationError

from sungazer.models.firmware import CheckFWResponse


class TestCheckFWResponse:
    """Test cases for the CheckFWResponse model."""

    def test_check_fw_response_with_valid_url(self) -> None:
        """Test CheckFWResponse with a valid URL."""
        data = {"url": "https://example.com/firmware.bin"}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is not None
        assert isinstance(response.url, AnyUrl)
        assert str(response.url) == "https://example.com/firmware.bin"

    def test_check_fw_response_with_none_url(self) -> None:
        """Test CheckFWResponse with None URL."""
        data = {"url": None}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is None

    def test_check_fw_response_with_none_string(self) -> None:
        """Test CheckFWResponse with 'none' string (should convert to None)."""
        data = {"url": "none"}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is None

    def test_check_fw_response_with_none_string_case_insensitive(self) -> None:
        """Test CheckFWResponse with 'NONE' string (case insensitive)."""
        data = {"url": "NONE"}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is None

    def test_check_fw_response_with_http_url(self) -> None:
        """Test CheckFWResponse with HTTP URL."""
        data = {"url": "http://example.com/firmware.bin"}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is not None
        assert isinstance(response.url, AnyUrl)
        assert str(response.url) == "http://example.com/firmware.bin"

    def test_check_fw_response_with_ftp_url(self) -> None:
        """Test CheckFWResponse with FTP URL."""
        data = {"url": "ftp://example.com/firmware.bin"}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is not None
        assert isinstance(response.url, AnyUrl)
        assert str(response.url) == "ftp://example.com/firmware.bin"

    def test_check_fw_response_with_invalid_url(self) -> None:
        """Test CheckFWResponse with invalid URL raises ValidationError."""
        data = {"url": "not-a-valid-url"}

        with pytest.raises(ValidationError) as exc_info:
            CheckFWResponse(**data)  # type: ignore[arg-type]

        assert "url" in str(exc_info.value)

    def test_check_fw_response_with_empty_string(self) -> None:
        """Test CheckFWResponse with empty string URL raises ValidationError."""
        data = {"url": ""}

        with pytest.raises(ValidationError) as exc_info:
            CheckFWResponse(**data)  # type: ignore[arg-type]

        assert "url" in str(exc_info.value)

    def test_check_fw_response_with_invalid_type(self) -> None:
        """Test CheckFWResponse with invalid type raises ValidationError."""
        data = {"url": 123}

        with pytest.raises(ValidationError) as exc_info:
            CheckFWResponse(**data)  # type: ignore[arg-type]

        assert "url" in str(exc_info.value)

    def test_check_fw_response_with_already_parsed_anyurl(self) -> None:
        """Test CheckFWResponse with already parsed AnyUrl object."""
        url = AnyUrl("https://example.com/firmware.bin")
        data = {"url": url}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is not None
        assert isinstance(response.url, AnyUrl)
        assert response.url == url

    def test_check_fw_response_with_url_containing_query_params(self) -> None:
        """Test CheckFWResponse with URL containing query parameters."""
        data = {"url": "https://example.com/firmware.bin?version=1.2.3&type=stable"}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is not None
        assert isinstance(response.url, AnyUrl)
        assert (
            str(response.url)
            == "https://example.com/firmware.bin?version=1.2.3&type=stable"
        )

    def test_check_fw_response_with_url_containing_fragments(self) -> None:
        """Test CheckFWResponse with URL containing fragments."""
        data = {"url": "https://example.com/firmware.bin#section1"}
        response = CheckFWResponse(**data)  # type: ignore[arg-type]

        assert response.url is not None
        assert isinstance(response.url, AnyUrl)
        assert str(response.url) == "https://example.com/firmware.bin#section1"
