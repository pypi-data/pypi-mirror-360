from datetime import datetime, timedelta
from typing import Literal, Union
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator

DeviceType = Literal[
    "PVS",
    "Power Meter",
    "Inverter",
    "PV Disconnect",
    "Gateway",
    "Storage Inverter",
    "ESS BMS",
    "Battery",
    "Energy Storage System",
]


class BaseDeviceDetail(BaseModel):
    """
    Base model containing common fields for all device types in the system.

    This model serves as the foundation for all device detail models, providing
    standard fields like identification information (serial, model), version data,
    operational status, and temporal information. All specific device types
    extend this model with additional specialized fields.
    """

    ISDETAIL: bool = Field(
        True,  # noqa: FBT003
        description="Details about the device",
        examples=[True],
    )
    STATE: str | None = Field(
        None, description="State of the device", examples=["working"]
    )
    STATEDESCR: str | None = Field(
        None, description="Description of the state", examples=["Working"]
    )
    SERIAL: str | None = Field(
        None,
        description="The serial number of the device",
        examples=["ZT112345678912A0069"],
    )
    MODEL: str | None = Field(
        None,
        description="The manufacturer's model of the device",
        examples=["PVS6M0400p"],
    )
    HWVER: str | None = Field(
        None, description="The hardware version", examples=["6.02"]
    )
    SWVER: str | None = Field(
        None,
        description="The software version  of the firmware",
        examples=["2021.9, Build 41001"],
    )
    #: The device type
    DEVICE_TYPE: DeviceType | None = None
    TYPE: str | None = Field(
        None,
        description=(
            "The detailed type of the device (usually includes the manufacturer)"
        ),
        examples=["PVS5-METER-P"],
    )
    PORT: str | None = Field(
        None, description="The port the device is connected to", examples=["COM1"]
    )
    DATATIME: datetime | None = Field(
        None, description="The time the data was recorded"
    )
    CURTIME: datetime | None = Field(
        None, description="The current time as reported by the device"
    )
    OPERATION: str | None = Field(None, description="Operation type", examples=["noop"])
    origin: str | None = Field(
        None, description="Origin of this data", examples=["data_logger"]
    )
    panid: float | None = Field(
        None,
        description=(
            "PAN ID is used to determine whether an MI is A) Un-associated (panid = 0),"
            "B) owned by 'me' (mi.panid == pvs.panid) or C) owned by someone else "
            "(mi.panid != 0 && mi.panid != pvs.panid)"
        ),
    )

    @field_validator("DATATIME", "CURTIME", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime | None) -> datetime | None:
        """
        Convert timestamp strings to datetime objects.

        Handles various timestamp formats found in the API responses:

        - PVS6 comma-separated format: "2025,06,22,00,15,54"
        - Already parsed datetime objects

        Args:
            v: The timestamp value to parse, can be a string or datetime object.

        Raises:
            ValueError: If the timestamp format is invalid or cannot be parsed.

        """
        if v is None:
            return None

        if isinstance(v, datetime):
            return v

        if isinstance(v, str):
            # Handle PVS6 comma-separated format
            if "," in v and len(v.split(",")) == 6:
                try:
                    year, month, day, hour, minute, second = v.split(",")
                    return datetime(
                        int(year),
                        int(month),
                        int(day),
                        int(hour),
                        int(minute),
                        int(second),
                        tzinfo=ZoneInfo("UTC"),
                    )
                except (ValueError, TypeError):
                    pass

        msg = f"Invalid datetime value: {v}"
        raise ValueError(msg)


