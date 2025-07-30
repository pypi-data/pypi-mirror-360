from pathlib import Path
import time
from typing import Dict, Tuple, Optional
from enum import IntEnum
from matterlab_serial_device import SerialDevice, open_close

from matterlab_valves.base_valve import SwitchingValve


class RunzeValveError(Exception):
    pass

class RunzeMotorEventType(IntEnum):
    Normal_status = 0x00
    Frame_error = 0x01
    Parameter_error = 0x02
    Optocoupler_error = 0x03
    Motor_busy = 0x04
    Motor_stalled = 0x05
    Unknown_position = 0x06
    Task_being_executed = 0xfe
    Unknown_error = 0xff

class RunzeSelectionValve(SwitchingValve, SerialDevice):
    category="Valve"
    ui_fields  = ("com_port", "address", "num_port")
    STX = 0xcc
    ETX = 0xdd

    def __init__(self,
                 com_port: str,
                 address: int,
                 num_port: int,
                 encoding: str = "utf-8",
                 baudrate: int = 9600,
                 timeout: float = 1.0,
                 parity: str = "none",
                 bytesize: int = 8,
                 stopbits: int = 1,
                 direction_CW: bool = True,
                 ports: Optional[Dict[str, int]] = None,
                 connect_hardware: bool = True,
                 **kwargs
                 ):
        SerialDevice.__init__(
            self,
            com_port=com_port,
            encoding=encoding,
            baudrate=baudrate,
            timeout=timeout,
            parity=parity,
            bytesize=bytesize,
            stopbits=stopbits,
            **kwargs
        )
        SwitchingValve.__init__(self,
                                num_port=num_port,
                                ports=ports
                                )
        self.address=address
        self.num_port=num_port
        self.direction_CW = direction_CW

    @staticmethod
    def calc_checksum(cmd:bytearray) -> bytearray:
        checksum = 0
        for item in cmd:
            checksum += item
        return bytearray([checksum & 0xff, (checksum >>8) & 0xff])

    @open_close
    def _execute_valve(self, cmd_raw: bytearray) -> bytearray:
        """
        Send execution command to the valve and get response
        :param cmd_raw: raw command
        :return:
        """
        cmd = bytearray([RunzeSelectionValve.STX]) + cmd_raw + bytearray([RunzeSelectionValve.ETX])
        cmd += self.calc_checksum(cmd)
        rtn = self.query(write_command=cmd, return_bytes = True)
        if len(rtn):
            return bytearray(rtn)
        else:
            raise RunzeValveError("Return 0 length data, communication failed")

    def set_address(self, address: int) -> None:
        """
        Set the RS485 address of the valve
        :param address: RS485 address, range [0x00, 0x7F], default 0x00
        :return:
        """
        if "Yes" != input("Changing RS485 address is dangerous, MUST label on the valve right after!\n"
                          "Type Yes for confirmation:\n") :
            print("Set RS485 address CANCELLED")
            return
        if not 0x00 <= address <= 0x7f:
            raise ValueError("RS485 address out of range [0, 0x7f]")
        self._execute_valve(bytearray([self.address, 0x00, 0xff, 0xee, 0xbb, 0xaa, address, 0x00,0x00,0x00]))
        print(f"RS485 address of valve set to {address}. Please disconnect power and label the address on the hardware!")

    def set_baudrate(self) -> None:
        """
        Set the RS485 baudrate of the valve
        :return:
        """
        if "Yes" != input("Changing RS485 baudrate is dangerous, MUST label on the valve right after!\n"
                          "Type Yes for confirmation:\n"):
            print("Set RS485 baudrate CANCELLED")
            return
        baud_options = {"9600": 0x00, "19200": 0x01, "38400": 0x02, "57600": 0x03, "115200": 0x04}
        baud = input("Enter baudrate (9600, 19200, 38400, 57600, 115200):\n")
        if baud not in baud_options:
            raise ValueError("Invalid baudrate entered")
        self._execute_valve(
            bytearray([self.address, 0x02, 0xff, 0xee, 0xbb, 0xaa, baud_options[baud], 0x00, 0x00, 0x00]))
        print(f"RS485 baudrate of valve set to {baud}, Please disconnect power and label the address on the hardware!")

    def restore_factory(self) -> None:
        """
        restore factory settings
        :return:
        """
        if "Yes" != input("Restoring factory settings!\n"
                          "Type Yes for confirmation:\n"):
            print("Restore factory settings CANCELLED")
            return
        self._execute_valve(bytearray([self.address, 0xff, 0xff, 0xee, 0xbb, 0xaa, 0x00, 0x00, 0x00, 0x00]))
        print("Restored factory settings")

    def check_motor(self) -> int:
        """
        Check motor status
        :return: status code
        """
        try:
            rtn = self._execute_valve(bytearray([self.address, 0x4a, 0x00, 0x00]))
            status = RunzeMotorEventType(rtn[2])
            print(f"Motor status {status.name}")
            return status.value
        except ValueError:
            raise RunzeValveError("Unknown motor status")

    def get_current_port(self) -> int:
        """
        Get the current port of the valve
        :return: current port
        """
        rtn = self._execute_valve(bytearray([self.address, 0x3e, 0x00, 0x00]))
        self._port = int(rtn[3])
        return self._port

    def set_current_port(self, port: int, direction_CW: bool = None, confirmation: bool = True):
        """
        Set the current port of the valve through closest path
        :param port: target port to move to
        :param direction_CW: None to take the closest path, True to move clock wise, False to counter clock wise
        :param confirmation: True to enable confirmation moving to correct port
        :return:
        """
        if not 1 <= port <= self.num_port:
            raise ValueError(f"Port number out of range, default [1, {self.num_port}], set to {port}")
        if direction_CW is None:
            rtn = self._execute_valve(bytearray([self.address,0x44, port, 0x00]))
        else:
            if direction_CW:
                through_port = 1 if port == self.num_port else port + 1
            else:
                through_port = self.num_port if port == 1 else port - 1
            rtn = self._execute_valve(bytearray([self.address, 0xa4, through_port, port]))
        if rtn[2] != 0xfe:
            raise RunzeValveError("Set port failed, did not return 'Task being executed'")
        if confirmation:
            time.sleep(0.5)
            current_port = self.get_current_port()
            if current_port != port:
                raise RunzeValveError(f"Set port failed: Expected {port}, got {current_port}")
        else:
            self._port = port

    def reset(self, origin: bool = False) -> None:
        """
        Reset the valve to home position
        :param origin: reset to original home of the encoder
        :return:
        """
        if origin:
            self._execute_valve(bytearray([self.address, 0x4f, 0x00, 0x00]))
        else:
            self._execute_valve(bytearray([self.address, 0x45, 0x00, 0x00]))
        self._port=1

    def set_between_ports(self, port) -> None:
        """
        Move the
        :param port: 0.5 position AFTER port (e.g. if port == 1, valve move to between 1 and 2)
        :return:
        """
        if not 1 <= port <= self.num_port:
            raise ValueError(f"Port number out of range, default [1, {self.num_port}], set to {port}")
        port_adjacent = 1 if port == self.num_port else port + 1
        self._execute_valve(bytearray([self.address, 0xb4, port, port_adjacent]))

    def _home_valve(self) -> None:
        """
        Home valve, same function name as of Valco
        :return:
        """
        self.reset(origin=False)

    @property
    def port(self) -> int:
        """
        concrete method to report the port of valve
        """
        return self.get_current_port()

    @port.setter
    def port(self, port: int):
        """
        concrete method to set the port of valve
        """
        self.set_current_port(port=port)