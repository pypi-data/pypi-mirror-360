from pathlib import Path
import time
from typing import Dict, Union, Tuple, Optional, List
import struct

from matterlab_serial_device import SerialDevice, open_close

from matterlab_pumps.base_pump import SyringePump


class JKemPump(SyringePump, SerialDevice):
    category="Pump"
    ui_fields  = ("com_port", "address", "syringe_volume", "home_pos")
    def __init__(self,
                 com_port: str,
                 address: Union[str, int],
                 syringe_volume: float,
                 num_valve_port: int,
                 ports: Optional[Dict[str, int]] = None,
                 init_valve: int = 5,
                 out_valve: int = 5,
                 connect_hardware: bool = True,
                 encoding: str = "utf-8",
                 baudrate: int = 38400,
                 timeout: float = 1.0,
                 bytesize: int = 8,
                 parity: str = "none",
                 stopbits: int = 1,
                 top_speed_ml: float = 0.1,
                 home_pos: int = -14000,
                 home_pos_port: int = -6000,
                 plunger_length: int = 200000,
                 top_speed: int = 384,
                 start_speed: int = 256,
                 stop_speed: int = 256,
                 speed_slope: int = 256,
                 wait_time: float = 3600.0,
                 step_resolution: int = 4,
                 **kwargs
                 ):
        """

        :param com_port: COM port of the pump connected to, example: "COM1", "/tty/USB0"
        :param address: address of pump, set at the back of the pump, char '0' - 'E' or int 0-9
        :param ports: dict containing nickname and valve port number mapping
        :param change_def_setting_path: if load a different default setting json file,
                                        default is 'default_settings_tecan.json'
        :param syringe_volume: syringe volume in unit of L (NOT mL!!!)
        :param init_valve:  valve port num to draw from when initializing, typically air/N2, pure solvent or waste
        :param out_valve:   valve port num to dispense to when initializing, typically waste
        :param connect_hardware: if initialize hardware up on connect
        """
        SerialDevice.__init__(self,
                              com_port=com_port,
                              encoding=encoding,
                              baudrate=baudrate,
                              timeout=timeout,
                              parity=parity,
                              bytesize=bytesize,
                              stopbits=stopbits,
                              **kwargs,
                              )
        SyringePump.__init__(self,
                             address=address,
                             syringe_volume=syringe_volume,
                             num_valve_port=num_valve_port,
                             init_valve=init_valve,
                             out_valve=out_valve,
                             top_speed_ml=top_speed_ml,
                             home_pos=home_pos,
                             top_speed=top_speed,
                             start_speed=start_speed,
                             stop_speed=stop_speed,
                             speed_slope=speed_slope,
                             wait_time=wait_time,
                             ports=ports,
                             )
        self.home_pos_port = home_pos_port
        self.plunger_length = plunger_length
        self.step_resolution = step_resolution

        self.initialization_status = False
        if connect_hardware:
            self.connect()

    def connect(self):
        """
        hardware initialization function
        :return:
        """
        self._motor_reference = [False, False]
        self.initialization_status = False
        self._set_max_step()
        self._generate_valve_positions()
        self.initialize()

    @staticmethod
    def change_default_setting():
        setting_path = input("Please input new default setting json file path:\n")
        if Path(setting_path).exists() and Path(setting_path).is_file():
            return Path(setting_path)
        raise ValueError("Invalid setting path")

    @staticmethod
    def _update_address(address: Union[str, int]) -> int:
        """
        convert address of pump in str to int
        :param address:
        :return:
        """
        if isinstance(address, str):
            address = int(address)
        if 0 < address <= 16:
            return address
        else:
            raise ValueError("Address of pump must be 1-16!")

    @staticmethod
    def _checksum(command: Union[bytes, bytearray]) -> bytes:
        """
        calculate the checksum of a bytes or bytearray object and append the checksum to the end
        Parameters
        ----------
        command

        Returns
        -------

        """
        if isinstance(command, bytearray):
            command = bytes(command)
        sum = 0
        for command_byte in command:
            sum += command_byte
        checksum = command + struct.pack('B', sum & 0xFF)
        return checksum

    @open_close
    def _query_pump(self, instruction: int, command_type: int, motor: int, value: int) -> int:
        """
        query/execute the pump with a checksum_ed 9 bytes
        return None if query/execution failed
        return int value for querying
        for execution, return 0 (doesn't matter)

        Parameters
        ----------
        instruction
        command_type
        motor
        value

        Returns
        -------
        reading value in int
        """
        command = self._checksum(struct.pack('>BBBBi',
                                             self.address,
                                             instruction,
                                             command_type,
                                             motor,
                                             value))
        rtn = self.query(write_command = command, num_bytes = 9, return_bytes = True, read_delay = 0)
        if rtn[2] != 0x64:
            return None
        else:
            return struct.unpack('>i', rtn[4:8])[0]

    def _busy_report(self):
        """
        check if pump is ready for next command
            motor0 (syringe) and motor1(valve) both should have position_reached_flag == 1 (True)
        set self._ready to True if pump is ready
        set self._ready to False if pump is not ready
        Returns
        -------

        """
        motor0_status = self._query_pump(instruction = 6, command_type = 8, motor = 0, value = 0)
        motor1_status = self._query_pump(instruction=6, command_type=8, motor=1, value=0)
        if motor0_status and motor1_status:
            self._ready = True
        else:
            self._ready = False

    def _ensure_ready(self, wait_time: float = None) -> bool:
        """
        ensure the pump is ready
        Parameters
        ----------
        wait_time: max time to wait until pump is ready

        Returns: True if pump is ready
        -------

        """
        if not wait_time:
            wait_time = self.wait_time
        t0 = time.time()
        while (time.time() - t0) < wait_time:
            self._busy_report()
            if self._ready:
                return True
            else:
                time.sleep(0.05)
        raise IOError(f"Pump busy for {wait_time} seconds and not ready, exiting...")

    def _set_max_step(self):
        self._max_step = self.plunger_length + self.home_pos
    @property
    def max_step(self) -> int:
        return self._max_step

    def _set_home_position(self):
        """
        set the home position of the pump
        Parameters
        ----------

        Returns
        -------

        """
        #TODO: add two-step set home physically
        pass

    def report_plunger_absolute_position(self, max_try = 5) -> int:
        """
        report the current absolute position of the plunger
        Returns
        -------

        """
        for i in range (0, max_try):
            rtn = self._query_pump(instruction = 4, command_type = 1, motor = 0, value = 0)
            if isinstance(rtn, int):
                # print(f"Absolute plunger position is {rtn}.")
                return rtn
            time.sleep(1)
        raise IOError(f"Report plunger position of pump on {self.address} failed.")

    def _update_plunger_absolute_position(self, plunger_absolute_position: int):
        """
        update absolute plunger position internally
        Parameters
        ----------
        plunger_absolute_position

        Returns
        -------

        """
        self._plunger_absolute_position = plunger_absolute_position

    def _search_motor_reference(self, motor: int, max_wait_time = 120):
        """
        initialize the motor by searching for internal reference
        wait max_wait_time (default 120) s for finding the reference, otherwise raise error
        must follow by home
        Returns
        -------

        """
        rtn = self._query_pump(instruction = 13, command_type = 0, motor = motor, value = 0)
        if isinstance(rtn, int):
            for i in range(0, max_wait_time):
                if self._query_pump(instruction = 13, command_type = 2, motor = motor, value = 0) == 0:
                    self._motor_reference[motor] = True
                    return
                else:
                    time.sleep(1)
        raise IOError(f'Search reference of pump motor {motor} on {self.address} failed!')

    def initialize_plunger(self):
        """
        search for plunger reference (goto position 0)
        move plunger to home position
        wait until ready
        query current position, if in +/- 100 of setting,
        Returns
        -------

        """
        self._search_motor_reference(motor = 0)
        self._query_pump(instruction=4, command_type=0, motor=0, value=self.home_pos)
        self._ensure_ready(wait_time=120)
        plunger_pos = self.report_plunger_absolute_position()
        if plunger_pos in range(self.home_pos - 100, self.home_pos + 100):
            self._update_plunger_absolute_position(plunger_pos)
            print(f"Home plunger of pump on {self.address} succeed.")
            return
        raise IOError(f"Home plunger of pump on {self.address} failed.")

    def _generate_valve_positions(self):
        """
        create a list of motor positions of desired port
        self._valve_positions[0] port_1, etc.
        Returns
        -------

        """
        self._valve_positions = []
        for i in range(0, self.num_valve_port):
            pos = self.home_pos_port + int(i * 43928.0 / self.num_valve_port)
            self._valve_positions.append(pos)

    def report_valve_num(self, max_try = 5) -> int:
        """
        get the position of valve motor
        find match in +/- steps in the self_valve_positions
        Returns
        -------
        valve num in int, start from 1
        """
        for i in range(0, max_try):
            rtn = self._query_pump(instruction = 6, command_type = 1, motor = 1, value = 0)
            if isinstance(rtn, int):
                for j in range (0, self.num_valve_port):
                    if rtn in range(self._valve_positions[j] - 100, self._valve_positions[j] + 100):
                        print(f'Valve num of pump on {self.address} is {j+1}')
                        return j+1
            time.sleep(1)
        raise IOError(f'Report valve of pump on {self.address} failed.')

    def _update_valve_number(self, valve_number: int):
        """
        update the valve number internally
        Parameters
        ----------
        valve_number

        Returns
        -------

        """
        self._valve_number = valve_number

    def initialize_valve(self, init_valve: int = None):
        """

        Returns
        -------

        """
        if init_valve is None:
            init_valve = self.init_valve
        self._search_motor_reference(motor=1)
        self._query_pump(instruction=4, command_type=0, motor=1, value=self._valve_positions[init_valve - 1])
        self._ensure_ready(wait_time=30)
        valve_number = self.report_valve_num()
        if valve_number == init_valve:
            self._update_valve_number(valve_number)
            print(f"Initialize valve of pump on {self.address} succeed.")
            return
        raise IOError(f"Home valve of pump on {self.address} failed.")

    def _stop_motor(self, motor: int):
        """
        stop motor running
        Parameters
        ----------
        motor

        Returns
        -------

        """
        self._query_pump(instruction=3, command_type=0, motor=motor, value= 0)

    def stop_plunger(self):
        """
        stop the plunger moving
        Returns
        -------

        """
        self._stop_motor(motor = 0)

    def stop_valve(self):
        """
        stop the valve moving
        Returns
        -------

        """
        self._stop_motor(motor = 1)

    def _set_current(self, max_current = 100, standby_current = 20):
        """
        set the max current, do not change
        Parameters
        ----------
        max_current

        Returns
        -------

        """
        self._query_pump(instruction = 5, command_type = 6, motor = 0, value = max_current)
        self._query_pump(instruction=5, command_type=6, motor=1, value=max_current)
        self._query_pump(instruction=5, command_type=7, motor=0, value=standby_current)
        self._query_pump(instruction=5, command_type=7, motor=1, value=standby_current)

    def _set_interrupt_parameter(self):
        """
        set the interrupt parameter, do not change
        Returns
        -------

        """
        self._query_pump(instruction=9, command_type=27, motor=3, value=1)
        self._query_pump(instruction=9, command_type=29, motor=3, value=1)

    def _set_communication_parameter(self):
        """
        set the RS485 communication parameter, do not change
        Returns
        -------

        """
        self._query_pump(instruction=9, command_type=76, motor=0, value=255)

    def _set_left_switch_polarity(self):
        """
        set both motor left limit to active
        motor will stop if input is low
        Returns
        -------

        """
        self._query_pump(instruction=5, command_type=13, motor=0, value=1)
        self._query_pump(instruction=5, command_type=13, motor=1, value=1)

    def _set_reference_search_mode(self):
        """
        set the reference search mode of both motor to search left switch only
        Returns
        -------

        """
        self._query_pump(instruction=5, command_type=193, motor=0, value=1)
        self._query_pump(instruction=5, command_type=193, motor=1, value=1)

    def _set_reference_search_speed(self, speed: int = 128):
        """
        set the reference search speed of both motor,
        default search speed*2 = 256, switch speed 128
        Parameters
        ----------
        speed

        Returns
        -------

        """
        self._query_pump(instruction=5, command_type=194, motor=0, value=speed*2)
        self._query_pump(instruction=5, command_type=194, motor=1, value=speed*2)
        self._query_pump(instruction=5, command_type=195, motor=0, value=speed)
        self._query_pump(instruction=5, command_type=195, motor=1, value=speed)

    def _set_boost_current(self, boost_current = 200):
        """
        set the boost current of plunger motor
        default 200
        Parameters
        ----------
        boost_current

        Returns
        -------

        """
        self._query_pump(instruction=5, command_type=200, motor=0, value=boost_current)

    def _set_valve_max_positioning_speed(self, speed = 1024):
        """
        set the max positioning speed of valve motor
        default 1024
        Parameters
        ----------
        speed

        Returns
        -------

        """
        self._query_pump(instruction=5, command_type=4, motor=1, value=speed)

    def _set_output(self):
        """
        set digital output
        not clear with trianic manual
        Returns
        -------

        """
        self._query_pump(instruction=14, command_type=0, motor=0, value=24)
        self._query_pump(instruction=14, command_type=0, motor=0, value=56)

    def report_top_speed(self, max_try = 5) -> int:
        """
        report the top speed of the plunger
        Returns
        -------

        """
        for i in range (0, max_try):
            rtn = self._query_pump(instruction=6, command_type=4, motor=0, value=0)
            if isinstance(rtn, int):
                print(f'Top speed of plunger on pump on {self.address} is {rtn}')
                return rtn
            time.sleep(1)
        raise IOError(f"Report top speed of plunger on pump on {self.address} failed.")

    def _update_top_speed(self, top_speed):
        """
        update the topspeed value internally
        Parameters
        ----------
        top_speed

        Returns
        -------

        """
        self._top_speed = top_speed

    def set_top_speed(self, top_speed: int):
        """
        set the speed of the plunger motor
        Parameters
        ----------
        top_speed

        Returns
        -------

        """
        assert 1<= top_speed <= 2047, "Top speed out of range, min 1, max 2047."
        self._query_pump(instruction=5, command_type=4, motor=0, value=top_speed)
        if self.report_top_speed() == top_speed:
            self._update_top_speed(top_speed)
        else:
            raise IOError("Set top speed failed!")

    def set_speed_slope(self, speed_slope: int):
        """
        set the acceleration parameters of both motors
        Parameters
        ----------
        speed_slope

        Returns
        -------

        """
        self._query_pump(instruction=5, command_type=5, motor=0, value=speed_slope)
        self._query_pump(instruction=5, command_type=153, motor=0, value=6)
        self._query_pump(instruction=5, command_type=154, motor=0, value=3)
        self._query_pump(instruction=5, command_type=5, motor=1, value=speed_slope)
        self._query_pump(instruction=5, command_type=153, motor=1, value=6)
        self._query_pump(instruction=5, command_type=154, motor=1, value=3)

    def _set_step_resolution(self, step_resolution: int):
        """
        set the step resolution of plunger motor
        default 4
        Parameters
        ----------
        step_resolution

        Returns
        -------

        """
        self._query_pump(instruction=5, command_type=160, motor=0, value=0)
        self._query_pump(instruction=5, command_type=140, motor=0, value=step_resolution)
        if step_resolution == 4:
            self._query_pump(instruction=5, command_type=160, motor=0, value=1)

    def _initialize_setting(self):
        """
        test communication with motor 0 (plunger motor)
        initialize the settings of the pump
        Returns
        -------

        """
        if self._query_pump(instruction = 6, command_type = 1, motor = 0, value = 0) is None:
            raise IOError(f"Initial communication with pump on {self.address} failed.")
        print(f"Start initializing pump {self.address}")
        self.stop_plunger()
        self.stop_valve()
        self._set_current()
        self._set_interrupt_parameter()
        self._set_communication_parameter()
        self._set_left_switch_polarity()
        self._set_reference_search_mode()
        self._set_reference_search_speed()
        self._set_boost_current()
        self._set_valve_max_positioning_speed()
        self._set_output()
        self.set_top_speed(self._top_speed_def)
        self.set_speed_slope(self._speed_slope_def)
        self._set_step_resolution(self.step_resolution)

    def initialize(self, init_valve: int = None):
        """
        initialize the pump by
            1. initialize the settings
            2. initialize the valve to init port
            3. initialize the plunger to home position
        set initialize status to True
        Returns
        -------

        """
        self._initialize_setting()
        self.initialize_valve(init_valve = init_valve)
        self.initialize_plunger()
        self.initialization_status = True
        print(f"Pump on {self.address} has been initialized")

    def move_plunger(self, plunger_pos: int,
                     confirmation: bool = True,
                     ready_before_execute: int = 600,
                     ready_after_execute: bool = True):
        assert (self.home_pos - 50) <= plunger_pos <= (self._max_step + 50), "Plunger position out of range!"
        if ready_before_execute > 0:
            self._ensure_ready(ready_before_execute)
        self._query_pump(instruction=4, command_type=0, motor=0, value= plunger_pos)
        if ready_after_execute:
            self._ensure_ready()
        if confirmation:
            if self.report_plunger_absolute_position() in range (plunger_pos -50, plunger_pos + 50):
                self._update_plunger_absolute_position(plunger_pos)
                print(f'Pump {self.address} plunger moved to {self._plunger_absolute_position}.')
            else:
                raise IOError(f'Pump {self.address} move plunger failed!')
        else:
            self._update_plunger_absolute_position(self.report_plunger_absolute_position())

    def move_valve(self, valve_num: int,
                   confirmation: bool = True,
                   ready_before_execute: int = 600):
        assert 1 <= valve_num <= 8, "Valve number out of range, min 1, max 8!"
        if ready_before_execute > 0:
            self._ensure_ready(ready_before_execute)
        self._query_pump(instruction=4, command_type=0, motor=1, value=self._valve_positions[valve_num - 1])
        self._ensure_ready(wait_time=3)
        if confirmation:
            if self.report_valve_num() == valve_num:
                self._update_valve_number(valve_num)
                print(f"Pump {self.address} valve moved to {self._valve_number}.")
            else:
                raise IOError(f"Pump {self.address} move valve failed.")
        else:
            self._update_valve_number(self.report_valve_num())

    @property
    def port(self) -> int:
        """
        concrete method to report the current valve port number
        Returns
        -------
        current valve port number

        """
        return self.report_valve_num()

    @port.setter
    def port(self, port: int, **kwargs) -> None:
        """
        concrete method to set the valve number
        Parameters
        ----------
        port
        kwargs

        Returns
        -------

        """
        self.move_valve(valve_num=port, **kwargs)

    @property
    def volume(self) -> float:
        """
        concrete method to report the current volume of the plunger
        Returns
        -------

        """
        plunger_pos = self.report_plunger_absolute_position()
        volume = 1.0e3 * self.syringe_volume * (
                    plunger_pos - self.home_pos) / self.plunger_length
        return volume

    @volume.setter
    def volume(self, volume: float, **kwargs):
        """
        concrete method to set the pistion_position
        convert the piston_position in mL (float) to plunger_pos in steps (int)
            based on syringe_volume in L (float) and max_step (int)
        move plunger to designated position
        Parameters
        ----------
        volume

        Returns
        -------

        """
        plunger_pos = int((1e-3 * volume / self.syringe_volume) * self.plunger_length) + self.home_pos
        self.move_plunger(plunger_pos = plunger_pos, **kwargs)

    @property
    def top_speed_ml(self)-> float:
        """
        concrete method to get the speed of plunger based on mL/s
        Returns
        -------

        """
        speed_step = self.report_top_speed()
        speed = 0.13 * self.syringe_volume * speed_step
        return speed
 
    @top_speed_ml.setter
    def top_speed_ml(self, speed: float):
        """
        concrete method to set the speed of plunger based on mL/s
        Parameters
        ----------
        speed

        Returns
        -------

        """
        speed_step = int(speed / (0.13 * self.syringe_volume))
        if speed_step > 2047:
            speed_step = 2047
        self.set_top_speed(top_speed = speed_step)

    def set_default_speeds(self):
        pass