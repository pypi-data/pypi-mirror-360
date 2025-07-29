from dataclasses import dataclass
import re
@dataclass
class Status:
    voltage_set: int               # V
    real_voltage: float            # V
    pg_state: bool                 # True = OK
    target_position: int           # Steps
    current_position: int          # Steps
    speed: float                   # Steps/s
    encoder_value: float           # Raw count (AS5600)
    acceleration: float

def parse_status(serial_line: str) ->Status:
    pattern = (
        r"volltageSet: (\d+)V, "
        r"realVolltage: ([\d.]+)V, "
        r"PGState: (\d), "
        r"targetPosition: (-?\d+), "
        r"currentPosition: (-?\d+), "
        r"Speed: ([\d.]+)Steps/s, "
        r"EncoderValue: (-?[\d.]+), "
        r"Acceleration: ([\d.]+),"
    )

    match = re.match(pattern, serial_line.strip())
    if not match:
        raise ValueError(f"Could not parse motor status: {serial_line}")
    return Status(
        voltage_set=int(match.group(1)),
        real_voltage=float(match.group(2)),
        pg_state=bool(int(match.group(3))),
        target_position=int(match.group(4)),
        current_position=int(match.group(5)),
        speed=float(match.group(6)),
        encoder_value=float(match.group(7)),
        acceleration=float(match.group(8)),
    )