from csv import DictReader
import os
from enum import Enum
import re

# this doesn't work if the working directory has been changed
# so it's at the beginning just in case
dir_path = os.path.dirname(os.path.realpath(__file__))

sat_by_P_file = os.path.join(dir_path, "saturated_by_pressure_V1.4.csv")
sat_by_T_file = os.path.join(dir_path, "saturated_by_temperature_V1.5.csv")
comp_sup_file = os.path.join(dir_path, "compressed_liquid_and_superheated_steam_V1.3.csv")
class Property(Enum):
    TEMP = 'T (°C)'
    PRESSURE = 'P (MPa)'

    VOLUME_LIQUID = 'Specific Volume Liquid (m^3/kg)'
    VOLUME_VAPOR = 'Specific Volume Vapor (m^3/kg)'
    VOLUME = 'Specific Volume (m^3/kg)'
    DENSITY = 'Density (kg/m^3)'

    ENERGY_LIQUID = 'Internal Energy Liquid (kJ/kg)'
    ENERGY_VAPOR = 'Internal Energy Vapor (kJ/kg)'
    ENERGY_VAPORIZATION = 'Internal Energy of Vaporization (kJ/kg)'
    ENERGY = 'Specific Internal Energy (kJ/kg)'

    ENTHALPY_LIQUID = 'Enthalpy Liquid (kJ/kg)'
    ENTHALPY_VAPOR = 'Enthalpy Vapor (kJ/kg)'
    ENTHALPY_VAPORIZATION = 'Enthalpy of Vaporization (kJ/kg)'
    ENTHALPY = 'Specific Enthalpy (kJ/kg)'

    ENTROPY_LIQUID = 'Entropy Liquid [kJ/(kg K)]'
    ENTROPY_VAPOR = 'Entropy Vapor [kJ/(kg K)]'
    ENTROPY_VAPORIZATION = 'Entropy of Vaporization [kJ/(kg K)]'
    ENTROPY = 'Specific Entropy [kJ/(kg K)]'

    PHASE = 'Phase'

class Phase(Enum):
    VAPOR = 'vapor'
    SATURATED_VAPOR = 'saturated vapor'
    LIQUID = 'liquid'
    SATURATED_LIQUID = 'saturated liquid'
    SUPERCRITICAL_FLUID = 'supercritical fluid'

def read_csv(filepath):
    title_block_num_lines = 6
    # load CSV data into lists of dictionaries
    with open(filepath, "r", encoding="utf-8-sig") as f:
        # throw away non-data lines
        for i in range(title_block_num_lines):
            next(f)
        dict_list = list(DictReader(f))
        for x in dict_list:
            for key in x.keys():
                try:
                    x[key] = float(x[key])
                except ValueError:
                    continue
        return dict_list
    
def lin_interpolate(x, x_min, x_max, y_min, y_max):
    if x_min == x_max:
        raise ArithmeticError("Divide by Zero when interpolating!")
    return y_min + ((x - x_min) * (y_max - y_min)) / (x_max - x_min)

def double_interpolate(x, y, x_min, x_max, y_min, y_max, z_x_y, z_X_y, z_x_Y, z_X_Y):
    low_y_point = lin_interpolate(x, x_min, x_max, z_x_y, z_X_y)
    high_y_point = lin_interpolate(x, x_min, x_max, z_x_Y, z_X_Y)
    return lin_interpolate(y, y_min, y_max, low_y_point, high_y_point)

def find_value(search_by: Property, search_by_value: float, search_for: Property):
    return None

sat_by_T = read_csv(sat_by_T_file)
sat_by_P = read_csv(sat_by_P_file)
comp_sup = read_csv(comp_sup_file)

