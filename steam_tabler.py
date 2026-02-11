from csv import DictReader
import os
from enum import Enum
from math import inf
import tkinter as tk
from tkinter import ttk
import Units

# this doesn't work if the working directory has been changed
# so it's at the beginning just in case
dir_path = os.path.dirname(os.path.realpath(__file__))

sat_by_P_file = os.path.join(dir_path, "saturated_by_pressure_V1.4.csv")
sat_by_T_file = os.path.join(dir_path, "saturated_by_temperature_V1.5.csv")
comp_sup_file = os.path.join(dir_path, "compressed_liquid_and_superheated_steam_V1.3.csv")

class PropType(Enum):
    SAT = "sat"
    P_T = "p_t"
    SEARCH = "search"
class Property(Enum):
    TEMP = 'T (°C)', Units.Type.TEMPERATURE, "Temperature", PropType.SEARCH
    PRESSURE = 'P (MPa)', Units.Type.PRESSURE, "Pressure", PropType.SEARCH

    VOLUME_LIQUID = 'Specific Volume Liquid (m^3/kg)', Units.Type.SPECIFIC_VOLUME, "Specific Volume (liquid)", PropType.SAT
    VOLUME_VAPOR = 'Specific Volume Vapor (m^3/kg)', Units.Type.SPECIFIC_VOLUME, "Specific Volume (vapor)", PropType.SAT
    VOLUME = 'Specific Volume (m^3/kg)', Units.Type.SPECIFIC_VOLUME, "Specific Volume", PropType.P_T
    DENSITY = 'Density (kg/m^3)', Units.Type.DENSITY, "Density", PropType.P_T

    ENERGY_LIQUID = 'Internal Energy Liquid (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Internal Energy (liquid)", PropType.SAT
    ENERGY_VAPOR = 'Internal Energy Vapor (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Internal Energy (vapor)", PropType.SAT
    ENERGY_VAPORIZATION = 'Internal Energy of Vaporization (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Internal Energy of Vaporization", PropType.SAT
    ENERGY = 'Specific Internal Energy (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Internal Energy", PropType.P_T

    ENTHALPY_LIQUID = 'Enthalpy Liquid (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Enthalpy (liquid)", PropType.SAT
    ENTHALPY_VAPOR = 'Enthalpy Vapor (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Enthalpy (vapor)", PropType.SAT
    ENTHALPY_VAPORIZATION = 'Enthalpy of Vaporization (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Enthalpy of Vaporization", PropType.SAT
    ENTHALPY = 'Specific Enthalpy (kJ/kg)', Units.Type.SPECIFIC_ENERGY, "Enthalpy", PropType.P_T

    ENTROPY_LIQUID = 'Entropy Liquid [kJ/(kg K)]', Units.Type.ENTROPY, "Entropy (liquid)", PropType.SAT
    ENTROPY_VAPOR = 'Entropy Vapor [kJ/(kg K)]', Units.Type.ENTROPY, "Entropy (vapor)", PropType.SAT
    ENTROPY_VAPORIZATION = 'Entropy of Vaporization [kJ/(kg K)]', Units.Type.ENTROPY, "Entropy of Vaporization", PropType.SAT
    ENTROPY = 'Specific Entropy [kJ/(kg K)]', Units.Type.ENTROPY, "Entropy", PropType.P_T

    PHASE = 'Phase', None, "Phase", PropType.P_T

    def __new__(cls, table_name, unit_type, disp_name, type):
        obj = object.__new__(cls)
        obj._value_ = table_name
        obj.internal_name = unit_type
        obj.disp_name = disp_name
        obj.type = type
        return obj
class Phase(Enum):
    VAPOR = 'vapor'
    SATURATED_VAPOR = 'saturated vapor'
    LIQUID = 'liquid'
    SATURATED_LIQUID = 'saturated liquid'
    SUPERCRITICAL_FLUID = 'supercritical fluid'
