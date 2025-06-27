##
# @file dataforming.py
# @version 1
# @author Fumitaka ENDO
# @date 22025-01-28T13:59:12+09:00
# @brief utilities load input data
import numpy as np

def str_to_array(input_str):
    ##
    # @brief convert string to float
    # @param input_str input list written by string
    # @return numpy.array([float, float, ... , float])
    try:
        str_list = str(input_str).split() 
        return np.array([float(value) for value in str_list])
    except ValueError:
        print(f"Skipping invalid input: {input_str}")
        return np.array([])

def load_numbers(file_path):
    ##
    # @brief load number data
    # @param file_path input data path
    # @return numpy.array([int, int, ... , int])
    with open(file_path, 'r') as f:
        numbers = [int(line.strip()) for line in f if line.strip().isdigit()] 
    return numbers

def read_spe_file(file_path):
    ##
    # @brief read spe file (MCA data)
    # @param file_path input file path
    # @return x and y ([int, int, ... , int], [int, int, ... , int])
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
    ##
    # @brief generate frequency distribution from data point lists 
    # @param x data points along X axis
    # @param y data points along Y axis
    # @return  frequency distribution
    frequency_distribution = []
    
    for x_val, freq in zip(x, y):
        frequency_distribution.extend([x_val] * freq)
    
    return frequency_distribution

def find_peaks(data):
    ##
    # @brief find peak and reterun number of peak and index 
    # @param data 
    # @return return peak number and list of index (int, [int, int, ..., int])
    if len(data) < 3:
        return 0, []

    peaks = 0
    peak_indices = []

    for i in range(1, len(data) - 1):
        # ピーク判定: 両隣よりも大きい
        if data[i] > data[i - 1] and data[i] > data[i + 1]:
            peaks += 1
            peak_indices.append(i)

    return peaks, peak_indices