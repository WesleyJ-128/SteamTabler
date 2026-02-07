from csv import DictReader
import os

# this doesn't work if the working directory has been changed
# so it's at the beginning just in case
dir_path = os.path.dirname(os.path.realpath(__file__))

def read_csv(filepath):
    title_block_num_lines = 6
    # load CSV data into lists of dictionaries
    with open(filepath, "r", encoding="utf-8-sig") as f:
        # throw away non-data lines
        for i in range(title_block_num_lines):
            next(f)
        return list(DictReader(f))
    
def lin_interpolate(x, x_min, x_max, y_min, y_max):
    if x_min == x_max:
        raise ArithmeticError("Divide by Zero when interpolating!")
    return y_min + ((x - x_min) * (y_max - y_min)) / (x_max - x_min)

def double_interpolate(x, y, x_min, x_max, y_min, y_max, z_x_y, z_X_y, z_x_Y, z_X_Y):
    low_y_point = lin_interpolate(x, x_min, x_max, z_x_y, z_X_y)
    high_y_point = lin_interpolate(x, x_min, x_max, z_x_Y, z_X_Y)
    return lin_interpolate(y, y_min, y_max, low_y_point, high_y_point)

sat_by_P_file = os.path.join(dir_path, "saturated_by_pressure_V1.4.csv")
sat_by_T_file = os.path.join(dir_path, "saturated_by_temperature_V1.5.csv")
comp_sup_file = os.path.join(dir_path, "compressed_liquid_and_superheated_steam_V1.3.csv")

sat_by_T = read_csv(sat_by_T_file)
sat_by_P = read_csv(sat_by_P_file)
comp_sup = read_csv(comp_sup_file)