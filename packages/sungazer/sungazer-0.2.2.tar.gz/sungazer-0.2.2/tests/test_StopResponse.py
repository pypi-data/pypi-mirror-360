"""Tests for the StopResponse model."""  # noqa: N999

import pytest

from sungazer.models.session import StopResponse


class TestStopResponse:
    """Test cases for the StopResponse model."""

    def test_stop_response_with_success_result(self) -> None:
        """Test StopResponse with success result."""
        data = {"result": "success"}
        response = StopResponse(**data)  # type: ignore[arg-type]

        assert response.result == "success"

    def test_stop_response_with_different_result_values(self) -> None:
        """Test StopResponse with various result values."""
        test_cases = ["success", "failed", "error", "timeout", "cancelled"]

        for result in test_cases:
            data = {"result": result}
            response = StopResponse(**data)  # type: ignore[arg-type]

            assert response.result == result

    def test_stop_response_with_empty_string_result(self) -> None:
        """Test StopResponse with empty string result."""
        data = {"result": ""}
        response = StopResponse(**data)  # type: ignore[arg-type]

        assert response.result == ""

    def test_stop_response_with_long_result_string(self) -> None:
        """Test StopResponse with long result string."""
        long_result = "very_long_result_string_that_exceeds_normal_length " * 10
        data = {"result": long_result}
        response = StopResponse(**data)  # type: ignore[arg-type]

        assert response.result == long_result
