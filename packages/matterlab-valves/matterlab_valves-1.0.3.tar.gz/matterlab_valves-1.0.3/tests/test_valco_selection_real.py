from pathlib import Path
from matterlab_valves import ValcoSelectionValve
import time

COM_PORT = "COM5"
time.sleep(5)


def test_valve_read():
    valve = ValcoSelectionValve(com_port=COM_PORT, num_port=10, ports={"home":2})
    assert valve.num_port == 10
    assert valve.port == 1


def test_valve_targets():
    valve = ValcoSelectionValve(com_port=COM_PORT, num_port=10, ports={"home":1})
    valve.port = 2
    assert valve.port == 2
    time.sleep(5)
    valve.switch_port("home")
    assert valve.port == 1
