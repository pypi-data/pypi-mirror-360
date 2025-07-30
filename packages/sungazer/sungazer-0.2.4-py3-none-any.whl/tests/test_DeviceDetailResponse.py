# type: ignore  # noqa: N999, PGH003
import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from sungazer.models import (
    Battery,
    ConsumptionPowerMeterDeviceDetail,
    DeviceDetailResponse,
    EquinioxBMS,
    EquinoxESS,
    Gateway,
    ProductionPowerMeterDeviceDetail,
    PVDisconnectDetail,
    PVSDeviceDetail,
    SchneiderXwPro,
    SolarBridgeDeviceDetail,
)


def test_device_detail_response_new():  # noqa: PLR0912
    """Test DeviceDetailResponse.new() method with sample data from DeviceList.json."""
    # Load test data
    data_path = (
        Path(__file__).parent.parent
        / "tests"
        / "fixtures"
        / "DeviceList"
        / "DeviceList.json"
    )
    with Path(data_path).open() as f:
        test_data = json.load(f)

    # Parse the data using the new() method
    response = DeviceDetailResponse.new(test_data)

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == test_data.get("result", "unknown")

    # Check that we have devices
    assert response.devices is not None
    assert response.devices != []
    assert len(response.devices) == len(test_data.get("devices", []))

    # Verify device types were correctly parsed
    for i, device in enumerate(response.devices):
        device_type = test_data["devices"][i].get("DEVICE_TYPE")
        if device_type == "PVS":
            assert isinstance(device, PVSDeviceDetail)
        elif device_type == "Power Meter":
            if "production_subtype_enum" in test_data["devices"][i]:
                assert isinstance(device, ProductionPowerMeterDeviceDetail)
            elif "consumption_subtype_enum" in test_data["devices"][i]:
                assert isinstance(device, ConsumptionPowerMeterDeviceDetail)
        elif device_type == "Inverter":
            assert isinstance(device, SolarBridgeDeviceDetail)
        elif device_type == "PV Disconnect":
            assert isinstance(device, PVDisconnectDetail)
        elif device_type == "Gateway":
            assert isinstance(device, Gateway)
        elif device_type == "Storage Inverter":
            assert isinstance(device, SchneiderXwPro)
        elif device_type == "ESS BMS":
            assert isinstance(device, EquinioxBMS)
        elif device_type == "Battery":
            assert isinstance(device, Battery)
        elif device_type == "Energy Storage System":
            assert isinstance(device, EquinoxESS)

    # Test device accessor properties
    assert (
        isinstance(response.pvs, PVSDeviceDetail)
        if any(isinstance(d, PVSDeviceDetail) for d in response.devices)
        else response.pvs is None
    )

    # Check production meter (singular property)
    production_meters = [
        d for d in response.devices if isinstance(d, ProductionPowerMeterDeviceDetail)
    ]
    if production_meters:
        assert isinstance(response.production_meter, ProductionPowerMeterDeviceDetail)
    else:
        assert response.production_meter is None

    # Check consumption meter (singular property)
    consumption_meters = [
        d for d in response.devices if isinstance(d, ConsumptionPowerMeterDeviceDetail)
    ]
    if consumption_meters:
        assert isinstance(response.consumption_meter, ConsumptionPowerMeterDeviceDetail)
    else:
        assert response.consumption_meter is None

    # Check inverters (plural property)
    assert len(response.inverters) == len(
        [d for d in response.devices if isinstance(d, SolarBridgeDeviceDetail)]
    )
    for inverter in response.inverters:
        assert isinstance(inverter, SolarBridgeDeviceDetail)

    # Test that CURTIME fields are parsed correctly into datetime objects
    for i, device in enumerate(response.devices):
        if "CURTIME" in test_data["devices"][i]:
            curtime_str = test_data["devices"][i]["CURTIME"]
            # Parse the comma-separated timestamp format
            year, month, day, hour, minute, second = curtime_str.split(",")
            expected_curtime = datetime(
                int(year),
                int(month),
                int(day),
                int(hour),
                int(minute),
                int(second),
                tzinfo=ZoneInfo("UTC"),
            )
            assert device.CURTIME == expected_curtime