class PVSDeviceDetail(BaseDeviceDetail):
    """
    Model representing the PVS (Photovoltaic Supervisor) device itself.

    This model extends the base device details with PVS-specific metrics
    including diagnostic information about communication errors, system resource
    utilization (CPU, memory, flash storage), and operational metrics like scan
    performance and uptime.

    This device type appears in the device list when using
    ``Command=DeviceList`` and represents the central monitoring and control
    system for the solar installation.
    """

    dl_error_count: int | None = Field(
        None, description="Number of comms errors detected since last report"
    )
    dl_comm_err: int | None = Field(None, description="Number of comms errors")
    dl_skipped_scans: int | None = Field(
        None,
        description=(
            "This counts when the supervisor scans the PLC network for inverters and "
            "it decides it needs to skip a scan"
        ),
        examples=[0],
    )
    dl_cpu_load: float | None = Field(
        None, description="The CPU load of the device", examples=[12.5]
    )
    dl_flash_avail: int | None = Field(
        None, description="How much free flash memory is available", examples=[12234]
    )
    dl_mem_used: int | None = Field(
        None, description="How much memory is used, probably in kB", examples=[23456]
    )
    dl_scan_time: int | None = Field(
        None,
        description=(
            "How long the last scan of the PLC network took, maybe in milliseconds"
        ),
        examples=[1234],
    )
    dl_untransmitted: int | None = Field(
        None, description="Numbeer of not yet transmitted events/records?", examples=[0]
    )
    #: The uptime of the data logger in seconds (PVS only).  It has been
    #: observed to be lower after 24hrs, so either there can be restarts for power
    #: reasons or perhaps the device itself restarts itself periodically (to clear
    #: memory leaks?)
    dl_uptime: int | None = Field(None, examples=[123456])

    @property
    def last_restart_time(self) -> datetime | None:
        """
        Calculate when the data logger last restarted in UTC.

        Uses the current time (CURTIME) and subtracts the uptime (dl_uptime)
        to determine when the system was last restarted.

        Returns:
            datetime: The UTC timestamp when the data logger last restarted,
                     or None if insufficient data is available.

        """
        if self.CURTIME is None or self.dl_uptime is None:
            return None

        # Calculate restart time by subtracting uptime from current time
        restart_time = self.CURTIME - timedelta(seconds=self.dl_uptime)

        # Ensure the result is in UTC
        if restart_time.tzinfo is None:
            restart_time = restart_time.replace(tzinfo=ZoneInfo("UTC"))

        return restart_time


class PowerMeterDeviceDetail(BaseDeviceDetail):
    """
    Common base model for all power metering devices in the system.

    This model contains fields relevant to any power meter, whether measuring
    production or consumption. It includes power metrics (real, reactive, and
    apparent power), energy measurements, power factor calculations, and
    operational parameters like frequency and current sensor calibration.

    Power meters track electrical energy flow at key points in the solar system
    and building electrical infrastructure.
    """

    interface: str | None = Field(
        None, description="The type of interface used by the device", examples=["mime"]
    )
    subtype: str | None = Field(
        None, description="The subtype of meter", examples=["GROSS_PRODUCTION_SITE"]
    )
    ct_scl_fctr: int | None = Field(
        None,
        description=(
            "Current capacity of the calibration-reference CT sensor in Amps."
        ),
        examples=[50],
    )
    net_ltea_3phsum_kwh: float | None = Field(
        None, description="Net cumulative kWh, across all 3 phases", examples=[198.92]
    )
    p_3phsum_kw: float | None = Field(
        None, description="Average real power (kW)", examples=[1.9867]
    )
    q_3phsum_kvar: float | None = Field(
        None,
        description="Average reactive power (kVA) across all 3 phases",
        examples=[0.1234],
    )
    s_3phsum_kva: float | None = Field(
        None,
        description="Average apparent power (kVA) across all 3 phases",
        examples=[2.0],
    )
    tot_pf_rto: float | None = Field(
        None,
        description=(
            "Total power factor ratio, defined as real power (kW) "
            "divided by apparent (kVA)"
        ),
        examples=[0.993],
    )
    freq_hz: float | None = Field(
        None, description="Operating Frequency in Hz", examples=[60.0]
    )
    CAL0: int | None = Field(
        None,
        description=(
            "The sensor's current capacity for the calibration-reference CT sensor."
            "It will be 50 (50A) for the production meter and 100 or 200 for the "
            "consumption meter."
        ),
        examples=[50],
    )
    #: Supply voltage sum accross C1 and C2 leads (typically in the 220-140V range)
    v12_v: float | None = Field(
        None,
        description=(
            "Supply Voltage sum accross C1 and C2 leads (typically "
            "in the 220-140V range)"
        ),
        examples=[208.0],
    )


class ProductionPowerMeterDeviceDetail(PowerMeterDeviceDetail):
    """
    Model representing a production power meter that measures solar energy
    generation.

    This model extends the base power meter details with production-specific
    metrics.  Production meters monitor the electricity generated by the solar
    array, reporting zero output at night and varying levels during daylight
    hours based on sunlight conditions and system capacity.

    This device type appears in the device list when using
    ``Command=DeviceList`` if a production power meter is connected to the PVS6.
    """

    #: The production meter subtype enum
    production_subtype_enum: str | None = Field(
        None,
        description="The production subtype enum",
        examples=["GROSS_PRODUCTION_SITE"],
    )
    i_a: float | None = Field(None, description="Current in Amps", examples=[2.1122])


