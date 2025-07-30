__author__ = "Tony C. Wu (@verysure), Felix Strieth-Kalthoff (@felix-s-k), Martin Seifrid (@mseifrid)"

import time
from math import ceil
from abc import ABC, abstractmethod
from typing import Union, Optional, Dict


class SyringePump(ABC):
    # TODO: Should SyringePump have a logger?
    """
    Abstract Base Class for handling different kinds of syringe pumps.
    """
    category="Pump"
    ui_fields  = ("com_port", "address", "syringe_volume", "num_valve_port", "init_valve", "out_valve", "home_pos")
    def __init__(self,
                 address: Union[int, str],
                 syringe_volume: float,
                 num_valve_port: int,
                 init_valve: int,
                 out_valve: int,
                 top_speed_ml: float,
                 home_pos: int,
                 top_speed: float,
                 start_speed: float,
                 stop_speed: float,
                 speed_slope: float,
                 wait_time: float,
                 ports: Optional[Dict[str, int]] = None,
                 ):
        """
        take a dict define name of each port, e.g. {'N2': 1, 'water': 2} for ease of use
        Parameters
        ----------
        ports
        """
        if (init_valve > num_valve_port + 1) or (out_valve > num_valve_port + 1):
            raise ValueError("Init_valve or Out valve_num exceed num_valve_port!")
        self.address = address
        self.syringe_volume = syringe_volume
        self.num_valve_port = num_valve_port
        self.init_valve = init_valve
        self.out_valve = out_valve
        self.home_pos = home_pos
        self._top_speed_ml_def = top_speed_ml
        self._top_speed_def = top_speed
        self._start_speed_def = start_speed
        self._stop_speed_def = stop_speed
        self._speed_slope_def = speed_slope
        self.wait_time = wait_time
        self.ports: Optional[Dict[str, int]] = ports if ports else {}

    # Public Methods for Using the Syringe Pump
    def draw(self, volume: float, valve_port: Optional[Union[int, str]] = None, speed: Optional[float] = None) -> None:
        """
        Draws a specific volume through a given valve port.

        Args:
            :param volume: Volume to draw (in mL).
            :param valve_port: Identifier of the valve port to be used.
            :param speed: draw speed (in mL/s)
        """
        if volume == 0:
            return
        assert volume > 0, "Draw volume must be positive"
        current_volume = self.volume
        if (volume + current_volume) > (1.001e3 * self.syringe_volume):
            raise ValueError("Draw volume excess syringe size")
        if speed is not None:
            self.top_speed_ml = speed
        else:
            self.set_default_speeds()
        #     self.top_speed_ml = self.top_speed_ml
        if valve_port is not None:
            self.switch_port(port=valve_port)
            # valve_port: int = self.switch_port(valve_port)
            # self.port = valve_port
        self.volume = volume + current_volume
        self.top_speed = self.top_speed_ml

    def dispense(self, volume: float, valve_port: Optional[Union[int, str]] = None,
                 speed: Optional[float] = None) -> None:
        """
        Dispenses a specific volume through a given valve port.

        Args:
            :param volume: Volume to draw (in mL).
            :param valve_port: Identifier of the valve port to be used.
            :param  speed:  dispense speed (in mL/s)
        """
        if volume == 0:
            return
        assert volume > 0, "Dispense volume must be positive"
        current_volume = self.volume
        if volume > (current_volume + self.syringe_volume):
            # assess if going to dispense too much, the syringe_volume is added to avoid rounding issue
            # it is actually volume in mL / 1000, but as in setting the volume are given in L, it is multiplied back
            raise ValueError('Dispense volume excess amount in syringe')
        if speed is not None:
            self.top_speed_ml = speed
        else:
            self.set_default_speeds()
            # self.top_speed = self.top_speed_ml
        if valve_port is not None:
            self.switch_port(port=valve_port)
            # valve_port: int = self.switch_port(valve_port)
            # self.port = valve_port
        self.volume = current_volume - volume
        self.top_speed = self.top_speed_ml

    def draw_and_dispense(
            self,
            volume: float,
            draw_valve_port: Union[int, str] = None,
            dispense_valve_port: Union[int, str] = None,
            speed: Optional[float] = None,
            wait: float = 0
    ) -> None:
        """
        Draws a specified amount of volume from a specified port, and dispenses it to a specified port.
        Can temporarily change the draw/dispense velocity, if specified.

        Args:
             :param draw_valve_port: Identifier of the valve port to be used for drawing liquid.
             :param dispense_valve_port: Identifier of the valve port to be used for dispensing liquid.
             :param volume: Volume to be drawn and dispensed (in mL).
             :param wait: Waiting time between draw and dispense (in sec).
             :param speed: Draw / dispense velocity to be set temporarily (in mL/s).

        """
        # Multiple aspirations, if the dispense volume is greater than the syringe volume
        dispense_iterations = ceil(volume / (1e3 * self.syringe_volume))
        volume_per_iteration = volume / dispense_iterations
        for i in range(0, dispense_iterations):
            self.draw(volume=volume_per_iteration, valve_port=draw_valve_port, speed=speed)
            time.sleep(wait)
            self.dispense_all(valve_port=dispense_valve_port, speed=speed)
            time.sleep(wait)

    def draw_full(self, **kwargs) -> None:
        current_volume = self.volume
        draw_volume = self.syringe_volume * 1e3 - current_volume
        self.draw(volume=draw_volume, **kwargs)

    def dispense_all(self, **kwargs) -> None:
        current_volume = self.volume
        self.dispense(volume=current_volume, **kwargs)

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

    # Private Methods -> Valve Position
    @abstractmethod
    def port(self, port: int, **kwargs) -> int:
        """
        Abstract method for setting the valve to a specified port.

        Args:
            port: Integer value of the valve position.
        """
        pass

    # Private Methods -> Piston Movement and Position
    @abstractmethod
    def volume(self, volume: float, **kwargs) -> float:
        pass

    @abstractmethod
    def top_speed_ml(self) -> float:
        """
        get the speed of the plunger based on mL/s
        Returns
        -------

        """
        pass

    @abstractmethod
    def set_default_speeds(self):
        """
        set the pump to default speed
        Returns
        -------

        """
        pass

    # def __getattr__(self, attr):
    #     if attr in self.info:
    #         return self.info[attr]
    #     else:
    #         raise AttributeError(f'{attr} does not exist in obj or obj.info')
    #

class PeristalicPump(ABC):
    def __init__(self,
                 address: Union[int, str],
                #  syringe_volume: float,
                #  num_valve_port: int,
                #  init_valve: int,
                #  out_valve: int,
                #  top_speed_ml: float,
                #  home_pos: int,
                #  top_speed: float,
                #  start_speed: float,
                #  stop_speed: float,
                #  speed_slope: float,
                #  wait_time: float,
                #  ports: Optional[Dict[str, int]] = None,
                 ):
        """
        take a dict define name of each port, e.g. {'N2': 1, 'water': 2} for ease of use
        Parameters
        ----------
        ports
        """
        self.address = address
        
    @abstractmethod
    def set_pump(self,
                 speed: float,
                 start: bool,
                 direction_CCW: bool
                 ):
        pass

    @abstractmethod
    def rpm(self)->float:
        pass

    @abstractmethod
    def on(self)-> bool:
        pass

    @abstractmethod
    def direction(self)->bool:
        pass

class ContinuousSyringePump(ABC):
    def __init__(self,
                 com_port:str
                 ):
        pass

    @abstractmethod
    def speed(self)->int:
        pass