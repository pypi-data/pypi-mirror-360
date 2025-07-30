from multiprocessing import Value
from pathlib import Path
import time
from typing import Dict, Tuple, Optional, Union
from struct import pack, unpack

from matterlab_serial_device import SerialDevice, open_close

from matterlab_valves.base_valve import SwitchingValve


class JKemNewValve(SwitchingValve, SerialDevice):
    category="Valve"
    ui_fields  = ("com_port", "valve_num", "num_port")
    def __init__(self,
                 com_port: str,
                 valve_num: int,
                 num_port: int = 8,
                 encoding: str = "utf-8",
                 baudrate: int = 38400,
                 timeout: float = 1.0,
                 parity: str = "none",
                 bytesize: int = 8,
                 stopbits: int = 1,
                 ports: Optional[Dict[str, int]] = None,
                 connect_hardware: bool = True,
                 **kwargs
                 ):
        """
        :param com_port: COM port of the pump connected to, example: "COM1", "/tty/USB0"
        :param ports: dict containing nickname and valve port number mapping
        :param connect_hardware: if connect hardware up on initialization
        :return:
        """
        
        SerialDevice.__init__(self,
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
        self.valve_num = valve_num
        if connect_hardware:
            self.connect(self.valve_num)
            
    @staticmethod
    def calculate_checksum(raw_cmd_byte: Union[bytes, bytearray])->Union[bytes, bytearray]:
        sum_of_bytes = 0
        for b in raw_cmd_byte:
            sum_of_bytes += b
        return raw_cmd_byte + pack("<H", sum_of_bytes)
        
    @open_close
    def connect(self, valve_num: int = 1):
        """
        connect device, raise error if failed, default try to connect valve 1 
        :return: 0 for success
        """
        cmd = bytearray([204, valve_num, 74, 0, 0, 221])
        cmd_checked = self.calculate_checksum(cmd)
        rtn = self.query(write_command = cmd_checked,
                   read_until="",
                   remove_from_start=2,
                   remove_from_end=5
                   )
        if len(rtn) != 1:
            raise IOError("Connecting valve failed!")
        if unpack("B", rtn)[0] != 0:
            raise IOError("Connecting valve failed!")
        return 0
    
    @open_close
    def _execute_valve(self, valve_num: int, port: int)->int:
        """
        execute operation on valve and port
        :return: -1 for failure, 0 for success
        """
        cmd = bytearray([204, valve_num, 68, port, 0, 221])
        cmd_checked = self.calculate_checksum(cmd)
        rtn = self.query(write_command = cmd_checked,
                   read_until=""
                   )
        if len(rtn) != 8:
            return -1
        else:
            return 0
        
    @open_close
    def _query_valve(self, valve_num: int) -> int:
        """
        query valve for port info
        :return: current port number, or -1 for failue
        """
        cmd = bytearray([204, valve_num, 62, 0, 0, 221])
        cmd_checked = self.calculate_checksum(cmd)
        rtn =  self.query(write_command=cmd_checked,
                          read_until="",
                          remove_from_start=3,
                          remove_from_end=4
                          )
        if len(rtn) != 1:
            return -1
        return unpack("B", rtn)[0]

    
    def get_current_port(self, valve_num: int, max_try: int = 5) -> int:
        for i in range(0, max_try):
            try:
                return self._query_valve(valve_num = valve_num)
            except:
                time.sleep(1)
                continue
        raise IOError(f'Query port of valve {self.com_port} No. {valve_num} exceed max try.')

    def set_current_port(self, valve_num: int, port: int, max_try: int = 5):
        for i in range(0, max_try):
            self._execute_valve(valve_num = valve_num, port = port)
            if self.get_current_port(valve_num = valve_num) == port:
                print(f'Valve on {self.com_port} No. {valve_num} has been moved to {port}')
                time.sleep(1)
                return None
            else:
                time.sleep(1)
                continue
        raise IOError(f'Move port of valve {self.com_port} No. {valve_num} exceed max try.')

    @property
    def port(self) -> int:
        """
        concrete method to get current port
        """
        return self.get_current_port(valve_num=self.valve_num)

    @port.setter
    def port(self, port: int):
        """
        concrete method to set current port
        """
        self.set_current_port(valve_num=self.valve_num, port = port)
