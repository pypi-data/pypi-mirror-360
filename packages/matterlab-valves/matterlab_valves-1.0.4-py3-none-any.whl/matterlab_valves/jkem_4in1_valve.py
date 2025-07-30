from pathlib import Path
import time
from typing import Dict, Tuple, Optional

from matterlab_serial_device import SerialDevice, open_close

from matterlab_valves.base_valve import SwitchingValve


class JKem4in1Valve(SwitchingValve, SerialDevice):
    category="Valve"
    ui_fields  = ("com_port", "valve_num", "num_port")
    def __init__(self,
                 com_port: str,
                 valve_num: int,
                 num_port: int = 8,
                 encoding: str = "utf-8",
                 baudrate: int = 9600,
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
            self.connect()

    def connect(self):
        """
        placeholder to homogenize hardware initialization
        keep here to be consistent with other hardware code
        :return:
        """
        pass

    def _verify_valve_num(self):
        if hasattr(self.settings, 'valve_num'):
            if self.valve_num in (1, 2, 3, 4):
                return
            else:
                raise ValueError("Valve_num must be in 1-4.")
        else:
            print("############################################################################",
                  "#####   Using port property for JKem valve needs to specify valve_num!   ###",
                  "############################################################################"
                  )
        #raise ValueError("JKem need to specify valve_num when instantiating.")

    @open_close
    def _execute_valve(self, valve_num: int, port: int):
        """
        execute operations on valve and port
        """
        self.write(command=f'/{valve_num}o{port}R\r')

    @open_close
    def _query_valve(self, valve_num: int) -> str:
        return  self.query(write_command=f'/{valve_num}?8\r',
                           read_until='\r',
                           remove_from_start=3,
                           remove_from_end=1)

    def get_current_port(self, valve_num: int, max_try: int = 5) -> int:
        for i in range(0, max_try):
            try:
                return int(self._query_valve(valve_num = valve_num), base = 10)
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



