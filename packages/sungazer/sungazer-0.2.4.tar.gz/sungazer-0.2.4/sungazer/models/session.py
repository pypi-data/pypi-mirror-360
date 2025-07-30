from pydantic import BaseModel, Field


class Supervisor(BaseModel):
    """
    Details about the supervisor, the PVS6 device

    This model contains detailed version information about the device hardware,
    firmware, and software components. It serves as an initial response when
    establishing a session with the device.
    """

    #: Software version.
    SWVER: str | None = Field(None, examples=["2019.11, Build 5000"])
    #: The serial number of the device.
    SERIAL: str | None = Field(None, examples=["ZT184585000549A0069"])
    #: The hardware model.
    MODEL: str | None = Field(None, examples=["PVS6"])
    #: The firmware version.
    FWVER: str | None = Field(None, examples=["1.0.0"])
    #: The software version (how does this differ from SWVER?)
    SCVER: int | None = Field(None, examples=[16504])
    #: EASIC version number.
    EASICVER: int | None = Field(None, examples=[67072])
    #: Software build number (how does this differ from BUILD?)
    SCBUILD: int | None = Field(None, examples=[1185])
    #: Wireless network model identifier.
    WNMODEL: int | None = Field(None, examples=[400])
    #: Wireless network version number.
    WNVER: int | None = Field(None, examples=[3000])
    #: Wireless network serial number.
    WNSERIAL: int | None = Field(None, examples=[16])
    #: Build number of the software.
    BUILD: int | None = Field(None, examples=[5000])


class StartResponse(BaseModel):
    """
    Response model for the ``Command=Start`` API endpoint.

    This model contains detailed version information about the device hardware,
    firmware, and software components. It serves as an initial response when
    establishing a session with the device.
    """

    result: str = Field(..., examples=["success"])
    supervisor: Supervisor


class StopResponse(BaseModel):
    """
    Response model for the ``Command=Stop`` API endpoint.

    This model confirms the successful termination of a session with the device,
    providing a result status to indicate the outcome of the operation.
    """

    #: The result
    result: str = Field(..., examples=["success"])
