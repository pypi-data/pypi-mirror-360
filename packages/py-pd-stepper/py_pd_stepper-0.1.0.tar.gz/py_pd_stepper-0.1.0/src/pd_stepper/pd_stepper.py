from .controller import Controller
from .serial_port import SerialPort

class PDStepper:
    __serial_port: SerialPort
    controller: Controller
    def __init__(self, port: str) -> None:
        self.__serial_port = SerialPort(port)
        self.__serial_port.open_serial()
        self.controller = Controller(self.__serial_port)