def test_device_detail_response_new_unknown_device_type():
    """Test DeviceDetailResponse.new() method with an unknown device type."""
    # Create test data with an unknown device type
    test_data = {
        "devices": [
            {
                "DEVICE_TYPE": "UNKNOWN_TYPE",
                "SERIAL": "123456",
            }
        ],
        "result": "success",
    }

    # The method should raise a ValueError for unknown device types
    with pytest.raises(ValueError, match="Unknown device type: UNKNOWN_TYPE"):
        DeviceDetailResponse.new(test_data)


def test_device_detail_response_new_no_devices():
    """Test DeviceDetailResponse.new() method with no devices."""
    # Create test data with no devices
    test_data = {
        "result": "success",
    }

    # Parse the data using the new() method
    response = DeviceDetailResponse.new(test_data)

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"

    # Check that devices is None
    assert response.devices == []


def test_device_detail_response_properties_empty():
    """Test DeviceDetailResponse properties when devices is None."""
    response = DeviceDetailResponse(result="success")

    assert response.pvs is None
    assert response.inverters == []
    assert response.production_meter is None
    assert response.consumption_meter is None


def test_device_detail_response_pvs_multiple():
    """Test DeviceDetailResponse.pvs raises error with multiple PVS devices."""
    # Create a response with multiple PVS devices
    pvs1 = PVSDeviceDetail(DEVICE_TYPE="PVS", SERIAL="123")
    pvs2 = PVSDeviceDetail(DEVICE_TYPE="PVS", SERIAL="456")

    response = DeviceDetailResponse(devices=[pvs1, pvs2], result="success")

    # Accessing pvs property should raise ValueError
    with pytest.raises(ValueError, match="Multiple PVS devices found"):
        _ = response.pvs


def test_device_detail_response_production_meter_multiple():
    """
    Test DeviceDetailResponse.production_meter raises error with multiple
    production meters.
    """
    # Create a response with multiple production meters
    meter1 = ProductionPowerMeterDeviceDetail(
        DEVICE_TYPE="Power Meter",
        SERIAL="123",
        production_subtype_enum="GROSS_PRODUCTION_SITE",
    )
    meter2 = ProductionPowerMeterDeviceDetail(
        DEVICE_TYPE="Power Meter",
        SERIAL="456",
        production_subtype_enum="GROSS_PRODUCTION_SITE",
    )

    response = DeviceDetailResponse(devices=[meter1, meter2], result="success")

    # Accessing production_meter property should raise ValueError
    with pytest.raises(ValueError, match="Multiple production power meters found"):
        _ = response.production_meter


def test_device_detail_response_consumption_meter_multiple():
    """
    Test DeviceDetailResponse.consumption_meter raises error with multiple
    consumption meters.
    """
    # Create a response with multiple consumption meters
    meter1 = ConsumptionPowerMeterDeviceDetail(
        DEVICE_TYPE="Power Meter",
        SERIAL="123",
        consumption_subtype_enum="NET_CONSUMPTION_LOADSIDE",
    )
    meter2 = ConsumptionPowerMeterDeviceDetail(
        DEVICE_TYPE="Power Meter",
        SERIAL="456",
        consumption_subtype_enum="NET_CONSUMPTION_LOADSIDE",
    )

    response = DeviceDetailResponse(devices=[meter1, meter2], result="success")

    # Accessing consumption_meter property should raise ValueError
    with pytest.raises(ValueError, match="Multiple consumption power meters found"):
        _ = response.consumption_meter


