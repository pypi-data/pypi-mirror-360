from struct import pack
from matterlab_serial_device import SerialDevice, open_close
from matterlab_pumps.base_pump import ContinuousSyringePump


class ContinuousDualSyringe(ContinuousSyringePump, SerialDevice):
    category="Pump"
    ui_fields  = ("com_port")
    def __init__(self, com_port):
        SerialDevice.__init__(self,
                              com_port=com_port
                              )
        ContinuousSyringePump.__init__(self)
        self._speed = 0

    @property
    def speed(self)->int:
        return self._speed

    @speed.setter
    def speed(self, speed: int):
        self.write(pack(">H", speed))
        