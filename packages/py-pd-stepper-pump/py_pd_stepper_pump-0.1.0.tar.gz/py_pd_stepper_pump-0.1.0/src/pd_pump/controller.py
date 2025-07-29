from pd_stepper.controller import Controller
from pd_stepper.serial_port import SerialPort
from .parameters import Parameters

class ControllerPump(Controller):
    def __init__(self, port: SerialPort):
        super().__init__(port)
        self.__serial_port = port
        self.params = Parameters()

    def pump_ml(self, ml):
        curr_pos = self.get_status().current_position
        target = self.params.steps_per_ml_pump * ml + curr_pos
        self.__serial_port.communicate(f'setTarget:{target}')

    def suck_ml(self, ml):
        curr_pos = self.get_status().current_position
        target = self.params.steps_per_ml_suck * ml + curr_pos
        self.__serial_port.communicate(f'setTarget:{target}')
