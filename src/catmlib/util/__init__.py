"""!
@file __init__.py
@version 1
@author Fumitaka ENDO
@date 2025-06-28T18:17:41+09:00
@brief __init__
"""
from .catmviewer import find_nearest_index
from .catmviewer import calculate_track_dipole_magnet_analytical_solution
from .catmviewer import calculate_unit_vector
from .catmviewer import calculate_extrapolated_position
from .catmviewer import plot_3d_trajectory
from .catmviewer import plot_2d_trajectory
from .dataforming import str_to_array
from .dataforming import load_numbers
from .dataforming import read_spe_file
from .dataforming import create_histogram_data_from_points
from .dataforming import find_peaks
from .gifgenerator import generate_gif
from .xcfgreader import classify_indices
from .xcfgreader import get_tree
from .xcfgreader import get_node
from .xcfgreader import get_instance
from .xcfgreader import get_block
from .xcfgreader import print_tree
from .xcfgreader import write_text
from .xcfgreader import read_text
from .xcfgreader import get_matching_indices

__all__ = [
    'find_nearest_index', 'calculate_track_dipole_magnet_analytical_solution', 'calculate_unit_vector', 'calculate_extrapolated_position', 
    'plot_3d_trajectory', 'plot_2d_trajectory', 'str_to_array', 'load_numbers', 'read_spe_file', 'create_histogram_data_from_points', 'find_peaks',
    'generate_gif',
    'classify_indices', 'get_tree', 'get_node', 'get_instance', 'get_block', 'print_tree', 'write_text', 'read_text', 'get_matching_indices'
    ]
