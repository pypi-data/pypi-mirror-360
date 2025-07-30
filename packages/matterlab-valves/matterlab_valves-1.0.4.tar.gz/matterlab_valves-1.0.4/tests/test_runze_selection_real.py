from pathlib import Path
from matterlab_valves import RunzeSelectionValve
import time

COM_PORT = "COM3"
# time.sleep(1)


def test_valve_read():
    valve = RunzeSelectionValve(com_port=COM_PORT, address = 0, num_port=10, ports={"home":1})
    assert valve.num_port == 10
    # assert valve.port == 1


def test_valve_targets():
    valve = RunzeSelectionValve(com_port=COM_PORT, address = 0, num_port=10, ports={"home":1})
    valve.port = 2
    assert valve.port == 2
    # time.sleep(5)
    valve.switch_port("home")
    assert valve.port == 1
