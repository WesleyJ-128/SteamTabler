from enum import Enum

class Type(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    SPECIFIC_VOLUME = "specific_volume"
    DENSITY = "density"
    SPECIFIC_ENERGY = "sprecific_energy"
    ENTROPY = "entropy"

class Unit():
    def __init__(self, conversion, type, native_shift = 0, si_shift = 0):
        self.conversion = conversion
        self.type = type
        self.native_shift = native_shift
        self.si_shift = si_shift