def test_pv_disconnect_device_parsing():
    """Test parsing of PV-DISCONNECT device type."""
    # Create test data for a PV-DISCONNECT device
    test_data = {
        "devices": [
            {
                "ISDETAIL": True,
                "SERIAL": "SY01234567890ABCDEF",
                "TYPE": "PV-DISCONNECT",
                "STATE": "working",
                "STATEDESCR": "Working",
                "MODEL": "SunPower PV Disconnect Relay",
                "DESCR": "PV Disconnect SY01234567890ABCDEF",
                "DEVICE_TYPE": "PV Disconnect",
                "hw_version": "0.2.0",
                "interface": "ttymxc5",
                "slave": 230,
                "SWVER": "0.2.13",
                "PORT": "P0, Modbus, Slave 230",
                "DATATIME": "2022,05,26,14,50,30",
                "event_history": "32",
                "fw_error": "0",
                "relay_mode": "0",
                "relay1_state": "1",
                "relay2_state": "1",
                "relay1_error": "0",
                "relay2_error": "0",
                "v1n_grid_v": "123.1",
                "v2n_grid_v": "122.5",
                "v1n_pv_v": "122.8",
                "v2n_pv_v": "122.5",
                "origin": "data_logger",
                "OPERATION": "noop",
                "CURTIME": "2022,05,26,14,50,32",
            }
        ],
        "result": "success",
    }

    # Parse the data using the new() method
    response = DeviceDetailResponse.new(test_data)

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"
    assert len(response.devices) == 1

    # Check that the device was correctly parsed as PVDisconnectDetail
    device = response.devices[0]
    assert isinstance(device, PVDisconnectDetail)
    assert device.SERIAL == "SY01234567890ABCDEF"
    assert device.DEVICE_TYPE == "PV Disconnect"
    assert device.TYPE == "PV-DISCONNECT"
    assert device.MODEL == "SunPower PV Disconnect Relay"
    assert device.STATE == "working"
    assert device.STATEDESCR == "Working"
    assert device.hw_version == "0.2.0"
    assert device.interface == "ttymxc5"
    assert device.slave == 230
    assert device.SWVER == "0.2.13"
    assert device.PORT == "P0, Modbus, Slave 230"
    assert device.event_history == 32
    assert device.fw_error == 0
    assert device.relay_mode == 0
    assert device.relay1_state == 1
    assert device.relay2_state == 1
    assert device.relay1_error == 0
    assert device.relay2_error == 0
    assert device.v1n_grid_v == 123.1
    assert device.v2n_grid_v == 122.5
    assert device.v1n_pv_v == 122.8
    assert device.v2n_pv_v == 122.5

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 32, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_pv_disconnect_device_from_json():
    """Test parsing of PV-DISCONNECT device from actual JSON data."""
    # Load test data
    data_path = (
        Path(__file__).parent.parent
        / "tests"
        / "fixtures"
        / "DeviceList"
        / "DeviceList.json"
    )
    with Path(data_path).open() as f:
        test_data = json.load(f)

    # Parse the data using the new() method
    response = DeviceDetailResponse.new(test_data)

    # Find the PV-DISCONNECT device in the response
    pv_disconnect_devices = [
        device for device in response.devices if isinstance(device, PVDisconnectDetail)
    ]

    # Check that we found the PV-DISCONNECT device
    assert len(pv_disconnect_devices) == 1

    device = pv_disconnect_devices[0]
    assert device.SERIAL == "SY01234567890ABCDEF"
    assert device.DEVICE_TYPE == "PV Disconnect"
    assert device.TYPE == "PV-DISCONNECT"
    assert device.MODEL == "SunPower PV Disconnect Relay"
    assert device.STATE == "working"
    assert device.STATEDESCR == "Working"
    assert device.hw_version == "0.2.0"
    assert device.interface == "ttymxc5"
    assert device.slave == 230
    assert device.SWVER == "0.2.13"
    assert device.PORT == "P0, Modbus, Slave 230"
    assert device.event_history == 32
    assert device.fw_error == 0
    assert device.relay_mode == 0
    assert device.relay1_state == 1
    assert device.relay2_state == 1
    assert device.relay1_error == 0
    assert device.relay2_error == 0
    assert device.v1n_grid_v == 123.1
    assert device.v2n_grid_v == 122.5
    assert device.v1n_pv_v == 122.8
    assert device.v2n_pv_v == 122.5

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 32, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_gateway_device_parsing():
    """Test parsing of Gateway device type."""
    # Create test data for a Gateway device
    test_data = {
        "devices": [
            {
                "ISDETAIL": True,
                "SERIAL": "BC1234006789",
                "TYPE": "GATEWAY",
                "STATE": "error",
                "STATEDESCR": "Error",
                "MODEL": "SchneiderElectric-ConextGateway",
                "DESCR": "Gateway BC1234006789",
                "DEVICE_TYPE": "Gateway",
                "interface": "sunspec",
                "mac_address": "d8:a9:ab:cd:12:34",
                "slave": 1,
                "SWVER": "V1",
                "PORT": "P0, SunSpec, Slave 1",
                "origin": "data_logger",
                "OPERATION": "noop",
                "CURTIME": "2022,05,26,14,50,33",
            }
        ],
        "result": "success",
    }

    # Parse the data using the new() method
    response = DeviceDetailResponse.new(test_data)

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"
    assert len(response.devices) == 1

    # Check that the device was correctly parsed as Gateway
    device = response.devices[0]
    assert isinstance(device, Gateway)
    assert device.SERIAL == "BC1234006789"
    assert device.DEVICE_TYPE == "Gateway"
    assert device.TYPE == "GATEWAY"
    assert device.MODEL == "SchneiderElectric-ConextGateway"
    assert device.STATE == "error"
    assert device.STATEDESCR == "Error"
    assert device.interface == "sunspec"
    assert device.mac_address == "d8:a9:ab:cd:12:34"
    assert device.slave == 1
    assert device.SWVER == "V1"
    assert device.PORT == "P0, SunSpec, Slave 1"

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 33, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_gateway_device_from_json():
    """Test parsing of Gateway device from actual JSON data."""
    # Load test data
    data_path = (
        Path(__file__).parent.parent
        / "tests"
        / "fixtures"
        / "DeviceList"
        / "GATEWAY.json"
    )
    with Path(data_path).open() as f:
        test_data = json.load(f)

    # Create a response with the gateway device
    response = DeviceDetailResponse.new({"devices": [test_data], "result": "success"})

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"
    assert len(response.devices) == 1

    # Check that the device was correctly parsed as Gateway
    device = response.devices[0]
    assert isinstance(device, Gateway)
    assert device.SERIAL == "BC1234006789"
    assert device.DEVICE_TYPE == "Gateway"
    assert device.TYPE == "GATEWAY"
    assert device.MODEL == "SchneiderElectric-ConextGateway"
    assert device.STATE == "error"
    assert device.STATEDESCR == "Error"
    assert device.interface == "sunspec"
    assert device.mac_address == "d8:a9:ab:cd:12:34"
    assert device.slave == 1
    assert device.SWVER == "V1"
    assert device.PORT == "P0, SunSpec, Slave 1"

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 33, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_schneider_xwpro_device_parsing():
    """Test parsing of Schneider XW Pro Storage Inverter device type."""
    # Create test data for a Schneider XW Pro Storage Inverter device
    test_data = {
        "devices": [
            {
                "ISDETAIL": True,
                "SERIAL": "00001ABC1234",
                "TYPE": "SCHNEIDER-XWPRO",
                "STATE": "error",
                "STATEDESCR": "Error",
                "MODEL": "SchneiderElectric-XW6848-21",
                "DESCR": "Storage Inverter 00001ABC1234",
                "DEVICE_TYPE": "Storage Inverter",
                "interface": "sunspec",
                "mac_address": "d8:a9:ab:cd:12:34",
                "parent": 11,
                "slave": 10,
                "SWVER": "V1",
                "PORT": "P0, SunSpec, Slave 10",
                "origin": "data_logger",
                "OPERATION": "noop",
                "PARENT": "00001ABC1234_01234567890ABCDEF",
                "CURTIME": "2022,05,26,14,50,33",
            }
        ],
        "result": "success",
    }

    # Parse the data using the new() method
    response = DeviceDetailResponse.new(test_data)

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"
    assert len(response.devices) == 1

    # Check that the device was correctly parsed as SchneiderXwPro
    device = response.devices[0]
    assert isinstance(device, SchneiderXwPro)
    assert device.SERIAL == "00001ABC1234"
    assert device.DEVICE_TYPE == "Storage Inverter"
    assert device.TYPE == "SCHNEIDER-XWPRO"
    assert device.MODEL == "SchneiderElectric-XW6848-21"
    assert device.STATE == "error"
    assert device.STATEDESCR == "Error"
    assert device.interface == "sunspec"
    assert device.mac_address == "d8:a9:ab:cd:12:34"
    assert device.parent == 11
    assert device.slave == 10
    assert device.SWVER == "V1"
    assert device.PORT == "P0, SunSpec, Slave 10"
    assert device.PARENT == "00001ABC1234_01234567890ABCDEF"

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 33, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_schneider_xwpro_device_from_json():
    """
    Test parsing of Schneider XW Pro Storage Inverter device from actual JSON data.
    """
    # Load test data
    data_path = (
        Path(__file__).parent.parent
        / "tests"
        / "fixtures"
        / "DeviceList"
        / "SCHNEIDER-XWPRO.json"
    )
    with Path(data_path).open() as f:
        test_data = json.load(f)

    # Create a response with the Schneider XW Pro device
    response = DeviceDetailResponse.new({"devices": [test_data], "result": "success"})

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"
    assert len(response.devices) == 1

    # Check that the device was correctly parsed as SchneiderXwPro
    device = response.devices[0]
    assert isinstance(device, SchneiderXwPro)
    assert device.SERIAL == "00001ABC1234"
    assert device.DEVICE_TYPE == "Storage Inverter"
    assert device.TYPE == "SCHNEIDER-XWPRO"
    assert device.MODEL == "SchneiderElectric-XW6848-21"
    assert device.STATE == "error"
    assert device.STATEDESCR == "Error"
    assert device.interface == "sunspec"
    assert device.mac_address == "d8:a9:ab:cd:12:34"
    assert device.parent == 11
    assert device.slave == 10
    assert device.SWVER == "V1"
    assert device.PORT == "P0, SunSpec, Slave 10"
    assert device.PARENT == "00001ABC1234_01234567890ABCDEF"

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 33, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_equiniox_bms_device_parsing():
    """Test parsing of Equiniox BMS device type."""
    # Create test data for an Equiniox BMS device
    test_data = {
        "devices": [
            {
                "ISDETAIL": True,
                "SERIAL": "BC123400678933751040",
                "TYPE": "EQUINOX-BMS",
                "STATE": "error",
                "STATEDESCR": "Error",
                "MODEL": "SchneiderElectric-SP1",
                "DESCR": "ESS BMS BC01234567890ABCDEF",
                "DEVICE_TYPE": "ESS BMS",
                "interface": "sunspec",
                "mac_address": "d8:a9:ab:cd:12:34",
                "parent": 11,
                "slave": 230,
                "SWVER": "V1",
                "PORT": "P0, SunSpec, Slave 230",
                "origin": "data_logger",
                "OPERATION": "noop",
                "PARENT": "00001ABC1234_01234567890ABCDEF",
                "CURTIME": "2022,05,26,14,50,33",
            }
        ],
        "result": "success",
    }

    # Parse the data using the new() method
    response = DeviceDetailResponse.new(test_data)

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"
    assert len(response.devices) == 1

    # Check that the device was correctly parsed as EquinioxBMS
    device = response.devices[0]
    assert isinstance(device, EquinioxBMS)
    assert device.SERIAL == "BC123400678933751040"
    assert device.DEVICE_TYPE == "ESS BMS"
    assert device.TYPE == "EQUINOX-BMS"
    assert device.MODEL == "SchneiderElectric-SP1"
    assert device.STATE == "error"
    assert device.STATEDESCR == "Error"
    assert device.interface == "sunspec"
    assert device.mac_address == "d8:a9:ab:cd:12:34"
    assert device.parent == 11
    assert device.slave == 230
    assert device.SWVER == "V1"
    assert device.PORT == "P0, SunSpec, Slave 230"
    assert device.PARENT == "00001ABC1234_01234567890ABCDEF"

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 33, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_equiniox_bms_device_from_json():
    """Test parsing of Equiniox BMS device from actual JSON data."""
    # Load test data
    data_path = (
        Path(__file__).parent.parent
        / "tests"
        / "fixtures"
        / "DeviceList"
        / "EQUINOX-BMS.json"
    )
    with Path(data_path).open() as f:
        test_data = json.load(f)

    # Create a response with the Equiniox BMS device
    response = DeviceDetailResponse.new({"devices": [test_data], "result": "success"})

    # Check that we got a valid response
    assert isinstance(response, DeviceDetailResponse)
    assert response.result == "success"
    assert len(response.devices) == 1

    # Check that the device was correctly parsed as EquinioxBMS
    device = response.devices[0]
    assert isinstance(device, EquinioxBMS)
    assert device.SERIAL == "BC123400678933751040"
    assert device.DEVICE_TYPE == "ESS BMS"
    assert device.TYPE == "EQUINOX-BMS"
    assert device.MODEL == "SchneiderElectric-SP1"
    assert device.STATE == "error"
    assert device.STATEDESCR == "Error"
    assert device.interface == "sunspec"
    assert device.mac_address == "d8:a9:ab:cd:12:34"
    assert device.parent == 11
    assert device.slave == 230
    # This device has no firmware version
    assert device.SWVER is None
    assert device.PORT == "P0, SunSpec, Slave 230"
    assert device.PARENT == "00001ABC1234_01234567890ABCDEF"

    # Check that CURTIME is parsed correctly into a datetime
    expected_curtime = datetime(2022, 5, 26, 14, 50, 33, tzinfo=ZoneInfo("UTC"))
    assert device.CURTIME == expected_curtime


