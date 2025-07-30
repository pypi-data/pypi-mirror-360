from pydantic import AnyUrl, BaseModel, Field, field_validator


class CheckFWResponse(BaseModel):
    """
    Response model for the ``Command=CheckFW`` API endpoint.

    This model provides information about available firmware updates for the
    system.  It includes a URL to download the firmware update if one is
    available, or indicates that no updates are available.
    """

    #: The result
    url: AnyUrl | None = Field(None, examples=["none"])

    @field_validator("url", mode="before")
    @classmethod
    def parse_url(cls, v: str | AnyUrl | None) -> str | AnyUrl | None:
        """
        Convert string URL to AnyUrl type, handling special "none" case.

        Handles various input formats:

        - Valid URL strings (converted to AnyUrl)
        - The string "none" (converted to None)
        - Already parsed AnyUrl objects
        - None values (returned as None)

        Args:
            v: The URL value to parse, can be a string, AnyUrl, or None.

        Returns:
            The parsed AnyUrl object, or None if the input was "none" or None.

        Raises:
            ValueError: If the string cannot be converted to a valid URL.

        """
        if v is None:
            return None

        if isinstance(v, AnyUrl):
            return v

        if isinstance(v, str):
            # Handle the special "none" case
            if v.lower() == "none":
                return None

            # Return the string for pydantic to handle AnyUrl conversion
            return v

        msg = f"Invalid value type for URL: {type(v)}"
        raise ValueError(msg)