class ConsumptionPowerMeterDeviceDetail(PowerMeterDeviceDetail):
    """
    Model representing a consumption power meter that measures site power usage.

    This model extends the production power meter details with
    consumption-specific metrics including multi-lead current and voltage
    readings, detailed phase measurements, and bidirectional energy flow
    accounting (import from and export to the utility grid).

    Consumption meters monitor electricity used by the building, typically
    showing non-zero values even at night, and when solar production is
    insufficient to meet current demand.

    This device type appears in the device list when using
    ``Command=DeviceList`` if a consumption power meter is connected to the
    PVS6.
    """

    consumption_subtype_enum: str | None = Field(
        None,
        description="The consumption subtype enum",
        examples=["NET_CONSUMPTION_LOADSIDE"],
    )
    i1_a: float | None = Field(
        None,
        description=(
            "The sensor's current capacity for the calibration-reference CT sensor."
            "It will be 50 (50A) for the production meter and 100 or 200 for the "
            "consumption meter."
        ),
        examples=[1.2],
    )
    i2_a: float | None = Field(
        None, description="Current in Amps on CT2 lead", examples=[1.2]
    )
    v1n_v: float | None = Field(
        None, description="Voltage in Volts on lead 1 to neutral", examples=[120.0]
    )
    v2n_v: float | None = Field(
        None, description="Voltage in Volts on lead 2 to neutral", examples=[120.0]
    )
    p1_kw: float | None = Field(
        None, description="Lead 1 average power in kW", examples=[0.123]
    )
    p2_kw: float | None = Field(
        None, description="Lead 2 average power in kW", examples=[0.123]
    )
    neg_ltea_3phsum_kwh: float | None = Field(
        None, examples=[123.45], description="Cumulative kWh imported from utility"
    )
    pos_ltea_3phsum_kwh: float | None = Field(
        None, examples=[234.56], description="Cumulative kWh exported to utility"
    )


class SolarBridgeDeviceDetail(BaseDeviceDetail):
    """
    Model representing a SolarBridge microinverter device in the solar array.

    This model extends the base device details with microinverter-specific
    metrics including AC output parameters (power, voltage, current), DC input
    measurements from the connected solar panel, thermal monitoring, and energy
    production data.

    Microinverters convert DC power from individual solar panels to AC power for
    use in the building or export to the grid. Each microinverter typically
    connects to a single solar panel.

    This device type appears in the device list when using
    ``Command=DeviceList`` if SolarBridge microinverters are connected to the
    PVS6.
    """

    interface: str | None = Field(
        None, description="The type of interface used by the panel?", examples=["mime"]
    )
    hw_version: str | None = Field(
        None, description="Hardware version", examples=["1.0"]
    )
    module_serial: str | None = Field(
        None,
        description="Serial number of the inverter module",
        examples=["12345678901234"],
    )
    PANEL: str | None = Field(
        None,
        description="Model of the solar panel module",
        examples=["SPR-A410-G-AC"],
    )
    slave: bool | None = Field(
        None, description="Is this a slave device?", examples=[False]
    )
    MOD_SN: str | None = Field(
        None,
        description="Serial number of the microinverter",
        examples=["12345678901234"],
    )
    NMPLT_SKU: str | None = Field(
        None,
        description="SKU of the microinverter",
        examples=["SB250-1BD-US"],
    )
    ltea_3phsum_kwh: float | None = Field(
        None, description="Total Energy in kWh", examples=[123.45]
    )
    p_3phsum_kw: float | None = Field(
        None, description="AC Power (kW)", examples=[0.0471]
    )
    vln_3phsum_v: float | None = Field(
        None, description="AC Voltage (V)", examples=[246.5]
    )
    i_3phsum_a: float | None = Field(
        None, description="AC Current (A)", examples=[0.19]
    )
    p_mppt1_v: float | None = Field(
        None,
        description="DC Power (kW) for MPTT (Maximum Power Point Tracking)",
        examples=[0.0502],
    )
    v_mppt1_v: float | None = Field(
        None,
        description="DC Voltage (V) for MPTT (Maximum Power Point Tracking)",
        examples=[54.5],
    )
    i_mppt1_a: float | None = Field(
        None,
        description="DC Current (A) for MPTT (Maximum Power Point Tracking)",
        examples=[0.92],
    )
    p_mpptsum_kw: float | None = Field(
        None,
        description="Legacy? Seems replaced by p_mppt1_kw",
    )
    t_htsink_degc: float | None = Field(
        None, description="Heatsink temperature in degrees C", examples=[45.0]
    )
    freq_hz: float | None = Field(
        None, description="Operating Frequency in Hz", examples=[60.0]
    )
    stat_ind: int | None = Field(None, description="Status indicator?", examples=[0])


