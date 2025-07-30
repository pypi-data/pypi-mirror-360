import time
from typing import Dict, Union, Tuple, Optional, List
from matterlab_serial_device import SerialDevice, open_close
from matterlab_pumps.base_pump import SyringePump


class TecanXCPump(SyringePump, SerialDevice):
    category="Pump"
    ui_fields  = ("com_port", "address", "syringe_volume", "num_valve_port", "init_valve", "out_valve", "home_pos")
    def __init__(self,
                 com_port: str,
                 address: Union[str, int],
                 syringe_volume: float,
                 num_valve_port: int,
                 ports: Optional[Dict[str, int]] = None,
                 init_valve: int = 1,
                 out_valve: int = 12,
                 connect_hardware: bool = True,
                 encoding: str = "utf-8",
                 baudrate: int = 9600,
                 timeout: float = 0.2,
                 bytesize: int = 8,
                 parity: str = "none",
                 stopbits: int = 1,
                 top_speed_ml: float = 0.1,
                 direction_CW: bool = True,
                 fine_pos: bool = True,
                 home_pos: int = 20,
                 backlash_pos: int = 12,
                 top_speed: int = 1000,
                 start_speed: int = 800,
                 stop_speed: int = 800,
                 speed_slope: int =14,
                 wait_time: float = 3600.0,
                 error_msg: List = [
                                    "No Error",
                                    "Initialization Error",
                                    "Invalid Command",
                                    "Invalid Operand",
                                    "Invalid Command Sequence",
                                    "Error Code Not Used",
                                    "EEPROM Failure",
                                    "Device Not Initialized",
                                    "Error Code Not Used",
                                    "Plunger Overload",
                                    "Valve Overload",
                                    "Plunger Move Not Allowed",
                                    "Error Code Not Used",
                                    "Error Code Not Used",
                                    "Error Code Not Used",
                                    "Command Overflow"
                                  ],
                 **kwargs
                 ):
        """
        :param com_port: COM port of the pump connected to, example: "COM1", "/tty/USB0"
        :param address: address of pump, set at the back of the pump, char '0' - 'E' or int 0-9
        :param syringe_volume: syringe volume in unit of L (NOT mL!!!)
        :param num_valve_port: number of valve ports for selection/distribution
        :param ports: dict containing nickname and valve port number mapping
        :param init_valve: valve port num to draw from when initializing, typically air/N2, pure solvent or waste
        :param out_valve: valve port num to dispense to when initializing, typically waste
        :param connect_hardware: if initialize hardware up on connect
        :param encoding: encoding of command, default utf-8
        :param baudrate: baudrate for communication, default 9600
        :param timeout: timeout for communication, default 0.2 s
        :param bytesize: bytesize for communication, default 8
        :param parity: parity for communication, default none
        :param stopbits: stopbits for communication, default 1
        :param top_speed_ml: default speed for transfer, for 1/16 0.03 tubing, 0.1 mL/s
        :param direction_CW: direction of selection valve indexing, default True for clockwise
        :param fine_pos: turn on/off fine positioning, default True
        :param home_pos: home position, default 20
        :param backlash_pos: backlash steps, default 12
        :param top_speed: top speed by steps, default 1000
        :param start_speed: start speed by steps, default 800
        :param stop_speed: stop speed by steps, default 800
        :param speed_slope: speed slop grading, default 14
        :param wait_time: max wait time for a transfer, default 3600 s or 1 h
        :param error_msg: error messages from pump
        :param kwargs:
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
        self.direction_CW = direction_CW
        self.fine_pos = fine_pos
        self.backlash_pos = backlash_pos
        self.error_msg = error_msg
        # Tecan syringe pump use its own way of addressing RS485 device, and is used as self.address in code
        # so initialize the RS485 device with common address format, then update the self.address
        address = self._update_address(address)
        self.address = address

        self.initialization_status = False
        if connect_hardware:
            self.connect()

    def connect(self):
        """
        hardware initialization function
        :return:
        """
        self._set_fine_position()
        self._set_backlash_position()
        self._set_home_position()
        self.initialize_pump()
        self.set_top_speed(top_speed=self._top_speed_def, auto_start_stop_speed=True)
        self.set_speed_slope(speed_slope=self._speed_slope_def)

    @staticmethod
    def _update_address(address: Union[str, int]) -> str:
        """
        update the address setting
        translate   int 0, 1, 2,... 8, 9, 10, ...14
                    str '0', '1', '2',... '8', '9', 'A',... 'E'
            to      chr '1', '2', '3',... '9', ':', ';',... '?'
        Returns
        -------

        """
        if isinstance(address, int):
            return chr(49 + address)
        elif isinstance(address, str):
            return chr(int(('0x' + address), 0) + 49)
        else:
            raise TypeError('Invalid pump address.')

    @open_close
    def _query_pump(self, command: str) -> str:
        """
        send query command to pump
        return sliced return value in str
        Parameters
        ----------
        command

        Returns
        -------

        """
        return self.query(write_command=f"/{self.address}{command}\r",
                          remove_from_start=3, remove_from_end=3, read_delay= 0.05)

    @open_close
    def _execute_pump(self, command: str):
        """
        execute command
        R for 'RUN'
        Parameters
        ----------
        command

        Returns
        -------

        """
        self.write(f"/{self.address}{command}R\r")
        time.sleep(0.05)

    @open_close
    def _busy_report(self):
        """
        check if pump is ready for next command
        set self._ready to True if pump is ready
        set self._ready to False if pump is not ready
        raise IOError if pump report error
        Returns
        -------

        """
        rtn = self.query(write_command=f"/{self.address}Q\r",
                         read_delay=0,
                         read_until=b"\r\n",
                         remove_from_end=2,
                         return_bytes = True,
                         )
        if len(rtn) < 3:  # no meaningful return means communication failure, pump is not ready
            self._ready = False
            return
        if rtn[2] == 0x60:  # 3rd byte is 0x60 (int 96) means pump is ready
            self._ready = True
            return
        else:
            self._ready = False  # pump is not ready
        if rtn[2] != 0x40:  # 3rd byte is 0x40 (int 64) means pump is simply not ready
            error_num = rtn[2] % 16  # not 0x40 means hardware error, raise error message
            raise IOError(self.error_msg[error_num])

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
                time.sleep(0.1)
        raise IOError(f"Pump busy for {wait_time} seconds and not ready, exiting...")

    def _set_fine_position(self):
        """
        set the fine position of the pump
        if fine position, range (0, 240001), else (0, 3001) NOTE: five folds
        can ONLY be called before initialization!
        Returns
        -------

        """
        print(self.fine_pos)
        if self.fine_pos:
            self._max_step = 24000
            self.home_pos *= 8
            self.backlash_pos *= 8
            self._execute_pump(command='N1')
        else:
            self._max_step = 3000
            self._execute_pump(command='N0')
        print(f"Fine position is {str(self.fine_pos)}")

    def report_backlash_position(self):
        rtn = int(self._query_pump(command='?12'))
        print(f"Backlash_position is {rtn}.")
        return rtn

    def _update_backlash_position(self, backlash_position):
        self._backlash_position = backlash_position

    def _set_backlash_position(self):
        """
        set the backlash position of the pump
        can ONLY be called before initialization!
        Parameters
        ----------

        Returns
        -------

        """
        self._execute_pump(command=f'K{self.backlash_pos}')
        if self.report_backlash_position() == self.backlash_pos:
            self._update_backlash_position(self.backlash_pos)
        else:
            raise IOError("Set backlash position failed.")

    def report_home_position(self):
        rtn = int(self._query_pump(command='?24'))
        print(f"Home_position is {rtn}.")
        return rtn

    def _update_home_position(self, position):
        self._home_position = position

    def _set_home_position(self):
        """
        set the home position of the pump
        can only be called BEFORE initializing a pump
        Parameters
        ----------

        Returns
        -------

        """
        # TODO: add two-step set home physically
        self._execute_pump(command=f'k{self.home_pos}')
        if self.report_home_position() == self.home_pos:
            self._update_home_position(self.home_pos)
        else:
            raise IOError("Set home position failed.")

    def report_start_speed(self):
        rtn = int(self._query_pump(command='?1'))
        #print(f"Start speed is {rtn}.")
        return rtn

    def _update_start_speed(self, start_speed):
        self._start_speed = start_speed

    def set_start_speed(self, start_speed: int = 800):
        """
        set the start speed of the pump, range (50, 1001)
        Parameters
        ----------
        start_speed

        Returns
        -------

        """
        if start_speed < 50:
            start_speed = 50
        if start_speed > 1000:
            start_speed = 1000
        self._execute_pump(command=f'v{start_speed}')
        if self.report_start_speed() == start_speed:
            self._update_start_speed(start_speed)
        else:
            raise IOError("Set start speed failed!")

    def report_top_speed(self):
        rtn = int(self._query_pump(command='?2'))
        #print(f"Top speed is {rtn}.")
        return rtn

    def _update_top_speed(self, top_speed):
        self._top_speed = top_speed

    def set_top_speed(self, top_speed: int = 1000, auto_start_stop_speed: bool = True):
        """
        set the start speed of the pump, range (50, 6001)
        Notes: top_speed need to set to 2701 at beginning to avoid set start/stop speed failure
        Parameters
        ----------
        top_speed

        Returns
        -------

        """
        self._execute_pump(command=f'V2701')
        if top_speed < 50:
            top_speed = 50
        if top_speed > 6000:
            top_speed = 6000
        if auto_start_stop_speed:
            self.set_start_speed(start_speed=int(top_speed * 0.8))
            self.set_stop_speed(stop_speed=top_speed)
        self._execute_pump(command=f'V{top_speed}')
        if self.report_top_speed() == top_speed:
            self._update_top_speed(top_speed)
        else:
            raise IOError("Set top speed failed!")

    def report_stop_speed(self):
        rtn = int(self._query_pump(command='?3'))
        #print(f"Stop speed is {rtn}.")
        return rtn

    def _update_stop_speed(self, stop_speed):
        self._stop_speed = stop_speed

    def set_stop_speed(self, stop_speed: int = 800):
        """
        set the stop speed of the pump, range (50, 2701)
        Parameters
        ----------
        stop_speed

        Returns
        -------

        """
        if stop_speed < 500:
            stop_speed = 500
        if stop_speed > 2700:
            stop_speed = 2700
        self._execute_pump(command=f'c{stop_speed}')
        if self.report_stop_speed() == stop_speed:
            self._update_stop_speed(stop_speed)
        else:
            raise IOError("Set stop speed failed!")

    def set_speed_slope(self, speed_slope: int = 14):
        """
        set the speed slope, higher accelerate faster
        Parameters
        ----------
        speed_slope

        Returns
        -------

        """
        assert 1 <= speed_slope < 21, "Speed slope out of range"
        self._execute_pump(command=f'L{speed_slope}')

    def set_default_speeds(self):
        self.set_start_speed(int(self._start_speed_def))
        self.set_stop_speed(int(self._stop_speed_def))
        self.set_speed_slope(int(self._speed_slope_def))
        self.set_top_speed(int(self._top_speed_def))

    def report_buffer_status(self):
        self._buffer_status = bool(int(self._query_pump(command='?10')))

    def report_number_initialization(self):
        self._number_initialization = int(self._query_pump(command='?15'))
        print(f"Number_initialization is {self._number_initialization}.")

    def report_plunger_move_counting(self):
        self._plunger_move = int(self._query_pump(command='?16'))
        print(f"Plunger_move is {self._plunger_move}.")

    def report_valve_move_counting(self):
        self._valve_move = int(self._query_pump(command='?17'))
        print(f"Valve_move is {self._valve_move}.")

    def report_firmware_version(self):
        print(f"Firmware version is {self._query_pump(command='23')}")

    def report_pump_configuration(self):
        print(f"Pump configuration is {self._query_pump(command='76')}")

    def report_plunger_absolute_position(self) -> int:
        rtn = int(self._query_pump(command='?'))
        #print(f"Absolute plunger position is {rtn}.")
        return rtn

    def _update_plunger_absolute_position(self, plunger_absolute_position: int):
        self._plunger_absolute_position = plunger_absolute_position

    def report_plunger_relative_position(self) -> int:
        rtn = int(self._query_pump(command='?4'))
        #print(f"Relative plunger position is {rtn}.")
        return rtn

    def _update_plunger_relative_position(self, plunger_relative_position: int):
        self._plunger_relative_position = plunger_relative_position

    def report_valve_number(self) -> int:
        rtn = int(self._query_pump(command='?6'))
        #print(f"Valve number is {rtn}.")
        return rtn

    def _update_valve_number(self, valve_number: int):
        self._valve_number = valve_number

    def initialize_pump(self, init_valve: int = None, out_valve: int = None):
        """
        initialize the pump
        first check if re-initialize pump that has been initialized
        then set direction and force of initialization
            cmd_head = Z for clockwise initialization, meaning port 1 to port X increase CW,
                    = Y for counter clockwise initialization
            cmd_force = 0 for >= 1 mL syringe
                                = 1 for 100 uL - 1 mL syringe
                                = 2 for <= 100 uL syringe
        initialize using
            init_valve as input, out_valve as output
        communicate with pump after initialization, if ready proceed
            max try 30 times, 1 sec per trial
        set initialization status to True
        Returns
        -------

        """
        if self.initialization_status:
            while True:
                verify = input(
                    'The pump has been initialized, are you sure to re-initialize?\n'
                    'Type Y for initialization, '
                    'N for continue without execution.\n')
                if verify == 'Y':
                    print('Pump re-initialization!')
                    break
                elif verify == 'N':
                    print('Pump not re-initialized!')
                    return None
                else:
                    continue
        if self.direction_CW:
            cmd_head = 'Z'
        else:
            cmd_head = 'Y'
        if 1.0e-3 < self.syringe_volume <= 5.0e-3:
            cmd_force = '0'
        elif 1.0e-4 < self.syringe_volume <= 1.0e-3:
            cmd_force = '1'
        elif 0 < self.syringe_volume <= 1.0e-4:
            cmd_force = '2'
        else:
            raise ValueError("Wrong syringe size, check setting file!")
        if init_valve is None:
            init_valve = self.init_valve
        if out_valve is None:
            out_valve = self.out_valve
        self._execute_pump(command=f'{cmd_head}{cmd_force},{init_valve},{out_valve}')
        for ready_count in range(0, 30):
            if self._ensure_ready(wait_time=30):
                self._update_plunger_absolute_position(self.report_plunger_absolute_position())
                self._update_valve_number(self.report_valve_number())
                self.initialization_status = True
                print(f'Pump {self.address} has been initialized')
                return
            else:
                time.sleep(5)
        raise IOError(f'Pump {self.address} initialization failed!')

    def _initialize_plunger(self):
        """
        initialize the plunger only, use with caution!
            cmd_force = 0 for >= 1 mL syringe
                                = 1 for 100 uL - 1 mL syringe
                                = 2 for <= 100 uL syringe
        Returns
        -------

        """
        input('Caution!\nInitialization of the plunger only, press Enter to confirm...')
        cmd_head = 'W'
        if 1.0e-3 < self.syringe_volume <= 5.0e-3:
            cmd_force = '0'
        elif 1.0e-4 < self.syringe_volume <= 1.0e-3:
            cmd_force = '1'
        elif 0 < self.syringe_volume <= 1.0e-4:
            cmd_force = '2'
        else:
            raise ValueError("Wrong syringe size, check setting file!")
        self._execute_pump(command=f'{cmd_head}{cmd_force}')
        self.initialization_status = False
        print("Plunger initialized only, a full initialization is required for operations.")

    def _initialize_valve(self, init_valve: int = None):
        """
        initialize the valve only, use with caution!
        Returns
        -------

        """
        if self.direction_CW:
            direction = '0'
        else:
            direction = '1'
        if init_valve is None:
            init_valve = self.init_valve
        self._execute_pump(command=f'w{init_valve},{direction}')
        self.initialization_status = False
        print("Plunger initialized only, a full initialization is required for operations.")

    def move_valve(self, valve_num: int,
                   direction_CW: bool = None,
                   confirmation: bool = True,
                   ready_before_execute: int = 600):
        """
        wait max ready_before_execute seconds for pump to be ready
        move valve to valve_num
        if direction_CW is provided, use T for clockwise, F for CCW
            else use settings.direction_CW
        Parameters
        ----------
        valve_num
        direction_CW
        confirmation
        ready_before_execute

        Returns
        -------

        """
        assert self.initialization_status, f'Pump {self.address} has not been initialized.'
        if direction_CW is None:
            direction_CW = self.direction_CW
        if ready_before_execute > 0:
            self._ensure_ready(ready_before_execute)
        if direction_CW:
            self._execute_pump(f'I{valve_num}')
        else:
            self._execute_pump(f'O{valve_num}')
        # print(f'Valve moving to {valve_num}...')
        self._ensure_ready(wait_time=3)
        if confirmation:
            if self.report_valve_number() == valve_num:
                self._update_valve_number(valve_num)
                print(f'Pump {self.address} valve moved to {self._valve_number}.')
            else:
                raise IOError(f'Pump {self.address} move valve failed!')
        else:
            self._update_valve_number(self.report_valve_number())

    def move_plunger(self, plunger_pos: int,
                     confirmation: bool = True,
                     ready_before_execute: int = 600,
                     ready_after_execute: bool = True,
                     not_busy: bool = True):
        """
        wait max ready_before_execute seconds for pump to be ready
        move plunger to absolute position
        set post_confirmation to True to confirm plunger has moved to designated position
        USE WITH CARE
            set not_busy to False to not setting pump status to busy during moving
        Parameters
        ----------
        plunger_pos
        confirmation
        not_busy
        ready_before_execute
        ready_after_execute

        Returns
        -------

        """
        assert self.initialization_status, f'Pump {self.address} has not been initialized.'
        assert 0 <= plunger_pos <= self._max_step, "Plunger position out of range."
        if ready_before_execute > 0:
            self._ensure_ready(ready_before_execute)
        if not_busy:
            self._execute_pump(f'A{plunger_pos}')
        else:
            self._execute_pump(f'a{plunger_pos}')
        # print(f'Plunger moving to position {plunger_pos}.')
        if ready_after_execute:
            self._ensure_ready()
        if confirmation:
            if plunger_pos -5 <= self.report_plunger_absolute_position() <= plunger_pos + 5:
                self._update_plunger_absolute_position(plunger_pos)
                print(f'Pump {self.address} plunger moved to {self._plunger_absolute_position}.')
            else:
                raise IOError(f'Pump {self.address} move plunger failed!')
        else:
            self._update_plunger_absolute_position(self.report_plunger_absolute_position())

    @property
    def volume(self) -> float:
        """
        concrete method to report the current volume of the plunger
        Returns
        -------

        """
        plunger_pos = self.report_plunger_absolute_position()
        #volume = 1.0e3 * self.syringe_volume * (plunger_pos - self.home_pos) / self._max_step
        volume = 1.0e3 * self.syringe_volume * plunger_pos / self._max_step
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
        kwargs

        Returns
        -------

        """
        plunger_pos = int((1e-3 * volume / self.syringe_volume) * self._max_step)
        self.move_plunger(plunger_pos = plunger_pos, **kwargs)

    @property
    def port(self) -> int:
        """
        concrete method to report the current valve port number
        Returns
        -------
        current valve port number

        """
        return self.report_valve_number()

    @port.setter
    def port(self, port: int, **kwargs):
        """
        concrete method to set the valve number
        Parameters
        ----------
        port

        Returns
        -------

        """
        self.move_valve(valve_num = port, **kwargs)

    @property
    def top_speed_ml(self) -> float:
        """
        concrete method to report the top speed of plunger
        Returns
        -------

        """
        return self.report_top_speed() * 0.15 * self.syringe_volume

    @top_speed_ml.setter
    def top_speed_ml(self, top_speed: float):
        """
        concrete method to set the top speed
        Parameters
        ----------
        top_speed

        Returns
        -------

        """
        top_speed_int = int(top_speed / (0.15 * self.syringe_volume))
        self.set_top_speed(top_speed=top_speed_int)


# pump = TecanXCPump(com_port="COM6", address=0, syringe_volume=1e-3, num_valve_port=12)
