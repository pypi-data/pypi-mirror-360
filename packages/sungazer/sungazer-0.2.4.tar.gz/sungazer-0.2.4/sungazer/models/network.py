from ipaddress import IPv4Address

from pydantic import BaseModel, Field, field_validator


class Interface(BaseModel):
    """
    Network interface model representing a communication interface in the system.

    This model captures details about network interfaces such as WiFi, cellular,
    or Ethernet connections. It includes connectivity status, addressing information,
    and interface-specific details like signal strength and operational state.

    This is part of the ``Command=Get_Comm`` response in :py:class:`GetCommResponse`.
    """

    #: The WiFi SSID.
    ssid: str | None = Field(None, examples=["Laneakea"])
    #: The status of the interface.
    status: str | None = Field(None, examples=["not registered"])
    #: If the interface is paired
    pairing: str | None = Field(None, examples=["unpaired"])
    #: The speed of the interface.
    speed: int | None = Field(None, examples=[5])
    is_primary: bool | None = Field(
        None,
        description="this is the primary interface, only shows for cell interface",
        examples=[True],
    )
    is_always_on: bool | None = Field(
        False,  # noqa: FBT003
        description="this interface is always on, only shows for cell interface",
        examples=[True],
    )
    #: Provider name for cellular interfaces
    provider: str | None = Field(None, examples=["Verizon"])
    #: The SIM status for cellular interfaces
    sim: str | None = Field(None, examples=["SIM_READY"])
    #: Whether the interface is connected
    link: str | None = Field(None, examples=["connected"])
    #: The name of the interface.
    interface: str | None = Field(None, examples=["wan"])
    #: If the interface is up or down
    internet: str | None = Field(None, examples=["up"])
    #: The IP address of the interface.
    ipaddr: IPv4Address | None = Field(None, examples=["192.168.0.125"])
    #: The mode of the interface, e.g. wan, lan, etc.
    mode: str | None = Field(None, examples=["wan"])
    #: For cellular interfaces, whether the modem is ready
    modem: str | None = Field(None, examples=["MODEM_OK"])
    #: Whether SMS is reachable for cellular interfaces
    sms: str | None = Field(None, examples=["reachable"])
    #: THe state of the interface, e.g. up, down, etc.
    state: str | None = Field(None, examples=["up"])

    @field_validator("ipaddr", mode="before")
    @classmethod
    def parse_ipaddr(cls, v: str | IPv4Address | None) -> IPv4Address | None:
        """
        Convert string values to IPv4Address objects.

        Handles various input formats:

        - Valid IPv4 address strings (e.g., "192.168.1.1")
        - Empty strings (converted to None)
        - None values (returned as None)
        - Already parsed IPv4Address objects

        Args:
            v: The IP address value to parse, can be a string, IPv4Address, or None.

        Returns:
            The parsed IPv4Address object, or None if the input was empty/None.

        Raises:
            ValueError: If the string cannot be converted to a valid IPv4 address.

        """
        if v is None:
            return None

        if isinstance(v, IPv4Address):
            return v

        if isinstance(v, str):
            # Handle empty strings
            if not v.strip():
                return None

            try:
                return IPv4Address(v)
            except ValueError as e:
                msg = f"Invalid IPv4 address: {v}"
                raise ValueError(msg) from e

        msg = f"Invalid value type for IP address: {type(v)}"
        raise ValueError(msg)


class System(BaseModel):
    """
    System model representing overall system connectivity status.

    This model provides a high-level view of the system's network connectivity,
    including internet access status and SMS communication capabilities.

    This is part of the ``Command=Get_Comm`` response in :py:class:`GetCommResponse`.
    """

    interface: str | None = Field(
        None, description="the name of an interface", examples=["wan"]
    )
    internet: str | None = Field(None, description="internet status", examples=["up"])
    sms: str | None = Field(None, description="sms status", examples=["reachable"])


class NetworkStatus(BaseModel):
    #: The list of network interfaces.
    interfaces: list[Interface] | None = None
    #: The system information.
    system: System | None = None
    ts: str | None = Field(
        None, description="the system timestamp", examples=["1575501242"]
    )


class GetCommResponse(BaseModel):
    """
    Response model for the ``Command=Get_Comm`` API endpoint.

    This model encapsulates information about all network interfaces in the system,
    the overall system connectivity status, and a timestamp for when the information
    was collected.
    """

    result: str = Field(..., examples=["success"])
    networkstatus: NetworkStatus