class PVDisconnectDetail(BaseDeviceDetail):
    """
    Model representing a PV disconnect device in the solar system.

    This model extends the base device details with PV disconnect-specific metrics
    including switch status, control capabilities, and operational parameters.
    PV disconnect devices provide safety isolation between the solar array and
    the rest of the electrical system, allowing for safe maintenance and emergency
    shutdown procedures.

    This device type appears in the device list when using ``Command=DeviceList``
    if a PV disconnect device is connected to the PVS6 system.
    """

    event_history: int | None = Field(
        None, description="Count of 'events' seen so far", examples=[32]
    )
    hw_version: str | None = Field(
        None, description="The hardware version", examples=["0.2.0"]
    )
    interface: str | None = Field(
        None,
        description="The type of interface used by the panel",
        examples=["ttymxc5"],
    )
    slave: int | None = Field(None, description="Slave number", examples=[230])
    fw_error: int | None = Field(
        None,
        description="Error count for firmware operations",
        examples=[0, 1, 2],
    )
    relay_mode: int | None = Field(
        None,
        description="Indicates the relay mode of the disconnect",
        examples=[0, 1],
    )
    relay1_state: Literal[0, 1] | None = Field(
        None,
        description="State of Relay 1, indicating operational status",
        examples=[0, 1],
    )
    relay2_state: Literal[0, 1] | None = Field(
        None,
        description="State of Relay 2, indicating operational status",
        examples=[0, 1],
    )
    relay1_error: int | None = Field(
        None,
        description="Error count for Relay 1",
        examples=[0, 1, 2],
    )
    relay2_error: int | None = Field(
        None,
        description="Error count for Relay 2",
        examples=[0, 1, 2],
    )
    v1n_grid_v: float | None = Field(
        None,
        description=(
            "Voltage differential between line and neutral at the "
            "disconnect in volts for phase 1"
        ),
        examples=[120.0],
    )
    v2n_grid_v: float | None = Field(
        None,
        description=(
            "Voltage differential between line and neutral at the "
            "disconnect in volts for phase 2"
        ),
        examples=[120.0],
    )
    v1n_pv_v: float | None = Field(
        None,
        description=(
            "Voltage differential between phase 1 neutral and the PV system in volts"
        ),
        examples=[120.0],
    )
    v2n_pv_v: float | None = Field(
        None,
        description=(
            "Voltage differential between phase 2 neutral and the PV system in volts"
        ),
        examples=[120.0],
    )

    @field_validator(
        "event_history",
        "fw_error",
        "relay_mode",
        "relay1_state",
        "relay2_state",
        "relay1_error",
        "relay2_error",
        mode="before",
    )
    @classmethod
    def parse_integer_fields(cls, v: str | int | None) -> int | None:
        """
        Convert string values to integers for fields that come from the API as strings.

        Args:
            v: The value to parse, can be a string, integer, or None.

        Returns:
            The parsed integer value, or None if the input was None.

        Raises:
            ValueError: If the value cannot be converted to an integer.

        """
        if v is None:
            return None

        if isinstance(v, int):
            return v

        if isinstance(v, str):
            try:
                return int(v)
            except ValueError as e:
                msg = f"Invalid integer value: {v}"
                raise ValueError(msg) from e

        msg = f"Invalid value type for integer field: {type(v)}"
        raise ValueError(msg)