def test_pvs_device_detail_last_restart_time():
    """Test PVSDeviceDetail.last_restart_time property calculation."""
    # Test case 1: Both CURTIME and dl_uptime are available
    current_time = datetime(2025, 1, 15, 12, 30, 0, tzinfo=ZoneInfo("UTC"))
    uptime_seconds = 3600  # 1 hour uptime
    expected_restart_time = current_time - timedelta(seconds=uptime_seconds)

    pvs_device = PVSDeviceDetail(
        DEVICE_TYPE="PVS",
        SERIAL="123456",
        CURTIME=current_time,
        dl_uptime=uptime_seconds,
    )

    restart_time = pvs_device.last_restart_time
    assert restart_time is not None
    assert restart_time == expected_restart_time
    assert restart_time.tzinfo == ZoneInfo("UTC")

    # Test case 2: CURTIME is None
    pvs_device_no_curtime = PVSDeviceDetail(
        DEVICE_TYPE="PVS",
        SERIAL="123456",
        CURTIME=None,
        dl_uptime=3600,
    )

    restart_time = pvs_device_no_curtime.last_restart_time
    assert restart_time is None

    # Test case 3: dl_uptime is None
    pvs_device_no_uptime = PVSDeviceDetail(
        DEVICE_TYPE="PVS",
        SERIAL="123456",
        CURTIME=current_time,
        dl_uptime=None,
    )

    restart_time = pvs_device_no_uptime.last_restart_time
    assert restart_time is None

    # Test case 4: Both CURTIME and dl_uptime are None
    pvs_device_no_data = PVSDeviceDetail(
        DEVICE_TYPE="PVS",
        SERIAL="123456",
        CURTIME=None,
        dl_uptime=None,
    )

    restart_time = pvs_device_no_data.last_restart_time
    assert restart_time is None

    # Test case 5: Large uptime value (e.g., 30 days)
    current_time = datetime(2025, 1, 15, 12, 30, 0, tzinfo=ZoneInfo("UTC"))
    uptime_seconds = 30 * 24 * 3600  # 30 days in seconds
    expected_restart_time = current_time - timedelta(seconds=uptime_seconds)

    pvs_device_large_uptime = PVSDeviceDetail(
        DEVICE_TYPE="PVS",
        SERIAL="123456",
        CURTIME=current_time,
        dl_uptime=uptime_seconds,
    )

    restart_time = pvs_device_large_uptime.last_restart_time
    assert restart_time is not None
    assert restart_time == expected_restart_time
    assert restart_time.tzinfo == ZoneInfo("UTC")


