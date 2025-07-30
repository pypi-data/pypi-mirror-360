from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator


class Zipcode(BaseModel):
    """
    Model representing a range of ZIP codes for grid profile geographical
    applicability.

    This model defines the minimum and maximum ZIP code values within which a
    particular grid profile is valid. This is used to determine which grid
    profiles are appropriate for a system based on its installation location.
    """

    #: The maximum ZIP code value in the range (inclusive).
    max: float | None = Field(None, examples=[96898])
    #: The minimum ZIP code value in the range (inclusive).
    min: float | None = Field(None, examples=[96701])


class GridProfile(BaseModel):
    """
    Model representing a grid profile configuration option for the system.

    Grid profiles define how the solar system interacts with the utility grid,
    establishing parameters for compliance with local utility regulations and
    requirements. Each profile has a unique identifier, name, and may have
    geographical applicability constraints expressed through ZIP code ranges.

    The profile may also indicate special capabilities like self-supply
    operation, and whether it's the default profile for new installations.
    """

    #: Whether this profile is the default profile for new installations.
    default: bool | None = None
    #: The filename of the grid profile metadata file.
    filename: str | None = Field(None, examples=["8c9c4170.meta"])
    #: The unique identifier for the grid profile.
    id: str | None = Field(None, examples=["8c9c4170457c88f6dcee7216357681d580a3b9bd"])
    #: The human-readable name of the grid profile.
    name: str | None = Field(None, examples=["HECO OMH R14H (Legacy)"])
    #: Whether this profile supports self-supply operation.
    selfsupply: bool | None = None
    #: List of ZIP code ranges where this profile is applicable.
    zipcodes: list[Zipcode] | list[int] | None = None


class GridProfileRefreshResponse(BaseModel):
    """
    Response model for the ``Command=GridProfileRefresh`` API endpoint.

    This model contains the result of a grid profile refresh operation,
    including success status, creation timestamp, and the list of available
    grid profiles that can be applied to the system.
    """

    #: The result status of the grid profile refresh operation.
    result: str = Field(..., examples=["succeed"])
    #: Whether the grid profile refresh operation was successful.
    success: bool | None = Field(True, examples=[True])  # noqa: FBT003
    #: Unix timestamp when the grid profile list was created or last updated.
    creation: datetime | None = None
    #: List of available grid profiles that can be applied to the system.
    profiles: list[GridProfile] = Field(default_factory=list)

    @field_validator("creation", mode="before")
    @classmethod
    def parse_creation_timestamp(
        cls, v: str | int | datetime | None
    ) -> datetime | None:
        """
        Convert Unix epoch timestamp to datetime object.

        Handles various input formats:

        - Unix epoch timestamp as string (e.g., "1600704253")
        - Unix epoch timestamp as integer (e.g., 1600704253)
        - Already parsed datetime objects
        - None values (returned as None)

        Args:
            v: The timestamp value to parse, can be a string, integer, datetime,
            or None.

        Returns:
            The parsed datetime object, or None if the input was None.

        Raises:
            ValueError: If the string/integer cannot be converted to a valid timestamp.

        """
        if v is None:
            return None

        if isinstance(v, datetime):
            return v

        if isinstance(v, (str, int)):
            try:
                # Convert to integer if it's a string
                timestamp = int(v) if isinstance(v, str) else v
                return datetime.fromtimestamp(timestamp, tz=ZoneInfo("UTC"))
            except (ValueError, OSError) as e:
                msg = f"Invalid Unix timestamp: {v}"
                raise ValueError(msg) from e

        msg = f"Invalid value type for timestamp: {type(v)}"
        raise ValueError(msg)


class GridProfileGetResponse(BaseModel):
    """
    Response model for the ``Command=GridProfileGet`` API endpoint.

    This model provides information about the currently active and pending grid
    profiles on the system, including their names, IDs, completion percentage,
    and support status.
    """

    #: The result status of the grid profile get operation.
    result: str = Field(..., examples=["succeed"])
    #: The name of the currently active grid profile.
    active_name: str | None = Field(None, examples=["IEEE-1547a-2014 + 2020 CA Rule21"])
    #: The unique identifier of the currently active grid profile.
    active_id: str | None = Field(
        None, examples=["816bf3302d337a42680b996227ddbc46abf9cd05"]
    )
    #: The name of the pending grid profile (if any).
    pending_name: str | None = Field(
        None, examples=["IEEE-1547a-2014 + 2020 CA Rule21"]
    )
    #: The unique identifier of the pending grid profile (if any).
    pending_id: str | None = Field(
        None, examples=["816bf3302d337a42680b996227ddbc46abf9cd05"]
    )
    #: Not sure what this is, but it's always 100% for me
    percent: int | None = Field(None, examples=[100])
    #: Indicates which components support the grid profile.
    supported_by: str | None = Field(None, examples=["ALL"])
    #: The overall status of the grid profile operation.
    status: str | None = Field(None, examples=["success"])
