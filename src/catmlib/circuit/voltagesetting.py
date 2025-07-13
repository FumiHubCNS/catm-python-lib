"""!
@file voltagesetting.py
@version 1
@author Fumitaka ENDO
@date 2025-07-13T10:34:53+09:00
@brief voltage setting calculator for catm (beam TPC and Recoil TPC with devider circuit)
"""
import argparse
import pathlib
import catmlib.circuit.basecircuit as bc
import catmlib.circuit.circuitsimulator as cs
import PySpice
import PySpice.Logging.Logging as Logging
from PySpice.Probe.Plot import plot
from PySpice.Spice.Netlist import Circuit
import PySpice.Unit as U
from typing import Any
from scipy.optimize import minimize

this_file_path = pathlib.Path(__file__).parent

class TBaseVoltageSettingData():
    """!
    @class TBaseVoltageSettingData
    @brief gem-based tpc's voltage setting calculation class 
    """

    def __init__(self, input=None, spaces=None, voltages=None, pressure=0.2):
        """!
        @brief initialze object
        @param input list of PySpice circuit 
        @param spaces space inforamtion between each stages
        @param voltages source voltage setting dictionary list
        @param pressure pressure value for calculating field strength
        """
        self.stages = []
        self.input_voltages = []
        self.analysis_voltages = []
        self.analysis_currents = []
        self.electrode_voltages = []
        self.circuit_voltage_instance = [] 
        self.conditions = {}
        self.pressure = pressure
        self.spaces = spaces

        if input is not None:
            for i in range(len(input)):
                self.add_stage(input[i])

        if voltages is not None:
            self.input_voltages = voltages
            self.set_voltages()

        space_labels = list(self.spaces.keys())

        for i in range(len(space_labels)):
            self.conditions[space_labels[i]] = 0

    def set_condition(self,inputs=[],dump_flag=False):
        """!
        @brief set condition (field and voltage between each stage)

        @param input list of PySpice circuit 
        @param dump_flag flag for duming debug information to terminal
        """
        if len(inputs) != len((self.conditions.keys())):
            print("input list length does not match conditions")
            print(inputs)
            print(self.conditions)
            return None
        
        else:
            labels = list(self.conditions.keys())
            for i in range(len(labels)):
                self.conditions[labels[i]] = inputs[i]
        
        if dump_flag:
            print(self.conditions)
        
        return self.conditions

    def add_stage(self, obj:Circuit):
        """!
        @brief add stage 
        @param obj Circuit
        """
        self.stages.append(obj)
    
    def check_stage_object(self):
        """!
        @brief dump debug information to terminal
        """
        for i in range(len(self.stages)):
            print(self.stages[i])
    
    def set_voltages(self,voltage_list=None):
        """!
        @brief set voltage (set source voltage values for each stage)

        @param voltage_list voltage dictionary list
        """
        if voltage_list is not None:
            self.input_voltages = voltage_list
        
        for i in range(len(self.input_voltages)):
            objs=[]

            for j in range(len(self.input_voltages[i])):

                if ( i == 0 ) and ( j != 0 ):
                    ref_input = vlist[self.input_voltages[i][j]["junction"].lower()]
                    set_input = self.input_voltages[i][j]["value"]@U.u_V
                    
                    if abs(ref_input) > abs(set_input):
                        print(f"\033[31m[warning] set voltage {j} @ stage {i} is lower than minimum voltage\033[0m")

                objs.append( self.stages[i].V(j, self.input_voltages[i][j]["junction"], self.stages[i].gnd, self.input_voltages[i][j]["value"]@U.u_V)  )

                if ( i == 0 ) and ( j == 0 ):
                    simulator, analysis = cs.execute_simulator(self.stages[i])
                    vlist = cs.get_node_voltage(analysis,False)
                    # print(vlist,self.input_voltages[i][j]["junction"].lower())
            
            self.circuit_voltage_instance.append(objs)

    def simulate_all_stage(self):
        """!
        @brief execute simulator to all stages(all circuits)
        """
        for i in range(len(self.stages)):
            simulator, analysis =  cs.execute_simulator(self.stages[i]) 
            self.analysis_voltages.append( cs.get_node_voltage(analysis, False) )
            self.analysis_currents.append( cs.get_source_current(analysis, False) )

    def get_simulated_source_voltage_current(self, dump_flag=False):
        """!
        @brief get simulation result 

        @param dump_flag flag for duming debug information to terminal
        @return voltages, currents (these object are value list)
        """
        voltages = []
        electrode = []
        currents = []

        for i in range(len(self.analysis_voltages)):
            vol = list(self.analysis_voltages[i].values())
            if i == 0:
                voltages.append(vol[2])
                voltages.append(vol[0])

                electrode.append(vol[2])
                electrode.append(vol[1])

            else:
                voltages.append(vol[0])

                electrode.append(vol[0])

        for i in range(len(self.analysis_currents)):
            cur = list(self.analysis_currents[i].values())
            for j in range(len(cur)):
                currents.append(cur[j]*1e6)

        if dump_flag:
            for i in range(len(voltages)):
                print(f"source {i} : V = {voltages[i]:8.2f} [V], I = {currents[i]:7.3f} [uA]" )

        self.electrode_voltages = electrode
        
        return voltages, currents
    
    def calculate_field_strength(self):
        """!
        @brief calculate field strength and voltage value of gems
        @detail 
            this method calculate the electric field strength of field cage, transfer region, ang induction region, 
            this method also calculate voltage value of each gem.
            these values correspond to tpc condition, so this method write self.conditions after calling 
        """
        dx = list(self.spaces.values())
        labels = list(self.spaces.keys())

        for i in range(len(self.electrode_voltages)):

            if i < len(self.electrode_voltages)-1:
                dv = self.electrode_voltages[i] - self.electrode_voltages[i+1]

            else:
                dv = self.electrode_voltages[i] - 0
            
            e = dv / dx[i] / self.pressure / 1e3

            self.conditions[labels[i]] = abs(dv) if "gem" in labels[i] else e


    def get_condition(self, dump_flag=False):
        """!
        @brief get conditions

        @param dump_flag flag for duming debug information to terminal
        """
        if dump_flag:
            labels = list(self.conditions.keys())
            values = list(self.conditions.values())
            for i in range(len(values)):
                unit = 'V' if 'gem' in labels[i] else 'kV/cm/atm'
                title = 'dV' if 'gem' in labels[i] else 'E'
                print(f"{title:<2}_{labels[i]:<10} = {values[i]:8.3f} [{unit}]")

        return self.conditions
    
    def estimate_trial_input_voltage(self):
        """!
        @brief estimate voltages of each stage for trial input to optimize input voltage 

        @return trial input voltages
        """        
        conl = list(self.conditions.keys())
        conv = list(self.conditions.values())
        spal = list(self.spaces.keys())
        spav = list(self.spaces.values())

        n = len(conv)
        
        trial = []

        voltage = 0

        for i in range(n):
            factor = -1 if 'gem' in conl[n-i-1] else 1e3 * spav[n-i-1] * self.pressure
            voltage += conv[n-i-1] * factor

            trial.append(voltage) 
            # print(trial[i])
        
        return trial

    def simulate_first_stage_volages(self,val1,val2):
        """!
        @brief variavles calculation method to be used optimization

        @param val1 voltage of cathode
        @param val2 voltage after protection resistor for gem

        @return cathode and thegem voltage
        """   
        self.circuit_voltage_instance[0][0].dc_value = val1 @ U.u_V
        self.circuit_voltage_instance[0][1].dc_value = val2 @ U.u_V
        simulator, analysis =  cs.execute_simulator(self.stages[0]) 

        output_dict = cs.get_node_voltage(analysis, False) 
        output_list = list(output_dict.values())

        return output_list[2], output_list[1]

    def objective(self, x, target):
        """!
        @brief estimation function to be used minimization

        @param x trial varibles 
        @param target ideal values

        @return sum of chi2 with error
        """   
        ref1, ref2 = self.simulate_first_stage_volages(x[0], x[1])
        tri1, tri2 = target
        return (ref1 - tri1)**2 + (ref2 - tri2)**2
    
    def search_first_stage_voltages(self, debug_flag=True):
        """!
        @brief search voltage values for cirtain condition usinf scipy optimization method

        @param dump_flag flag for duming debug information to terminal
        """
        trial = self.estimate_trial_input_voltage()
        target = (trial[-1], trial[-2])
        x0 = [trial[-1], trial[-2]]
  
        result = minimize(self.objective, x0, args=(target,))
        # print(result)

        x_opt = result.x
        y_opt = self.simulate_first_stage_volages(x_opt[0], x_opt[1])

        if debug_flag:
            print(result)
            print(f"optimized vlues: {x_opt}")
            print(f"electrode voltage using optimized values: {y_opt}")

        return x_opt
        
