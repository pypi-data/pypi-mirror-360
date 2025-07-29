from pd_stepper import PDStepper
from pd_stepper.serial_port import SerialPort

from .controller import ControllerPump

class Pump(PDStepper):
    def __init__(self, port: str):
        super().__init__(port)
        self.__serial_port = self._PDStepper__serial_port
        self.controller:ControllerPump = ControllerPump(self.__serial_port)