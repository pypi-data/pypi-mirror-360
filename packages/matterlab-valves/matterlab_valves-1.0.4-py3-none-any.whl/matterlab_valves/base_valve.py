from abc import ABC, abstractmethod
from typing import Dict, Optional, Union


class SwitchingValve(ABC):
    # TODO: Should SwitchingValve have a logger?
    category="Valve"
    """
    Abstract Base Class for handling different kinds of switching valves.
    """
    category="Valve"
    ui_fields  = ("com_port", "num_port")
    def __init__(self,
                 num_port: int,
                 ports: Optional[Dict[str, int]] = None) -> None:
        """
        Args:
            ports: Dictionary of human identifiers for the ports, with the respective port numbers as values.
        """
        self.num_port = num_port
        self.ports: Optional[Dict[str, int]] = ports if ports else {}

    # Public Methods for Using the Switching Valve
    @abstractmethod
    def port(self) -> int:
        """
        Abstract method that reads the current valve position.
        """
        pass

    def switch_port(self, port: Union[str, int]) -> int:
        """
        If applicable, converts the human identifier for a port (as key in the ports attribute) to the respective
        computer identifier.

        Args:
            port: Human identifier for the port.

        Returns:
            int: Port number, as required for communication with the pump.
        """
        if isinstance(port, str):
            port = self.ports.get(port)
        if port is not None:
            self.port = port
            return port
        else:
            raise ValueError('Wrong ports')

    # Private methods for translating the port id and name
    def _get_port_id(self, port_num: int) -> Union[str, int]:
        """
        Retrieve the port ID based on port number.

        Args:
            port_num: Port number.

        Returns:
            port_id: Port ID.
        """
        for port_id, port in self.ports.items():
            if port == port_num:
                return port_id
        raise KeyError(f'Port number {port_num} not found in ports.')