def test_battery_device_parsing():
    """Test Battery device parsing from synthetic data."""
    # Create synthetic battery device data
    battery_data = {
        "ISDETAIL": True,
        "SERIAL": "M00122109A0355",
        "TYPE": "BATTERY",
        "STATE": "error",
        "STATEDESCR": "Error",
        "MODEL": "POWERAMP-Komodo 1.2",
        "DESCR": "Battery M00122109A0355",
        "DEVICE_TYPE": "Battery",
        "hw_version": "4.34",
        "interface": "none",
        "parent": 11,
        "SWVER": "2.8",
        "PORT": "P0, None, Slave -1",
        "origin": "data_logger",
        "OPERATION": "noop",
        "PARENT": "00001ABC1234_01234567890ABCDEF",
        "CURTIME": "2022,05,26,14,50,34",
    }

    # Parse the battery device
    battery_device = Battery(**battery_data)

    # Verify the device was parsed correctly
    assert isinstance(battery_device, Battery)
    assert battery_device.SERIAL == "M00122109A0355"
    assert battery_device.DEVICE_TYPE == "Battery"
    assert battery_device.TYPE == "BATTERY"
    assert battery_device.STATE == "error"
    assert battery_device.STATEDESCR == "Error"
    assert battery_device.MODEL == "POWERAMP-Komodo 1.2"
    assert battery_device.DESCR == "Battery M00122109A0355"
    assert battery_device.hw_version == "4.34"
    assert battery_device.interface == "none"
    assert battery_device.parent == 11
    assert battery_device.SWVER == "2.8"
    assert battery_device.PORT == "P0, None, Slave -1"
    assert battery_device.origin == "data_logger"
    assert battery_device.OPERATION == "noop"
    assert battery_device.PARENT == "00001ABC1234_01234567890ABCDEF"

    # Verify CURTIME is parsed correctly into a datetime object
    expected_curtime = datetime(2022, 5, 26, 14, 50, 34, tzinfo=ZoneInfo("UTC"))
    assert battery_device.CURTIME == expected_curtime