def minitpc_filedcage_configuration(version:int=1,resitor_value:float=1,circuit_title:str="Filed Cage and THGEM top"):
    """!
    @brief get mini tpc field cage circuit 

    @param version circuit type (1: one tpc configuration, 2: two tpcs configuration)
    @param resitor_value pull-down resistor value
    @param circuit_title title of PySpice circuit object
    
    @return circuit object defined by PySpice
    """
    logger = Logging.setup_logging()
    
    circuit_array = bc.TCircuitComponentsArray()

    if version == 1:
        circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R0", ctype="resitor", cvalue=7, cunit="M"))
        circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R1", ctype="resitor", cvalue=7, cunit="M"))
    elif version == 2:
        circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R0", ctype="resitor", cvalue=3.5, cunit="M"))
        circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R1", ctype="resitor", cvalue=3.5, cunit="M"))

    circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R2", ctype="resitor", cvalue=1, cunit="M"))
    circuit_array.add_circuit_component( bc.TBaseCircuitComponent(cname="R3", ctype="resitor", cvalue=resitor_value, cunit="M"))

    comps = circuit_array.get_component_list()

    circuit_array.connect_components_with_parallel(comps[0],comps[1])
    circuit_array.connect_components_with_series(comps[0],comps[2])
    circuit_array.connect_components_with_series(comps[2],comps[3])
    
    circuit = cs.build_pyspice_circuit(circuit_array, gnd_label='JR3-2', circuit_title=circuit_title)

    return circuit