class Gateway(BaseDeviceDetail):
    """
    Model representing a gateway device in the solar system.

    This model extends the base device details with gateway-specific metrics
    including network interface information, communication protocols, and
    operational status. Gateway devices provide communication interfaces
    between the solar system and external networks or monitoring systems.

    This device type appears in the device list when using ``Command=DeviceList``
    if a gateway device is connected to the PVS6 system.
    """

    interface: str | None = Field(
        None,
        description="The type of interface used by the gateway",
        examples=["sunspec"],
    )
    mac_address: str | None = Field(
        None,
        description="The MAC address of the gateway device",
        examples=["d8:a9:ab:cd:12:34"],
    )
    slave: int | None = Field(None, description="The slave number", examples=[1])


class SchneiderXwPro(BaseDeviceDetail):
    """
    Model representing a Schneider XW Pro storage inverter in the solar system.

    This model extends the base device details with Schneider XW Pro-specific
    metrics including storage inverter capabilities, battery management, and
    operational parameters. Schneider XW Pro devices provide energy storage
    functionality, allowing for battery backup and energy management in solar
    installations.

    This device type appears in the device list when using ``Command=DeviceList``
    if a Schneider XW Pro storage inverter is connected to the PVS6 system.
    """

    interface: str | None = Field(
        None,
        description="The type of interface used by the storage inverter",
        examples=["sunspec"],
    )
    mac_address: str | None = Field(
        None,
        description="The MAC address of the storage inverter device",
        examples=["d8:a9:ab:cd:12:34"],
    )
    parent: int | None = Field(
        None, description="The parent device identifier", examples=[11]
    )
    slave: int | None = Field(
        None,
        description="The slave number for the storage inverter device",
        examples=[10],
    )
    PARENT: str | None = Field(
        None,
        description="The parent device serial number",
        examples=["00001ABC1234_01234567890ABCDEF"],
    )


class EquinioxBMS(BaseDeviceDetail):
    """
    Model representing an Equiniox Battery Management System (BMS) in the solar system.

    This model extends the base device details with Equiniox BMS-specific
    metrics including battery management capabilities, monitoring parameters,
    and operational status. Equiniox BMS devices provide battery management
    functionality for energy storage systems, monitoring battery health,
    state of charge, and safety parameters.

    This device type appears in the device list when using ``Command=DeviceList``
    if an Equiniox BMS is connected to the PVS6 system.
    """

    interface: str | None = Field(
        None,
        description="The type of interface used by the BMS",
        examples=["sunspec"],
    )
    mac_address: str | None = Field(
        None,
        description="The MAC address of the BMS device",
        examples=["d8:a9:ab:cd:12:34"],
    )
    parent: int | None = Field(
        None, description="The parent device identifier", examples=[11]
    )
    slave: int | None = Field(
        None, description="The slave number of the BMS device", examples=[230]
    )
    PARENT: str | None = Field(
        None,
        description="The parent device serial number",
        examples=["00001ABC1234_01234567890ABCDEF"],
    )


class Battery(BaseDeviceDetail):
    """
    Model representing a Battery device in the solar system.

    This model extends the base device details with Battery-specific
    metrics including battery management capabilities, monitoring parameters,
    and operational status. Battery devices provide energy storage
    functionality for solar installations, storing excess energy for later use.

    This device type appears in the device list when using ``Command=DeviceList``
    if a Battery is connected to the PVS6 system.
    """

    interface: str | None = Field(
        None,
        description="The type of interface used by the battery",
        examples=["none"],
    )
    parent: int | None = Field(
        None, description="The parent device identifier", examples=[11]
    )
    PARENT: str | None = Field(
        None,
        description="The parent device serial number",
        examples=["00001ABC1234_01234567890ABCDEF"],
    )
    hw_version: str | None = Field(
        None,
        description="The hardware version of the battery",
        examples=["4.34"],
    )
    DESCR: str | None = Field(
        None,
        description="Description of the battery",
        examples=["Battery M00122109A0355"],
    )


class EquinoxESS(BaseDeviceDetail):
    """
    Model representing an Equinox Energy Storage System (ESS) device in the
    solar system.

    This model extends the base device details with ESS-specific metrics including
    operational status, hardware and software versions, and descriptive information.
    Equinox ESS devices provide energy storage functionality for solar installations.

    This device type appears in the device list when using ``Command=DeviceList``
    if an Equinox ESS is connected to the PVS6 system.
    """

    interface: str | None = Field(
        None,
        description="The type of interface used by the ESS",
        examples=["none"],
    )
    hw_version: str | None = Field(
        None,
        description="The hardware version of the ESS",
        examples=["0"],
    )
    DESCR: str | None = Field(
        None,
        description="Description of the ESS",
        examples=["Energy Storage System 00001ABC1234_01234567890ABCDEF"],
    )