class SearchMode(Enum):
    SAT_BY_T = 0
    SAT_BY_P = 1
    T_AND_P = 2

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
    # special case to deal with phase string values
    if search_for == Property.PHASE:
        if low_result == high_result:
            result = low_result
        else:
            result = f"{low_result} or {high_result}"
    else:
        result = lin_interpolate(search_by_value, low_x, high_x, low_result, high_result)
    return low_x, high_x, result

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
    low_temp_result = search_interpolate(Property.PRESSURE, P, search_for, low_temp_entries)
    high_temp_result = search_interpolate(Property.PRESSURE, P, search_for, high_temp_entries)
    print(high_temp_result)
    if low_temp_result[2] is None or high_temp_result[2] is None:
        return None, None, None, None, None
    # special case to deal with phase string values
    if search_for == Property.PHASE:
        if low_temp_result[2] == high_temp_result[2]:
            result = low_temp_result[2]
        else:
            result = f"{low_temp_result[2]} or {high_temp_result[2]}"
    else:
        result = lin_interpolate(T, low_temp, high_temp, low_temp_result[2], high_temp_result[2])
    return low_temp, high_temp, low_temp_result[0], low_temp_result[1], result
    
sat_by_T = read_csv(sat_by_T_file)
sat_by_P = read_csv(sat_by_P_file)
comp_sup = read_csv(comp_sup_file)


temp_units = ["°C", "K", "°F", "°R"]
pres_units = ["MPa", "kPa", "Pa", "bar", "atm"]

def search_mode_change():
    mode = search_mode.get()
    result_type.set("")
    result_unit_sel.set("")
    result_unit_sel["values"] = []
    match mode:
        case SearchMode.SAT_BY_T.value:
            result_type['values'] = sorted([x.disp_name for x in Property if x.type == PropType.SAT] + [Property.PRESSURE.disp_name])
            temp_label.configure(state=tk.NORMAL)
            temp_entry.configure(state=tk.NORMAL)
            temp_unit_sel.configure(state=tk.NORMAL)
            pres_label.configure(state=tk.DISABLED)
            pres_entry.configure(state=tk.DISABLED)
            pres_unit_sel.configure(state=tk.DISABLED)
        case SearchMode.SAT_BY_P.value:
            result_type['values'] = sorted([x.disp_name for x in Property if x.type == PropType.SAT] + [Property.TEMP.disp_name])
            temp_label.configure(state=tk.DISABLED)
            temp_entry.configure(state=tk.DISABLED)
            temp_unit_sel.configure(state=tk.DISABLED)
            pres_label.configure(state=tk.NORMAL)
            pres_entry.configure(state=tk.NORMAL)
            pres_unit_sel.configure(state=tk.NORMAL)
        case SearchMode.T_AND_P.value:
            result_type['values'] = sorted([x.disp_name for x in Property if x.type == PropType.P_T])
            temp_label.configure(state=tk.NORMAL)
            temp_entry.configure(state=tk.NORMAL)
            temp_unit_sel.configure(state=tk.NORMAL)
            pres_label.configure(state=tk.NORMAL)
            pres_entry.configure(state=tk.NORMAL)
            pres_unit_sel.configure(state=tk.NORMAL)

def update_units(event):
    print("update")

