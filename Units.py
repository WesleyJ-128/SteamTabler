from enum import Enum

class Type(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    SPECIFIC_VOLUME = "specific_volume"
    DENSITY = "density"
    SPECIFIC_ENERGY = "sprecific_energy"
    ENTROPY = "entropy"

class Unit():
    def __init__(self):
        pass