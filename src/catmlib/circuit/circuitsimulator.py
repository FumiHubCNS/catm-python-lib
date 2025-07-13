"""!
@file circuitsimulator.py
@version 1
@author Fumitaka ENDO
@date 2025-07-12T12:03:51+09:00
@brief circuit smulation utilities uing PySpice
"""
import argparse
import pathlib
import PySpice
import catmlib.circuit.basecircuit as bc
import PySpice.Logging.Logging as Logging
from PySpice.Probe.Plot import plot
from PySpice.Spice.Netlist import Circuit
import PySpice.Unit as U
from typing import Any

this_file_path = pathlib.Path(__file__).parent

def get_resistance_unit(prefix: str) -> Any:
    """!
    @brief method for converting unit between TBaseCircuitComponent and PySpice
    """
    units = {
        '': U.u_Ω,
        'k': U.u_kΩ,
        'M': U.u_MΩ,
        'm': U.u_mΩ,
    }
    try:
        return units[prefix]
    except KeyError:
        raise ValueError(f"Unsupported unit prefix: {prefix}")

def build_pyspice_circuit(circuit_array: bc.TCircuitComponentsArray, gnd_label:str="", circuit_title:str="Generated Circuit") -> Circuit:
    """!
    @brief make circuit with PySpice from TCircuitComponentsArray

    @param circuit_array input object (TCircuitComponentsArray)
    @param gnd_label junction label for making GND with PySpice
    @param circuit_title circuit object title

    @return circuit object (Circuit)
    """
    circuit = Circuit(circuit_title)

    comps = circuit_array.get_component_list()
    comp_lookup = {i: c for i, c in enumerate(comps)}
    added = set()
    circiut_list = []

    for i, conn in enumerate(circuit_array.connection_list):
        idx1, idx2 = conn['list']
        c1 = comp_lookup[idx1]
        c2 = comp_lookup[idx2]

        name1 = c1.component['name']
        name2 = c2.component['name']

        node1_pre  = c1.pre_junction['name']
        node1_post = c1.pos_junction['name'] if gnd_label != c1.pos_junction['name'] else circuit.gnd
        node2_pre  = c2.pre_junction['name']
        node2_post = c2.pos_junction['name'] if gnd_label != c2.pos_junction['name'] else circuit.gnd

        unit1 = get_resistance_unit(c1.component['unit'][0])
        unit2 = get_resistance_unit(c2.component['unit'][0])

        if conn['type'] == 'series':
            if idx1 not in added:
                circuit.R(name1, node1_pre, node1_post, c1.component['value'] @ unit1)
                added.add(idx1)
                circiut_list.append({ 'index' : idx1, 'pre' : node1_pre, 'post' : node1_post})
            if idx2 not in added:
                circuit.R(name2, node1_post, node2_post, c2.component['value'] @ unit2)
                added.add(idx2)
                circiut_list.append({ 'index' : idx2, 'pre' : node1_post, 'post' : node2_post})

        elif conn['type'] == 'parallel':
            base_node1 = node1_pre if gnd_label != node1_pre else circuit.gnd
            base_node2 = node1_post if gnd_label != node1_post else circuit.gnd

            if idx1 not in added:
                circuit.R(name1, base_node1, base_node2, c1.component['value'] @ unit1)
                added.add(idx1)
                circiut_list.append({ 'index' : idx1, 'pre' : base_node1, 'post' : base_node2})
            if idx2 not in added:
                if idx1 in added:
                    result = next((d for d in circiut_list if d['index'] == idx1), None)
                    base_node1 = result['pre'] if gnd_label != result['pre'] else circuit.gnd
                    base_node2 = result['post']  if gnd_label != result['post'] else circuit.gnd
                circuit.R(name2, base_node1, base_node2, c2.component['value'] @ unit2)
                added.add(idx2)
                circiut_list.append({ 'index' : idx2, 'pre' : base_node1, 'post' : base_node2})

    return circuit

def execute_simulator(circuit: Circuit):
    """!
    @brief execute circuit simulator with circuit 

    @param input circuit (Circuit object from PySpice)
    @return simulator output (simulator, analysis)
    """
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    return simulator, analysis

def get_node_voltage(analysis, dump_flag=True) -> dict:
    """!
    @brief get node voltage information

    @param analysis output object from method of execute simulator  
    @param dump_flag flag for duming debug information to terminal
    @return node voltage dictionary
    """
    output = {}
    for node_name in analysis.nodes.keys():
        v = float(analysis[node_name][0])
        output[node_name] = v

        if dump_flag:
            print(f'Voltage at {node_name}: {v:.2f} V')

    return output

def get_source_current(analysis, dump_flag=True) -> dict:
    """!
    @brief get source current information

    @param analysis output object from method of execute simulator  
    @param dump_flag flag for duming debug information to terminal
    @return source current dictionary
    """
    output = {}
    for branch in analysis.branches.keys():
        i = float(analysis.branches[branch][0])
        output[branch] = i

        if dump_flag:
            print(f'Current through {branch}: {i*1e3:.3f} mA')
            
    return output

def main():
    parser = argparse.ArgumentParser()
 
    parser.add_argument("-v", "--values", nargs="+", type=int, help="list of items", default=[-10])
    parser.add_argument("-l", "--labels", nargs="+", type=str, help="list of items", default=["JR0-1"])

    args = parser.parse_args()

    voltages = args.values
    junctions = args.labels

    logger = Logging.setup_logging()
    
    circuit_array = bc.TCircuitComponentsArray()

    circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R0", ctype="resitor", cvalue=3.5, cunit="M"))
    circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R1", ctype="resitor", cvalue=3.5, cunit="M"))
    circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R2", ctype="resitor", cvalue=1, cunit="M"))
    circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R3", ctype="resitor", cvalue=1, cunit="M"))

    comps = circuit_array.get_component_list()

    circuit_array.connect_components_with_parallel(comps[0],comps[1])
    circuit_array.connect_components_with_series(comps[0],comps[2])
    circuit_array.connect_components_with_series(comps[2],comps[3])
    
    circuit = build_pyspice_circuit(circuit_array, gnd_label='JR3-2')

    for i in range(len(voltages)):
        circuit.V(i, junctions[i], circuit.gnd, voltages[i]@U.u_V)       
    
    print(circuit)

    simulator, analysis = execute_simulator(circuit)

    print("Available nodes:", list(analysis.nodes.keys()))

    vlist = get_node_voltage(analysis,True)
    ilist = get_source_current(analysis,True)

if __name__ == "__main__":
    main()
