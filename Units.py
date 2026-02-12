from enum import Enum

class Type(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    SPECIFIC_VOLUME = "specific_volume"
    DENSITY = "density"
    SPECIFIC_ENERGY = "sprecific_energy"
    SPECIFIC_ENTROPY = "entropy"

class Unit():
    def __init__(self, symbol: str, conversion: float, type: Type, native_shift = 0.0, si_shift = 0.0):
        """
        Creates a new Unit object
        
        :param symbol: String to display as the unit's symbol
        :type symbol: str
        :param conversion: Conversion factor, as SI units/self units
        :type conversion: float
        :param type: Type of unit (e.g. temperature, pressure, etc.)
        :type type: Type
        :param native_shift: Additive shift applied before conversion factor
        :type native_shift: float
        :param si_shift: Additive shift applied after conversion factor
        :type si_shift: float
        """
        self.symbol = symbol
        self.conversion = conversion
        self.type = type
        self.native_shift = native_shift
        self.si_shift = si_shift
    
    def __repr__(self):
        return self.symbol
    
    def __eq__(self, value):
        return (
            (self.si_shift == value.si_shift) and
            (self.conversion == value.conversion) and
            (self.native_shift == value.native_shift) and
            (self.type == value.type))

def convert(value: float, unit_from: Unit, unit_to: Unit) -> float:
    """
    Returns ``value`` converted to ``unit_to`` from ``unit_from``. 
    
    :param value: Value to convert
    :type value: float
    :param unit_from: Unit to convert from (the unit of ``value``)
    :type unit_from: Unit
    :param unit_to: Unit to convert to
    :type unit_to: Unit
    :return: ``value``, in terms of ``unit_to``
    :rtype: float
    """
    if unit_from == unit_to:
        return value
    if unit_from.type != unit_to.type:
        raise ValueError("Cannot convert between units of mismatched type!")
    si_value = ((value + unit_from.native_shift) * unit_from.conversion) + unit_from.si_shift
    return ((si_value - unit_to.si_shift) / unit_to.conversion) - unit_to.native_shift