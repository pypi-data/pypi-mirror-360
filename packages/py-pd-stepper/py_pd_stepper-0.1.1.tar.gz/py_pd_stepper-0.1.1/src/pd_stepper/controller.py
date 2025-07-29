from .serial_port import SerialPort
from .status import parse_status, Status

class Controller:
    def __init__(self, port: SerialPort):
        self.__serial_port = port
        self.status: Status = None

    def get_status(self):
        status = self.__serial_port.communicate('status')
        self.status = parse_status(status)
        return self.status

    def turn_light_on(self):
        self.__serial_port.communicate('setLight:0')

    def turn_light_off(self):
        self.__serial_port.communicate('setLight:1')

    def set_target_position(self, position: int):
        self.__serial_port.communicate(f'setTarget:{position}')

    def set_acceleration(self, accel: int):
        self.__serial_port.communicate(f'setAcceleration:{accel}')

    def run_motor(self, speed: float):
        """
        run motor permanently on given speed
        """
        self.__serial_port.communicate(f'runMotor:{speed}')

    def stop_motor(self):
        self.__serial_port.communicate('stopMotor')

    def set_voltage(self, voltage: int):
        if voltage not in [5,9,12,15,20]:
            raise ValueError("Voltage must be 5, 9, 12, 15 or 20")
        self.__serial_port.communicate(f'setVoltage:{voltage}')

    def set_speed(self, speed: float):
        self.__serial_port.communicate(f'setSpeed:{speed}')