import os
import pytest
from matterlab_valves.jkem_4in1_valve import JKem4in1Valve


@pytest.fixture
def mock_serial(mocker):
    mock_serial = mocker.patch("matterlab_serial_device.serial_device.serial.Serial")
    mock_serial_instance = mock_serial.return_value
    yield mock_serial_instance


@pytest.fixture
def valve_fixture(mocker, mock_serial):
    # Mock the `query` method in the `SerialDevice` class to return the expected response
    mock_query = mocker.patch("matterlab_serial_device.serial_device.SerialDevice.query")
    mock_query.return_value = "1"

    port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"
    return JKem4in1Valve(com_port=port, ports={"A": 1, "B": 2, "C": 3}, valve_num=1)


@pytest.mark.parametrize("valve_num", [1, 2, 3, 4])
def test_jkem4in1_valve_initialization(valve_fixture, mock_serial, mocker, valve_num):
    com_port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"
    mock_verify_valve_num = mocker.patch.object(valve_fixture, "_verify_valve_num")

    valve_fixture.__init__(com_port=com_port, ports={"A": 1, "B": 2, "C": 3}, valve_num=valve_num, connect_hardware=True)
    mock_verify_valve_num.assert_called_once()


def test_verify_valve_num(valve_fixture):
    assert valve_fixture.valve_num == 1

    with pytest.raises(ValueError, match="Valve number must be in between 1 and 4."):
        valve_fixture.__init__(com_port="COM1", ports={"A": 1, "B": 2, "C": 3}, valve_num=5)


def test_write_valve(valve_fixture, mocker):
    mock_write = mocker.patch.object(valve_fixture, "write")
    valve_fixture._write_valve(valve_num=1, port=2)
    mock_write.assert_called_once_with(command="/1o2R\r")


def test_query_valve(valve_fixture, mocker):
    mock_query = mocker.patch.object(valve_fixture, "query", return_value="response")
    result = valve_fixture._query_valve(valve_num=1)
    mock_query.assert_called_once_with(write_command="/1?8\r", read_until="\r", remove_from_start=3, remove_from_end=1)
    assert result == "response"


@pytest.mark.parametrize(
    "valve_num, port, expected_command",
    [
        (1, 2, "/1o2R\r"),
        (2, 3, "/2o3R\r"),
    ],
)
def test_set_current_port(valve_fixture, mocker, valve_num, port, expected_command):
    mock_write = mocker.patch.object(valve_fixture, "_write_valve")
    mock_get_current_port = mocker.patch.object(valve_fixture, "_get_current_port", return_value=port)
    mock_logger = mocker.patch.object(valve_fixture.logger, "info")

    valve_fixture._set_current_port(valve_num, port)

    mock_write.assert_called_once_with(valve_num=valve_num, port=port)
    mock_get_current_port.assert_called_once_with(valve_num=valve_num)
    mock_logger.assert_called_once_with(f"Valve on {valve_fixture.com_port} No. {valve_num} moved to {port}.")


def test_set_current_port_raises_io_error(valve_fixture, mocker):
    com_port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"

    mocker.patch.object(valve_fixture, "_write_valve")
    mocker.patch.object(valve_fixture, "_get_current_port", return_value=3)

    with pytest.raises(IOError, match=f"Move port of valve {com_port} No. 1 exceed max try."):
        valve_fixture._set_current_port(valve_num=1, port=2)


def test_get_current_port(valve_fixture, mocker):
    mock_query = mocker.patch.object(valve_fixture, "_query_valve", return_value="2")
    result = valve_fixture._get_current_port(valve_num=1)
    mock_query.assert_called_once_with(valve_num=1)
    assert result == 2


def test_get_current_port_raises_io_error(valve_fixture, mocker):
    com_port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"

    mocker.patch.object(valve_fixture, "_query_valve", side_effect=ValueError)

    with pytest.raises(IOError, match=f"Query port of valve {com_port} No. 1 exceed max try."):
        valve_fixture._get_current_port(valve_num=1)


def test_get_port(valve_fixture, mocker):
    mock_get_current_port = mocker.patch.object(valve_fixture, "_get_current_port", return_value=2)
    assert valve_fixture.port == "B"
    mock_get_current_port.assert_called_once_with(valve_num=1)


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
    mock_set_current_port.assert_called_once_with(valve_num=1, port=expected_port_num)


@pytest.mark.parametrize(
    "port, expected_port_num",
    [
        (1, 1),
        (2, 2),
        (3, 3),
    ],
)
def test_set_port_int(valve_fixture, mocker, port, expected_port_num):
    valve_fixture.__init__(com_port="COM1", ports=3, valve_num=1)

    mock_set_current_port = mocker.patch.object(valve_fixture, "_set_current_port")
    valve_fixture.port = port
    mock_set_current_port.assert_called_once_with(valve_num=1, port=expected_port_num)


def test_set_port_raises_type_error(valve_fixture):
    with pytest.raises(TypeError, match="Port must be a string or an integer."):
        valve_fixture.port = 3.14