#: A helper type for all possible device details
DeviceClass = Union[  # noqa: UP007
    PVSDeviceDetail,
    ProductionPowerMeterDeviceDetail,
    ConsumptionPowerMeterDeviceDetail,
    SolarBridgeDeviceDetail,
    PVDisconnectDetail,
    Gateway,
    SchneiderXwPro,
    EquinioxBMS,
    Battery,
    EquinoxESS,
]


class DeviceDetailResponse(BaseModel):
    """
    Response model for the ``Command=DeviceList`` API endpoint.

    This model provides a comprehensive inventory of all devices in the solar
    system, including the PVS controller, power meters (both production and
    consumption), and individual microinverters. It handles the heterogeneous
    nature of the device list by implementing custom parsing logic in the new()
    class method.

    The response includes convenience properties to easily access specific
    device types (pvs, inverters, production_meter, consumption_meter) without
    having to filter the devices list manually.
    """

    #: The devices
    devices: list[DeviceClass] | None = None
    #: The result
    result: str = Field(..., examples=["success"])

    @classmethod
    def new(cls, obj: dict) -> "DeviceDetailResponse":  # noqa: PLR0912
        """
        Custom parsing to handle different device types from the
        payload returned by the PVS6 API for Command=DeviceList.
        """
        devices: list[DeviceClass] = []
        if "devices" in obj:
            for device in obj["devices"]:
                device_type = device.get("DEVICE_TYPE")
                if device_type == "PVS":
                    devices.append(PVSDeviceDetail(**device))
                elif device_type == "Power Meter":
                    if "production_subtype_enum" in device:
                        devices.append(ProductionPowerMeterDeviceDetail(**device))
                    elif "consumption_subtype_enum" in device:
                        devices.append(ConsumptionPowerMeterDeviceDetail(**device))
                elif device_type == "Inverter":
                    devices.append(SolarBridgeDeviceDetail(**device))
                elif device_type == "PV Disconnect":
                    devices.append(PVDisconnectDetail(**device))
                elif device_type == "Gateway":
                    devices.append(Gateway(**device))
                elif device_type == "Storage Inverter":
                    devices.append(SchneiderXwPro(**device))
                elif device_type == "ESS BMS":
                    devices.append(EquinioxBMS(**device))
                elif device_type == "Battery":
                    devices.append(Battery(**device))
                elif device_type == "Energy Storage System":
                    devices.append(EquinoxESS(**device))
                else:
                    msg = f"Unknown device type: {device_type}"
                    raise ValueError(msg)
        return DeviceDetailResponse(
            devices=devices, result=obj.get("result", "unknown")
        )

    @property
    def pvs(self) -> PVSDeviceDetail | None:
        """Return The PVS device, or None if not found."""
        if self.devices is None:
            return None
        pvs_devices = [
            device for device in self.devices if isinstance(device, PVSDeviceDetail)
        ]
        if not pvs_devices:
            return None
        if len(pvs_devices) > 1:
            msg = "Multiple PVS devices found"
            raise ValueError(msg)
        return pvs_devices[0]

    @property
    def inverters(self) -> list[SolarBridgeDeviceDetail]:
        """Return a list of inverters (SolarBridge devices)"""
        if self.devices is None:
            return []
        return [
            device
            for device in self.devices
            if isinstance(device, SolarBridgeDeviceDetail)
        ]

    @property
    def production_meter(self) -> ProductionPowerMeterDeviceDetail | None:
        """Return a list of production power meters, or None if not found."""
        if self.devices is None:
            return None
        meters = [
            device
            for device in self.devices
            if isinstance(device, ProductionPowerMeterDeviceDetail)
        ]
        if not meters:
            return None
        if len(meters) > 1:
            msg = "Multiple production power meters found"
            raise ValueError(msg)
        return meters[0]

    @property
    def consumption_meter(self) -> ConsumptionPowerMeterDeviceDetail | None:
        """Return a list of consumption power meters, or None if not found."""
        if self.devices is None:
            return None
        meters = [
            device
            for device in self.devices
            if isinstance(device, ConsumptionPowerMeterDeviceDetail)
        ]
        if not meters:
            return None
        if len(meters) > 1:
            msg = "Multiple consumption power meters found"
            raise ValueError(msg)
        return meters[0]