def test_battery_device_from_json():
    """Test Battery device parsing from real JSON data."""
    # Load test data from BATTERY.json
    data_path = (
        Path(__file__).parent.parent
        / "tests"
        / "fixtures"
        / "DeviceList"
        / "BATTERY.json"
    )
    with Path(data_path).open() as f:
        battery_data = json.load(f)

    # Parse the battery device
    battery_device = Battery(**battery_data)

    # Verify the device was parsed correctly
    assert isinstance(battery_device, Battery)
    assert battery_device.SERIAL == "M00122109A0355"
    assert battery_device.DEVICE_TYPE == "Battery"
    assert battery_device.TYPE == "BATTERY"
    assert battery_device.STATE == "error"
    assert battery_device.STATEDESCR == "Error"
    assert battery_device.MODEL == "POWERAMP-Komodo 1.2"
    assert battery_device.DESCR == "Battery M00122109A0355"
    assert battery_device.hw_version == "4.34"
    assert battery_device.interface == "none"
    assert battery_device.parent == 11
    assert battery_device.SWVER == "2.8"
    assert battery_device.PORT == "P0, None, Slave -1"
    assert battery_device.origin == "data_logger"
    assert battery_device.OPERATION == "noop"
    assert battery_device.PARENT == "00001ABC1234_01234567890ABCDEF"

    # Verify CURTIME is parsed correctly into a datetime object
    expected_curtime = datetime(2022, 5, 26, 14, 50, 34, tzinfo=ZoneInfo("UTC"))
    assert battery_device.CURTIME == expected_curtime


