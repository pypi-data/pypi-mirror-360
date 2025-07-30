import pytest
from typing import Union
from matterlab_valves import SwitchingValve  # Replace 'your_module' with the actual module name


class MockSwitchingValve(SwitchingValve):
    def _write_valve(self, command: str) -> None:
        pass

    def _query_valve(self, command: str) -> str:
        return ""

    @property
    def port(self) -> Union[str, int]:
        return "A"

    @port.setter
    def port(self, port_id: Union[str, int]) -> None:
        pass


def test_switching_valve_abstract_methods():
    with pytest.raises(TypeError):
        SwitchingValve(ports={"A": 1, "B": 2})


def test_switching_valve_instantiation_with_dict():
    ports = {"A": 1, "B": 2, "C": 3}
    valve = MockSwitchingValve(ports=ports)
    assert isinstance(valve, SwitchingValve)
    assert valve.ports == ports


def test_switching_valve_instantiation_with_int():
    valve = MockSwitchingValve(ports=3)
    assert isinstance(valve, SwitchingValve)
    assert valve.ports == {1: 1, 2: 2, 3: 3}


def test_switching_valve_instantiation_with_invalid_type():
    with pytest.raises(TypeError, match="ports must be a dict or an int."):
        MockSwitchingValve(ports="invalid")


def test_switching_valve_get_port_num():
    valve = MockSwitchingValve(ports={"A": 1, "B": 2})
    assert valve._get_port_num("A") == 1
    assert valve._get_port_num("B") == 2

    valve = MockSwitchingValve(ports=2)
    assert valve._get_port_num(1) == 1
    assert valve._get_port_num(2) == 2


def test_switching_valve_get_port_num_invalid():
    valve = MockSwitchingValve(ports={"A": 1, "B": 2})
    with pytest.raises(KeyError):
        valve._get_port_num("C")

    valve = MockSwitchingValve(ports=2)
    with pytest.raises(KeyError):
        valve._get_port_num(3)


def test_switching_valve_get_port_id():
    valve = MockSwitchingValve(ports={"A": 1, "B": 2})
    assert valve._get_port_id(1) == "A"
    assert valve._get_port_id(2) == "B"

    valve = MockSwitchingValve(ports=2)
    assert valve._get_port_id(1) == 1
    assert valve._get_port_id(2) == 2


def test_switching_valve_get_port_id_invalid():
    valve = MockSwitchingValve(ports={"A": 1, "B": 2})
    with pytest.raises(KeyError, match="Port number 3 not found in the ports."):
        valve._get_port_id(3)


def test_switching_valve_port_property():
    valve = MockSwitchingValve(ports={"A": 1, "B": 2})
    assert valve.port == "A"  # This is the default value we set in MockSwitchingValve
