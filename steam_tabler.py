from csv import DictReader
import os
from enum import Enum
import re
from math import inf

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

def search_interpolate(search_by: Property, search_by_value: float, search_for: Property, table: list[dict]):
    low_x = -inf
    high_x = inf
    low_result = None
    high_result = None
    for x in table:
        current_x = x[search_by.value]
        if current_x == search_by_value:
            return current_x, current_x, x[search_for.value]
        elif current_x > low_x and current_x < search_by_value:
            low_x = current_x
            low_result = x[search_for.value]
        elif current_x < high_x and current_x > search_by_value:
            high_x = current_x
            high_result = x[search_for.value]
    if low_result == None or high_result == None:
        return None, None, None
    return low_x, high_x, lin_interpolate(search_by_value, low_x, high_x, low_result, high_result)

def find_value_1var(search_by: Property, search_by_value: float, search_for: Property, P_table: list[dict], T_table: list[dict]):
    match search_by:
        case Property.TEMP:
            return search_interpolate(search_by, search_by_value, search_for, T_table)
        case Property.PRESSURE:
            return search_interpolate(search_by, search_by_value, search_for, P_table)
        case _:
            raise ValueError(f"Searching by {search_by.value} not supported!")

def find_value_T_P(T: float, P: float, search_for: Property, T_P_table: list[dict]):
    # Check if both T and P match exactly
    for x in T_P_table:
        if x[Property.TEMP.value] == T and x[Property.PRESSURE.value] == P:
            return T, T, P, P, x[search_for.value]
        
    # Check if T matches exactly but P doesn't
    matches_T = [x for x in T_P_table if x[Property.TEMP.value] == T]
    if matches_T:
        result = search_interpolate(Property.PRESSURE, P, search_for, matches_T)
        if result[2]:
            return (T, T) + result
        else:
            return None, None, None, None, None
    
    # Check if P matches exactly but T doesn't
    matches_P = [x for x in T_P_table if x[Property.PRESSURE.value] == P]
    if matches_P:
        result = search_interpolate(Property.TEMP, T, search_for, matches_P)
        if result[2]:
            return result[:2] + (P, P) + result[2:]
        else:
            return None, None, None, None, None
    
    # At this point we have a guarantee that neither temperature nor pressure exactly matches the table
    # Get unique pressure and temperature values
    unique_temps = sorted(list(set([x[Property.TEMP.value] for x in T_P_table])))
    
    last_temp = unique_temps[0]
    low_temp = None
    high_temp = None
    for temp in unique_temps:
        if temp > T and last_temp < T:
            low_temp = last_temp
            high_temp = temp
        last_temp = temp
    if not low_temp:
        return None, None, None, None, None
    low_temp_entries = [x for x in T_P_table if x[Property.TEMP.value] == low_temp]
    high_temp_entries = [x for x in T_P_table if x[Property.TEMP.value] == high_temp]
    # now scan for pressure on either side from both lists
    
    


sat_by_T = read_csv(sat_by_T_file)
sat_by_P = read_csv(sat_by_P_file)
comp_sup = read_csv(comp_sup_file)

#print(find_value_1var(Property.PRESSURE, 214, Property.ENTHALPY_VAPOR, sat_by_P, sat_by_T))
print(find_value_T_P(23, 0.01, Property.ENTHALPY, comp_sup))