from __future__ import annotations
import time
from typing import Dict, Union

from matterlab_serial_device import SerialDevice, open_close
from matterlab_pumps.base_pump import PeristalicPump


class LongerPeristalticPump(PeristalicPump, SerialDevice):
    category="Pump"
    """
    A peristaltic pump controller that communicates over a serial interface.

    Inherits from PeristalicPump for pump logic and SerialDevice for serial comms.

    Attributes:
        _rpm (float): Current pump speed in revolutions per minute.
        _on (bool): Pump running state.
        _direction (bool): Pump direction (True for CCW, False for CW).
    """

    def __init__(
        self,
        com_port: str,
        address: int,
        encoding: str = "utf-8",
        baudrate: int = 9600,
        timeout: float = 1.0,
        parity: str = "even",
        bytesize: int = 8,
        stopbits: int = 1,
        **kwargs,
    ) -> None:
        """
        Initialize the pump controller.

        Args:
            com_port (str): Serial port identifier (e.g., 'COM3' or '/dev/ttyUSB0').
            address (int): Device address for Modbus protocol.
            encoding (str, optional): Serial text encoding. Defaults to 'utf-8'.
            baudrate (int, optional): Communication speed. Defaults to 9600.
            timeout (float, optional): Read/write timeout in seconds. Defaults to 1.0.
            parity (str, optional): Parity setting ('even', 'odd', 'none'). Defaults to 'even'.
            bytesize (int, optional): Number of data bits (5, 6, 7, or 8). Defaults to 8.
            stopbits (int, optional): Number of stop bits (1, 1.5, or 2). Defaults to 1.
            **kwargs: Additional keyword args for SerialDevice.
        """
        SerialDevice.__init__(
            self,
            com_port=com_port,
            encoding=encoding,
            baudrate=baudrate,
            parity=parity,
            timeout=timeout,
            bytesize=bytesize,
            stopbits=stopbits,
            **kwargs,
        )
        PeristalicPump.__init__(self, address=address)
        self._rpm: float = 0.0
        self._on: bool = False
        self._direction: bool = False

    def _generate_execute_command(
        self,
        rpm: float,
        on: bool,
        direction: bool,
    ) -> bytes:
        """
        Build the Modbus command to on/stop the pump at the desired speed and direction.

        Args:
            rpm (float): Desired speed in RPM.
            on (bool): True to on the pump, False to stop.
            direction (bool): True for counter-clockwise rotation.

        Returns:
            bytes: Full command packet ready for transmission.
        """
        # Header: [address, function=0x06, register_high=0x57, register_low=0x4A]
        cmd = bytearray([self.address, 0x06, 0x57, 0x4A])
        # Speed is scaled by 10 (1 digit after decimal)
        speed_int = int(rpm * 10)
        cmd.extend([(speed_int >> 8) & 0xFF, speed_int & 0xFF])
        # Flags: on and direction
        cmd.append(int(on))
        cmd.append(int(direction))
        # Append checksum (XOR of all bytes)
        checksum = 0
        for b in cmd:
            checksum ^= b
        cmd.append(checksum)
        # Prefix with 0xE9
        return b"\xE9" + bytes(cmd)

    def _generate_query_command(self) -> bytes:
        """
        Build the Modbus command to query the current pump state.

        Returns:
            bytes: Full query packet ready for transmission.
        """
        cmd = bytearray([self.address, 0x02, 0x52, 0x4A])
        checksum = 0
        for b in cmd:
            checksum ^= b
        cmd.append(checksum)
        return b"\xE9" + bytes(cmd)

    @open_close
    def set_pump(
        self,
        rpm: float | None = None,
        on: bool | None = None,
        direction: bool | None = None,
    ) -> None:
        """
        Update pump settings and send command to device.

        Args:
            rpm (float, optional): Target speed in RPM. If None, previous speed is retained.
            on (bool, optional): True to on, False to stop. If None, previous state is retained.
            direction (bool, optional): True for CCW, False for CW. If None, previous direction is retained.
        """
        rpm = self._rpm if rpm is None else rpm
        on = self._on if on is None else on
        direction = self._direction if direction is None else direction

        packet = self._generate_execute_command(
            rpm=rpm, on=on, direction=direction
        )
        self.query(write_command=packet, return_bytes=True, num_bytes=6)

    @open_close
    def query_pump(self) -> Dict[str, Union[float, bool]]:
        """
        Query the pump's current status and update internal state.

        Returns:
            dict: Dictionary with keys 'rpm', 'on', 'direction'.
        """
        packet = self._generate_query_command()
        response = self.query(write_command=packet, return_bytes=True, num_bytes=10)
        # Small delay to allow device processing
        time.sleep(0.5)
        # Parse speed: two bytes at positions 5 and 6
        speed_raw = (response[5] << 8) | response[6]
        self._rpm = speed_raw / 10.0
        # Parse flags at positions 7 and 8
        self._on = bool(response[7])
        self._direction = bool(response[8])
        return {"rpm": self._rpm, "on": self._on, "direction": self._direction}

    @property
    def rpm(self) -> float:
        """
        Get the latest RPM reading from the pump.
        """
        return self.query_pump()["rpm"]

    @rpm.setter
    def rpm(self, value: float) -> None:
        """
        Set a new pump speed (RPM) without changing other states.
        """
        self.set_pump(rpm=value)

    @property
    def on(self) -> bool:
        """
        Get the pump's running state.
        """
        return self.query_pump()["on"]

    @on.setter
    def on(self, value: bool) -> None:
        """
        on or stop the pump without changing speed or direction.
        """
        self.set_pump(on=value)

    @property
    def direction(self) -> bool:
        """
        Get the pump's current rotation direction (True for CCW).
        """
        return self.query_pump()["direction"]

    @direction.setter
    def direction(self, value: bool) -> None:
        """
        Change the pump's rotation direction without altering speed or runtime state.
        """
        self.set_pump(direction=value)
