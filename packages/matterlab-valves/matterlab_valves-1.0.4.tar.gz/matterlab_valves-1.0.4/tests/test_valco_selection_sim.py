import os
import pytest

from matterlab_valves.valco_selection_valve import ValcoSelectionValve


@pytest.fixture
def mock_serial(mocker):
    mock_serial = mocker.patch("matterlab_serial_device.serial_device.serial.Serial")
    mock_serial_instance = mock_serial.return_value
    yield mock_serial_instance


@pytest.fixture
def valve_fixture(mocker, mock_serial):
    # Mock the `query` method in the `SerialDevice` class to return the expected response
    mock_query = mocker.patch("matterlab_serial_device.serial_device.SerialDevice.query")
    mock_query.return_value = "3"

    port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"
    return ValcoSelectionValve(com_port=port, ports={"A": 1, "B": 2, "C": 3})


def test_valco_selection_valve_initialization(valve_fixture, mock_serial, mocker):
    com_port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"

    mock_connect = mocker.patch.object(valve_fixture, "connect")
    valve_fixture.__init__(com_port=com_port, ports={"A": 1, "B": 2, "C": 3}, connect_hardware=True)
    mock_connect.assert_called_once()

    mock_connect = mocker.patch.object(valve_fixture, "connect")
    valve_fixture.__init__(com_port=com_port, ports={"A": 1, "B": 2, "C": 3}, connect_hardware=False)
    assert not mock_connect.called, "connect() shouldn't be called when connect_hardware=False"


def test_connect(valve_fixture, mocker):
    mock_set_response_mode = mocker.patch.object(valve_fixture, "_set_response_mode")
    mock_set_device_mode = mocker.patch.object(valve_fixture, "_set_device_mode")
    mock_home_valve = mocker.patch.object(valve_fixture, "_home_valve")

    valve_fixture.connect()

    mock_set_response_mode.assert_called_once()
    mock_set_device_mode.assert_called_once()
    mock_home_valve.assert_called_once()


def test_set_response_mode(valve_fixture, mocker):
    mock_write = mocker.patch.object(valve_fixture, "_write_valve")
    valve_fixture._set_response_mode()
    mock_write.assert_called_once_with("IFM1")


def test_set_device_mode(valve_fixture, mocker):
    mock_write = mocker.patch.object(valve_fixture, "_write_valve")
    mock_query = mocker.patch.object(valve_fixture, "_query_device_mode", return_value="3")

    valve_fixture._set_device_mode()

    mock_write.assert_called_once_with("AM3")
    mock_query.assert_called_once()


def test_set_device_mode_failure(valve_fixture, mocker):
    mocker.patch.object(valve_fixture, "_write_valve")
    mocker.patch.object(valve_fixture, "_query_device_mode", return_value="2")

    with pytest.raises(IOError, match="Failed to set device mode to selection valve in 5 tries."):
        valve_fixture._set_device_mode()


def test_home_valve(valve_fixture, mocker):
    mock_write = mocker.patch.object(valve_fixture, "_write_valve")
    valve_fixture._home_valve()
    mock_write.assert_called_once_with("HM")


def test_query_valve(valve_fixture, mocker):
    mock_query = mocker.patch.object(valve_fixture, "query", return_value="response")
    result = valve_fixture._query_valve("test")
    mock_query.assert_called_once_with(write_command="test\r", read_until=b"\r", remove_from_start=2, remove_from_end=1)
    assert result == "response"


def test_write_valve(valve_fixture, mocker):
    mock_write = mocker.patch.object(valve_fixture, "write")
    valve_fixture._write_valve("test")
    mock_write.assert_called_once_with(command="test\r")


def test_query_device_mode(valve_fixture, mocker):
    mock_query = mocker.patch.object(valve_fixture, "_query_valve", return_value="3")
    result = valve_fixture._query_device_mode()
    mock_query.assert_called_once_with(command="AM")
    assert result == "3"


# def test_num_ports(valve_fixture, mocker):
#     mock_query = mocker.patch.object(valve_fixture, "_query_valve", return_value="6")
#     assert valve_fixture.num_ports == 6
#     mock_query.assert_called_once_with(command="NP")


@pytest.mark.parametrize(
    "port_num, direction_cw, expected_command",
    [
        (2, True, "CW2"),
        (3, False, "CC3"),
    ],
)
def test_set_current_port(valve_fixture, mocker, port_num, direction_cw, expected_command):
    mock_write = mocker.patch.object(valve_fixture, "_write_valve")
    mock_get_current_port = mocker.patch.object(valve_fixture, "_get_current_port", return_value=port_num)
    mock_logger = mocker.patch.object(valve_fixture.logger, "info")

    valve_fixture._set_current_port(port_num, direction_cw)

    mock_write.assert_called_once_with(expected_command)
    mock_get_current_port.assert_called_once()
    mock_logger.assert_called_once_with(f"Valve on {valve_fixture.com_port} has been moved to {port_num} position.")


def test_set_current_port_raises_type_error(valve_fixture):
    with pytest.raises(TypeError, match="Port number must be an integer."):
        valve_fixture._set_current_port("invalid")


def test_set_current_port_raises_value_error(valve_fixture):
    with pytest.raises(ValueError, match="Valve port number out of range."):
        valve_fixture._set_current_port(10)


def test_get_port(valve_fixture, mocker):
    mock_get_current_port = mocker.patch.object(valve_fixture, "_get_current_port", return_value=2)
    assert valve_fixture.port == "B"
    mock_get_current_port.assert_called_once()


@pytest.mark.parametrize(
    "port, expected_port_num",
    [
        ("A", 1),
        ("B", 2),
        ("C", 3),
    ],
)
def test_set_port_dict(valve_fixture, mocker, port, expected_port_num):
    mock_set_current_port = mocker.patch.object(valve_fixture, "_set_current_port")
    valve_fixture.port = port
    mock_set_current_port.assert_called_once_with(port_num=expected_port_num)


@pytest.mark.parametrize(
    "port, expected_port_num",
    [
        (1, 1),
        (2, 2),
        (3, 3),
    ],
)
def test_set_port_int(valve_fixture, mocker, port, expected_port_num):
    valve_fixture.__init__(com_port="COM1", ports=3)

    mock_set_current_port = mocker.patch.object(valve_fixture, "_set_current_port")
    valve_fixture.port = port
    mock_set_current_port.assert_called_once_with(port_num=expected_port_num)


def test_set_port_raises_type_error(valve_fixture):
    with pytest.raises(TypeError, match="Port must be a string or an integer."):
        valve_fixture.port = 3.14