def test_equinox_ess_device_parsing():
    """Test EquinoxESS device parsing from synthetic data."""
    ess_data = {
        "ISDETAIL": True,
        "SERIAL": "00001ABC1234_01234567890ABCDEF",
        "TYPE": "EQUINOX-ESS",
        "STATE": "error",
        "STATEDESCR": "Error",
        "MODEL": "SPWR-Equinox-model",
        "DESCR": "Energy Storage System 00001ABC1234_01234567890ABCDEF",
        "DEVICE_TYPE": "Energy Storage System",
        "hw_version": "0",
        "interface": "none",
        "SWVER": "0",
        "PORT": "P0, Parent, Slave -1",
        "origin": "data_logger",
        "OPERATION": "noop",
        "CURTIME": "2022,05,26,14,50,35",
    }
    ess_device = EquinoxESS(**ess_data)
    assert isinstance(ess_device, EquinoxESS)
    assert ess_device.SERIAL == "00001ABC1234_01234567890ABCDEF"
    assert ess_device.DEVICE_TYPE == "Energy Storage System"
    assert ess_device.TYPE == "EQUINOX-ESS"
    assert ess_device.STATE == "error"
    assert ess_device.STATEDESCR == "Error"
    assert ess_device.MODEL == "SPWR-Equinox-model"
    assert ess_device.DESCR == "Energy Storage System 00001ABC1234_01234567890ABCDEF"
    assert ess_device.hw_version == "0"
    assert ess_device.interface == "none"
    assert ess_device.SWVER == "0"
    assert ess_device.PORT == "P0, Parent, Slave -1"
    assert ess_device.origin == "data_logger"
    assert ess_device.OPERATION == "noop"
    expected_curtime = datetime(2022, 5, 26, 14, 50, 35, tzinfo=ZoneInfo("UTC"))
    assert ess_device.CURTIME == expected_curtime


