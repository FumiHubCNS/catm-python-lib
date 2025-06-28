"""!
@file xcfgreader.py
@version 1
@author Fumitaka ENDO
@date 2025-06-28T04:42:00+09:00
@brief reading utillities for configuration file of GET electronics
"""
import xml.etree.ElementTree as ET
import pandas as pd
import sys
import numpy as np
import os
from collections import defaultdict

def classify_indices(values):
    """!
    @brief Classify indices by values in a list.
    
    This function groups the indices of elements in the input list by their values.
    
    @param values A list of values to be classified.
    @return A dictionary where each key is a unique value and the value is a list of indices where it occurs.
    """
    index_dict = defaultdict(list)
    for idx, val in enumerate(values):
        index_dict[val].append(idx)
    return dict(index_dict)

def get_tree(input_path):
    """!
    @brief Parse an XML configuration file and return its root element.
    
    @param input_path Path to the XML configuration file.
    @return Root element of the parsed XML tree.
    """
    tree = ET.parse(input_path)
    root = tree.getroot()
    return root

def get_node(root, node_id_name='CoBo'):
    """!
    @brief Retrieve a specific <Node> element by its ID from the XML tree.
    
    @param root Root element of the XML tree.
    @param node_id_name ID attribute value of the desired Node element (default is 'CoBo').
    @return The Node element if found; otherwise, None.
    """
    root = get_tree()
    cobo_node = root.find(f".//Node[@id='{node_id_name}']")
    return cobo_node

def get_instance(node, instance_id_name='*'):
    """!
    @brief Retrieve a specific <Instance> element by its ID within a given <Node>.
    
    @param node The parent Node element.
    @param instance_id_name ID attribute value of the desired Instance element (default is '*').
    @return The Instance element if found; otherwise, None.
    """
    instance = node.find(f".//Instance[@id='{instance_id_name}']")
    return instance

def get_block(instance, label_name='AsAd', block_name='0' ):
    """!
    @brief Retrieve a specific block element (e.g., AsAd or Aget) by tag and ID within an Instance.
    
    @param instance The parent Instance element.
    @param label_name The tag name of the block to find (e.g., 'AsAd', 'Aget').
    @param block_name ID attribute of the block element to retrieve (default is '0').
    @return The block element if found; otherwise, None.
    """
    block_data = instance.find(f".//{label_name}[@id='{block_name}']")
    return block_data

def print_tree(element, indent=0, indent_label=1):
    """!
    @brief Recursively print elements at a specified depth level in an XML tree.
    
    @param element The current element to print.
    @param indent Current recursion depth (used internally).
    @param indent_label Target depth level at which to print elements.
    """
    if indent == indent_label:
        print("  " * indent + f"{element.tag}: {element.attrib}")
    
    for child in element:
        print_tree(child, indent + 1, indent_label)

def write_text(input_path, output_path):
    root = get_tree(input_path)
    cobo_node = get_node(root)

    cobos_list = ['*','0','1','2','3']
    asads_list = ['*','0','1','2','3']
    agets_list = ['*','0','1','2','3']

    threshold_map = []

    for i in range(len(cobos_list)):
        instance = get_instance(cobo_node, cobos_list[i])
        if instance is not None:

            cobo_id_block = instance.find(f"./Module/coboId")
            cobo_id = cobo_id_block.text if cobo_id_block is not None else -1

            for j in range(len(asads_list)):
                asad = get_block(instance,'AsAd', asads_list[j])
                if asad is not None:

                    for k in range(len(agets_list)):
                        aget = get_block(asad,'Aget', agets_list[k])
                        if aget is not None:

                            global_threshold_block = aget.find(f"./Global/Reg1/GlobalThresholdValue")
                            global_threshold = global_threshold_block.text if (global_threshold_block is not None) else -1

                            channels = aget.findall('channel')

                            for l in range(len(channels)):
                                lsb_threshold_block = channels[l].find(f"./LSBThresholdValue")
                                lsb_threshold = lsb_threshold_block.text if lsb_threshold_block is not None else -1

                                threshold_map.append( 
                                    [
                                        cobos_list[i],
                                        asads_list[j], 
                                        agets_list[k],
                                        channels[l].attrib.get("id"),
                                        cobo_id,
                                        global_threshold,
                                        lsb_threshold
                                    ] 
                                )
                            
    pd_label_name = ['cobo', 'asad', 'aget', 'channel','coboId','global_threshold','LSB_threshold']

    data = pd.DataFrame(threshold_map, columns=pd_label_name)     
    data.to_csv(output_path, index=False, sep='\t')
 
def read_text(intput_path=None):
    """!
    @brief Reads a tab-separated text file into a pandas DataFrame.
    
    @param intput_path The path to the text file. If None, the function returns None.
    @return A pandas DataFrame containing the loaded data, or None if no path is given.
    """
    if intput_path is not None:
        data = pd.read_csv(intput_path,sep='\t')
        return data
    
def get_matching_indices(data, cobo_value, asad_value, aget_value, channel_value):
    """!
    @brief Get indices of rows in a DataFrame that match specified values.
    
    Each parameter can be set to a specific value (non-negative) to filter, or a negative value to ignore the filter.
    
    @param data A pandas DataFrame that contains columns: `cobos`, `asads`, `agets`, `channels`.
    @param cobo_value Integer. Cobo value to match (set < 0 to ignore).
    @param asad_value Integer. Asad value to match (set < 0 to ignore).
    @param aget_value Integer. Aget value to match (set < 0 to ignore).
    @param channel_value Integer. Channel value to match (set < 0 to ignore).
    @return A list of indices in the DataFrame where all specified values match.
    """
    matching_indices = []
    
    for i in range(len(data.ids)):
        if cobo_value >= 0:
            cobo_flag = data.cobos[i] == cobo_value
        else:
            cobo_flag = True

        if asad_value >= 0:
            asad_flag = data.asads[i] == asad_value
        else:
            asad_flag = True

        if aget_value >= 0:
            aget_flag = data.agets[i] == aget_value
        else:
            aget_flag = True

        if channel_value >= 0:
            chan_flag = data.channels[i] == channel_value
        else:
            chan_flag = True
        
        if chan_flag * aget_flag * asad_flag * cobo_flag == True:
            matching_indices.append(i)        

    return matching_indices