def run_search():
    nulTemp = Units.Unit(1, Units.Type.TEMPERATURE)
    nulPres = Units.Unit(1, Units.Type.PRESSURE)
    mode = search_mode.get()
    match mode:
        case SearchMode.SAT_BY_T.value:
            try:
                temp_raw = float(temp_entry.get())
            except ValueError:
                result_string.set("ERROR: Temperature must be a number.")
                return
            
            unit_raw = temp_unit_sel.get()
            if not unit_raw:
                result_string.set("ERROR: Select a temperature unit.")
                return
            
            result_type_raw = result_type.get()
            if not result_type_raw:
                result_string.set("ERROR: Select a property to look up.")
                return
            table_var = [x for x in Property if x.disp_name == result_type_raw][0]

            result_unit_raw = result_unit_sel.get()
            #if not result_unit_raw:
                #result_string.set("ERROR: Select an output unit.")
                #return

            table_temp = Units.convert(temp_raw, nulTemp, nulTemp) # make real units
            (temp_low, temp_high, output) = search_interpolate(
                Property.TEMP,
                table_temp,
                table_var,
                sat_by_T
            )
            true_out = Units.convert(output, nulTemp, nulTemp)
            disp_temp_low = Units.convert(temp_low, nulTemp, nulTemp)
            disp_temp_high = Units.convert(temp_high, nulTemp, nulTemp)

            if temp_low:
                if temp_low == temp_high:
                    result_string.set(f"{result_type_raw} at {temp_raw} {unit_raw} is {true_out} {result_unit_raw}.")
                else:
                    result_string.set(
                        f"Interpolating between {disp_temp_low} {unit_raw} and {disp_temp_high} {unit_raw}. \
                        \n{result_type_raw} at {temp_raw} {unit_raw} is {true_out} {result_unit_raw}."
                    )
            else:
                result_string.set(f"ERROR: {temp_raw} {unit_raw} outside of table range.")

        case SearchMode.SAT_BY_P.value:
            try:
                pres_raw = float(pres_entry.get())
            except ValueError:
                result_string.set("ERROR: Pressure must be a number.")
                return
            
            unit_raw = pres_unit_sel.get()
            if not unit_raw:
                result_string.set("ERROR: Select a pressure unit.")
                return
            
            result_type_raw = result_type.get()
            if not result_type_raw:
                result_string.set("ERROR: Select a property to look up.")
                return
            table_var = [x for x in Property if x.disp_name == result_type_raw][0]

            result_unit_raw = result_unit_sel.get()
            #if not result_unit_raw:
                #result_string.set("ERROR: Select an output unit.")
                #return

            table_pres = Units.convert(pres_raw, nulPres, nulPres) # make real units
            (pres_low, pres_high, output) = search_interpolate(
                Property.PRESSURE,
                table_pres,
                table_var,
                sat_by_P
            )
            true_out = Units.convert(output, nulPres, nulPres)
            disp_pres_low = Units.convert(pres_low, nulPres, nulPres)
            disp_pres_high = Units.convert(pres_high, nulPres, nulPres)

            if pres_low:
                if pres_low == pres_high:
                    result_string.set(f"{result_type_raw} at {pres_raw} {unit_raw} is {true_out} {result_unit_raw}.")
                else:
                    result_string.set(
                        f"Interpolating between {disp_pres_low} {unit_raw} and {disp_pres_high} {unit_raw}. \
                        \n{result_type_raw} at {pres_raw} {unit_raw} is {true_out} {result_unit_raw}."
                    )
            else:
                result_string.set(f"ERROR: {pres_raw} {unit_raw} outside of table range.")
                
        case SearchMode.T_AND_P.value:
            temp_entry.get()
            temp_unit_sel.get()
            pres_entry.get()
            pres_unit_sel.get()
            result_type.get()
            result_unit_sel.get()

root = tk.Tk()
root.title("SteamTabler")
search_mode = tk.IntVar()
input_temp = tk.DoubleVar()
input_pres = tk.DoubleVar()

tk.Label(root, text="Look up by:").grid(row=0,column=0,sticky='W')
tk.Radiobutton(root, command=search_mode_change, text="Saturation Temperature", variable=search_mode, value=SearchMode.SAT_BY_T.value).grid(row=1,column=0,sticky='W')
tk.Radiobutton(root, command=search_mode_change, text="Saturation Pressure", variable=search_mode, value=SearchMode.SAT_BY_P.value).grid(row=2,column=0,sticky='W')
tk.Radiobutton(root, command=search_mode_change, text="Temperature and Pressure", variable=search_mode, value=SearchMode.T_AND_P.value).grid(row=3,column=0,sticky='W')

temp_label = tk.Label(root, text="Temperature:")
temp_label.grid(row=5,column=0)
temp_entry = tk.Entry(root)
temp_entry.grid(row=5,column=1)
temp_unit_sel = ttk.Combobox(root, values=temp_units, state="readonly")
temp_unit_sel.grid(row=5,column=2)

pres_label = tk.Label(root, text="Pressure:")
pres_label.grid(row=6,column=0)
pres_entry = tk.Entry(root)
pres_entry.grid(row=6,column=1)
pres_unit_sel = ttk.Combobox(root, values=pres_units, state="readonly")
pres_unit_sel.grid(row=6,column=2)

tk.Label(root, text="Property to look up:").grid(row=8,column=0)
result_type = ttk.Combobox(root, state="readonly")
result_type.grid(row=8,column=1,columnspan=2,sticky="EW")
result_type.bind("<<ComboboxSelected>>", update_units)

tk.Label(root, text="Output Units:").grid(row=9,column=0)
result_unit_sel = ttk.Combobox(root, state="readonly")
result_unit_sel.grid(row=9, column= 1)

tk.Button(root, command=run_search, text="Go!").grid(row=10,column=0,columnspan=3,sticky="EW")

result_string = tk.StringVar()
result = tk.Label(root, textvariable=result_string)
result_string.set("No search results yet.")
result.grid(row=11, column=0, columnspan=3)

search_mode_change()
root.mainloop()