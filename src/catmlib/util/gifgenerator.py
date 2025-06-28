"""!
@file gifgenerator.py
@version 1
@author Fumitaka ENDO
@date 2025-06-28T03:55:00+09:00
@brief gif file generator from pngs
"""
from PIL import Image
import glob
import time
import os 
import os
from datetime import datetime
import argparse 

def generate_gif():
    """!
    @brief generate gif from png files
    
    @details input files and output directory are defined from command line argument
    
    CLI argument:
    @arg input input files pathname
    @arg output output directory
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input files path and name with wild card", type=str, default=None)
    parser.add_argument("output", help="output directory path", type=str, default=None)
    parser.add_argument("-duration", help="duration time to be genareted gif. default is 200", type=int, default=200)

    args = parser.parse_args()
    input_path: str = args.input
    output_path: str = args.output
    duration_time: int = args.duration

    if os.path.isdir(input_path):
        inputpath = input_path
    else:
        print("input directory does not exist")
    
    if os.path.isdir(output_path):
        today_str = datetime.now().strftime("%Y%m%d")
        dir_name = f"{output_path}/{today_str}"
    else:
        print("output directory does not exist")

    current_time = time.time()
    unix_time_str = str(int(current_time))
    
    os.makedirs(dir_name, exist_ok=True)

    basepath   = f"{dir_name}/*.gif"
    outputpath = basepath.replace('*', unix_time_str)

    files = sorted(glob.glob(inputpath), key=os.path.getctime)

    images = list(map(lambda file: Image.open(file), files))
    images[0].save(outputpath, save_all=True, append_images=images[1:], duration=duration_time, loop=0)

    current_directory = os.getcwd()

    full_path = os.path.join(current_directory, outputpath)
    print(full_path)


