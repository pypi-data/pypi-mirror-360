from pathlib import Path
import time
from typing import Dict, Tuple, Optional

from matterlab_serial_device import SerialDevice, open_close

from matterlab_valves.base_valve import SwitchingValve


class ValcoSelectionValve(SwitchingValve, SerialDevice):
    category="Valve"
    ui_fields  = ("com_port", "num_port")
    def __init__(self,
                 com_port: str,
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
        self.direction_CW = direction_CW
        if connect_hardware:
            self.connect()

    def connect(self):
        """
        connect the device, hardware initialization method
        :return:
        """
        self._set_response_mode()
        self._set_device_mode()
        self.num_port = (self.num_port, False)
        self._home_valve()

    @open_close
    def _query_valve(self, command: str) -> str:
        return self.query(write_command=f'{command}\r',
                          read_until=b'\r',
                          remove_from_start=2,
                          remove_from_end=1)

    @open_close
    def _execute_valve(self, command: str):
        """
        execute operations on valve
        """
        self.write(command=f'{command}\r')

    def _set_response_mode(self):
        """
        set the response mode to basic string
        """
        self._execute_valve('IFM1')

    def _query_device_mode(self):
        return self._query_valve(command='AM')

    def _set_device_mode(self, max_trial=5):
        """
        set the device mode to selection valve
        maximum try max_trial times
        """
        for i in range(0, max_trial):
            self._execute_valve('AM3')
            rtn = self._query_device_mode()
            if rtn == '3':
                return
            else:
                continue
        raise IOError('Failed to set device mode to selection valve')

    @property
    def num_port(self) -> int:
        return int(self._query_valve(command='NP'), base=10)

    @num_port.setter
    def num_port(self, new_num_port: int, reinstall: bool = False):
        """
        set the number of port based on physical port number
        essential if change the hardware configuration
        """
        if reinstall:
            self._execute_valve('AL')
            input(f"Resetting the number of port, press Enter to confirm {new_num_port} port valve is installed.")
        self._execute_valve(f'NP{new_num_port}')

    def get_current_port(self, max_try: int = 5) -> int:
        """
        report current port position as int
        Returns
        -------

        """
        for i in range(0, max_try):
            try:
                return int(self._query_valve(command='CP'), 10)
            except:
                time.sleep(1)
                continue
        raise IOError(f'Query port of valve on {self.com_port} exceed max try.')

    def set_current_port(self, port: int, direction_CW: bool = None, max_try=5):
        """
        move the valve port to position
        move direction default in clock wise
        try to move trial times, if all failed raise error
        """
        assert isinstance(port, int), "port number must be int!"
        assert 0 < port <= self.num_port, "Valve port number out of range!"
        # if direction_CW is None:
        #     direction_CW = self.direction_CW
        for i in range(0, max_try):
            if direction_CW is None:
                self._execute_valve(f'GO{port}')
            else:
                if direction_CW:
                    self._execute_valve(f'CW{port}')
                else:
                    self._execute_valve(f'CC{port}')
            if self.get_current_port() == port:
                print(f'Valve on {self.com_port} has been moved to {port} position.')
                return None
            else:
                time.sleep(1)
                continue
        raise IOError(f'Move port of valve on {self.com_port} exceed max try.')

    def _home_valve(self):
        """
        home valve
        """
        self._execute_valve('HM')

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
        self.set_current_port(port = port)
