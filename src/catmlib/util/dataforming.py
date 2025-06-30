"""!
@file dataforming.py
@version 1.2
@author Fumitaka ENDO
@date 2025-06-30T11:18:37+09:00
@brief utilities load input data
"""
import numpy as np
import tomllib
import os
import argparse 
import pprint  
import pathlib

this_file_path = pathlib.Path(__file__).parent

def read_config(path):
    with open(path, 'rb') as f:
        config = tomllib.load(f)
    return config

def str_to_array(input_str):
    """!
    @brief convert string to float
    @param input_str input list written by string
    @return numpy.array([float, float, ... , float])
    """
    try:
        str_list = str(input_str).split() 
        return np.array([float(value) for value in str_list])
    except ValueError:
        print(f"Skipping invalid input: {input_str}")
        return np.array([])

def load_numbers(file_path):
    """!
    @brief load number data
    @param file_path input data path
    @return numpy.array([int, int, ... , int])
    """
    with open(file_path, 'r') as f:
        numbers = [int(line.strip()) for line in f if line.strip().isdigit()] 
    return numbers

def read_toml_file(file_path=None):
    """!
    @brief read toml file and return result
    @param file_path input file path 
    @return return tomllib.load(f)
    """
    if os.path.isfile(file_path):
        try:
            with open(file_path, "rb") as f:
                config = tomllib.load(f)
            return config
        except (tomllib.TOMLDecodeError, OSError) as e:
            print(f"An error occurred while loading: {e}")
            return None
    else:
        print(f"File does not exist: {file_path}")
        return None

def read_spe_file(file_path):
    """!
    @brief read spe file (MCA data)
    @param file_path input file path
    @return x and y ([int, int, ... , int], [int, int, ... , int])
    """
    x = []
    y = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    data_section = False
    for i, line in enumerate(lines):
        if line.strip() == "$DATA:":
            data_section = True
            channel_count = int(lines[i + 1].split()[1])
            start_idx = i + 2  
            break
    
    if data_section:
        for i in range(start_idx, start_idx + channel_count):
            if lines[i].strip() == "$ENER_FIT:":
                break
            y.append(int(lines[i].strip()))
            x.append(len(x))

    return x, y

def create_histogram_data_from_points(x, y):
    """!
    @brief generate frequency distribution from data point lists 
    @param x data points along X axis
    @param y data points along Y axis
    @return  frequency distribution
    """
    frequency_distribution = []
    
    for x_val, freq in zip(x, y):
        frequency_distribution.extend([x_val] * freq)
    
    return frequency_distribution

def find_peaks(data):
    """!
    @brief find peak and reterun number of peak and index 
    @param data 
    @return return peak number and list of index (int, [int, int, ..., int])
    """
    if len(data) < 3:
        return 0, []

    peaks = 0
    peak_indices = []

    for i in range(1, len(data) - 1):
        if data[i] > data[i - 1] and data[i] > data[i + 1]:
            peaks += 1
            peak_indices.append(i)

    return peaks, peak_indices


def check_raed_file_function():
    """!
    @brief check file raeder

    CLI argument:
    @arg type select file type
    @arg path input file path
    @arg path input file path
    @arg spe-draw dump flag for plot histogram in terminal
    @arg draw-height maximum height of drawn histogram
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help="select file type", type=str)
    parser.add_argument("path", help="path input file path", type=str)
    parser.add_argument("-sd","--spe-draw", help="dump flag for plot histogram in terminal", action="store_true")
    parser.add_argument("-dh","--draw-height", help="maximum height of drawn histogram", type=int, default=10)
    
    args = parser.parse_args()
    file_type: str = args.type
    file_path: str = args.path
    spe_draw_flag: bool =  args.spe_draw
    draw_height: int = args.draw_height

    if file_type == "spe":
        data_x, data_y = read_spe_file(file_path)
        bin_width = data_x[1] - data_x[0]
        data_length = len(data_x)
        max_value = max(data_y)
        max_index = data_y.index(max_value)
        print(f"x range : [{data_x[0]} : {data_x[-1]} ], bin number : {data_length}, bin width :{bin_width}")
        print(f"maximum value : {max_value}, index : {max_index}")

        if spe_draw_flag:
            import shutil
            import math

            def spe_rebin(data, bins):
                n = len(data)
                if bins >= n:
                    return data + [0] * (bins - n) 
                bin_size = n / bins
                rebinned = []
                for i in range(bins):
                    start = int(i * bin_size)
                    end = int((i + 1) * bin_size)
                    if end <= start:
                        end = start + 1
                    chunk = data[start:end]
                    avg = sum(chunk) / len(chunk)
                    rebinned.append(avg)
                return rebinned

            def spe_normalize(data, height=10):
                max_val = max(data)
                if max_val == 0:
                    return [0] * len(data)
                return [round((v / max_val) * height) for v in data]

            def spe_draw_histogram(data, height=10):
                for level in range(height, 0, -1):
                    line = ''
                    for v in data:
                        line += '.' if v >= level else ' '
                    print(line)
            
            term_width = shutil.get_terminal_size().columns
            max_bins = term_width  

            rebinned = spe_rebin(data_y, max_bins)
            normalized = spe_normalize(rebinned, height=draw_height)
            spe_draw_histogram(normalized, height=draw_height)

    elif file_type == "toml":
        toml_output = read_toml_file(file_path)
        print("=== TOML Config Dump ===")
        pprint.pprint(toml_output, sort_dicts=False)