def gem_plate_configuration(resitor_value=10, circuit_title='THGEM Plate'):
    """!
    @brief get plate circuit 

    @param resitor_value pull-down resistor value
    @param circuit_title title of PySpice circuit object
    
    @return circuit object defined by PySpice
    """
    logger = Logging.setup_logging()

    circuit = Circuit(circuit_title)
    circuit.R(1, 'input', circuit.gnd, resitor_value@U.u_MΩ)      

    return circuit

def double_minitpc_double_thgem(resistors=[1,10,10,10]):
    """!
    @brief get circuits object with two TPCs(2gem) connected in parallel

    @param resistors pull-down resistor value list
    
    @return circuit object list. each circuit is defined by PySpice
    """
    if len(resistors) != 4:
        print('number of resitor is invalid.')
        return None
    
    circuit_titles = ["Filed Cage and THGEM1 top",'THGEM1 bottom','THGEM2 top','THGEM2 bottom']
    circuits = []

    for i in range(len(resistors)):
        if i == 0:
            circuits.append(minitpc_filedcage_configuration(version=2,resitor_value=resistors[i],circuit_title=circuit_titles[i]))
        else:
            circuits.append(gem_plate_configuration(resitor_value=resistors[i], circuit_title=circuit_titles[i]))
    
    return circuits

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--type", help="dump comment", type=str, default="condition")
    parser.add_argument("-r", "--resistors", nargs="+", type=float, help="list of items", default=[1,10,10,10])
    parser.add_argument("-v", "--voltages", nargs="+", type=float, help="list of items", default=[-1400,-583,-480,-440,-40])
    parser.add_argument("-c", "--conditions", nargs="+", type=float, help="list of items", default=[-1,400,-1,400,-1])
    # parser.add_argument("-f", "--flag", help="sample flag", action="store_true") 
    # parser.add_argument("-v", "--values", nargs="+", type=int, help="list of items", default=[-10])
    # parser.add_argument("-l", "--labels", nargs="+", type=str, help="list of items", default=["JR0-1"])

    args = parser.parse_args()
    
    simulator_type = args.type
    resistors = args.resistors
    input_voltages = args.voltages
    input_conditions = args.conditions

    spaces = {
        'drift' : 2.8, 'gem1' : 0.04, 'transfer' : 0.2,
        'gem2' : 0.04, 'induction' : 0.2
    } 

    circuits = double_minitpc_double_thgem(resistors=resistors)

    if simulator_type == 'voltage':

        voltages = [
            [{'junction':'JR0-1', 'value':input_voltages[0]}, {'junction':'JR2-2', 'value':input_voltages[1]}],
            [{'junction':'input', 'value':input_voltages[2]}],
            [{'junction':'input', 'value':input_voltages[3]}],
            [{'junction':'input', 'value':input_voltages[4]}]
        ]
        
        setting = TBaseVoltageSettingData(input=circuits, spaces=spaces, voltages=voltages, pressure=0.2)
        
        # setting.check_stage_object()
        setting.simulate_all_stage()
        setting.get_simulated_source_voltage_current(True)
        setting.calculate_field_strength()
        setting.get_condition(True)

    elif simulator_type == 'condition':

        setting = TBaseVoltageSettingData(input=circuits, spaces=spaces, pressure=0.2)
        
        setting.set_condition(input_conditions,False)
        trial = setting.estimate_trial_input_voltage()
        voltages = [
            [{'junction':'JR0-1', 'value':trial[-1]}, {'junction':'JR2-2', 'value':trial[-2]}],
            [{'junction':'input', 'value':trial[-3]}],
            [{'junction':'input', 'value':trial[-4]}],
            [{'junction':'input', 'value':trial[-5]}]
        ]

        setting.set_voltages(voltage_list=voltages)

        final = setting.search_first_stage_voltages(debug_flag=False)
        
        voltages = [
            [{'junction':'JR0-1', 'value':final[0]}, {'junction':'JR2-2', 'value':final[1]}],
            [{'junction':'input', 'value':trial[-3]}],
            [{'junction':'input', 'value':trial[-4]}],
            [{'junction':'input', 'value':trial[-5]}]
        ]

        circuits = double_minitpc_double_thgem(resistors=resistors)
        setting = TBaseVoltageSettingData(input=circuits, spaces=spaces, voltages=voltages, pressure=0.2)
        setting.simulate_all_stage()
        setting.get_simulated_source_voltage_current(True)
        setting.calculate_field_strength()
        setting.get_condition(True)

if __name__ == "__main__":
    main()