def test_equinox_ess_device_from_json():
    """Test EquinoxESS device parsing from real JSON data."""
    data_path = (
        Path(__file__).parent.parent
        / "tests"
        / "fixtures"
        / "DeviceList"
        / "EQUINOX-ESS.json"
    )
    with Path(data_path).open() as f:
        ess_data = json.load(f)
    ess_device = EquinoxESS(**ess_data)
    assert isinstance(ess_device, EquinoxESS)
    assert ess_device.SERIAL == "00001ABC1234_01234567890ABCDEF"
    assert ess_device.DEVICE_TYPE == "Energy Storage System"
    assert ess_device.TYPE == "EQUINOX-ESS"
    assert ess_device.STATE == "error"
    assert ess_device.STATEDESCR == "Error"
    assert ess_device.MODEL == "SPWR-Equinox-model"
    assert ess_device.DESCR == "Energy Storage System 00001ABC1234_01234567890ABCDEF"
    assert ess_device.hw_version == "0"
    assert ess_device.interface == "none"
    assert ess_device.SWVER == "0"
    assert ess_device.PORT == "P0, Parent, Slave -1"
    assert ess_device.origin == "data_logger"
    assert ess_device.OPERATION == "noop"
    expected_curtime = datetime(2022, 5, 26, 14, 50, 35, tzinfo=ZoneInfo("UTC"))
    assert ess_device.CURTIME == expected_curtime
