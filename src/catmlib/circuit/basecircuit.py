"""!
@file basecircuit.py
@version 1
@author Fumitaka ENDO
@date 2025-07-12T10:15:54+09:00
@brief basic class for making divider circuit
"""
import argparse
import pathlib
import schemdraw
import schemdraw.elements as elm
import networkx as nx
import matplotlib.pyplot as plt
import copy

this_file_path = pathlib.Path(__file__).parent

class TBaseCircuitComponent():
    """!
    @class TBaseCircuitComponent
    @brief basic circuit parts class
    """

    def __init__(self, cname="C1", ctype="resitor", cvalue=1, cunit="M"):
        """!
        @brief initialze object
        @param cname label name of component
        @param ctype parts type
        @param cvalue part values
        @param cunit unit
        @return None
        """
        if (ctype == 'resitor') or (ctype == 'r'):
            cunit_title = cunit+"$\\Omega$"  

        elif (ctype == 'capacitor') or (ctype == 'c'):
            cunit_title = cunit+"F" 

        elif (ctype == 'inductor') or (ctype == 'i'):      
            cunit_title = cunit+"H" 

        self.component = {'name' : cname, 'type' : ctype , 'value' : cvalue, 'unit' : cunit_title, 'title' : f"{cname[0]}_{{{cname[1:]}}}"}
        self.pre_junction = {'name' : 'J'+cname+'-1', 'list' : ['J'+cname+'-2'], 'title' : f"J_{{ {self.component["title"]} }}^{{pre}}"}
        self.pos_junction = {'name' : 'J'+cname+'-2', 'list' : ['J'+cname+'-1'], 'title' : f"J_{{ {self.component["title"]} }}^{{post}}"}
    
    def add_pre_junction(self, label=None):
        """!
        @brief add connection before parts
        @param label junction name
        @return None
        """
        if label is not None:
            self.pre_junction['list'].append(label)

    def add_post_junction(self, label=None):
        """!
        @brief add connection after parts
        @param label junction name
        @return None
        """
        if label is not None:
            self.pos_junction['list'].append(label)

    def get_component_title(self,flag=True):
        """!
        @brief write title for drawing and return title 
        @param flag switch title option. if ture, parts value is included 
        @return title : str
        """
        if flag:
            title = f"${self.component["title"]}={self.component["value"]}$ [{self.component["unit"]}]"
        else:
            title = f"${self.component["title"]}$"
        
        return title 
    
    def check_component_information(self):
        """!
        @brief dump object information
        @return None
        """
        print( ", ".join(f"{k}: {v}" for k, v in self.component.items()))


    def check_diagram(self,value_flag=True):
        """!
        @brief draw circuit
        @param value_flag flag for title 
        @return None
        """
        d = schemdraw.Drawing(unit=2.0, inches_per_unit=3.0)
        d.add(elm.Dot(d='down', label="$"+self.pre_junction["title"]+"$",lblpos='right', color='gray'))
        d.add(elm.Resistor(d='down', label=self.get_component_title(value_flag)))
        d.add(elm.Dot(d='down',label="$"+self.pos_junction["title"]+"$",lblpos='right', color='gray'))
        
        d.draw() 

class TCircuitComponentsArray():
    """!
    @class TCircuitComponentsArray
    @brief array of TBaseCircuitComponent for circuit making
    """

    def __init__(self):
        """!
        @brief initialze object
        @return None
        """
        self.components = []
        self.connection_list = []
    
    def add_circuit_component(self, comp:TBaseCircuitComponent):
        """!
        @brief add TBaseCircuitComponent
        @param comp parts information(TBaseCircuitComponent) to be added 
        @return None
        """
        self.components.append(comp)

    def get_component_list(self):
        """!
        @brief get parts list 
        @return None
        """
        return self.components
    
    def find_index_by_component_name(self, name):     
        """!
        @brief index finder using component name
        @param name component name
        @return index
        """   
        for idx, comp in enumerate(self.components):
            if comp.component['name'] == name:
                return idx

        return None

    def connect_components_with_series(self,component1:TBaseCircuitComponent,component2:TBaseCircuitComponent):
        """!
        @brief make connection with sereies circuit (component1 -> component2)
        @param component1 component name
        @param component2 component name
        """     
        component1.add_post_junction(component2.pre_junction['name'])
        component2.add_pre_junction(component1.pos_junction['name'])

        index1 = self.find_index_by_component_name(component1.component['name'])
        index2 = self.find_index_by_component_name(component2.component['name'])

        self.connection_list.append({'type' : 'series', 'list' : [index1, index2]})

    def connect_components_with_parallel(self,component1:TBaseCircuitComponent,component2:TBaseCircuitComponent):
        """!
        @brief make connection with parallel (open and close parallel circuit)

                 --------------
                 |            |    
            component1   component2
                 |            |    
                 --------------

        @param component1 component name
        @param component2 component name
        """    
        component1.add_pre_junction(component2.pre_junction['name'])
        component2.add_pre_junction(component1.pre_junction['name'])

        component1.add_post_junction(component2.pos_junction['name'])
        component2.add_post_junction(component1.pos_junction['name'])

        index1 = self.find_index_by_component_name(component1.component['name'])
        index2 = self.find_index_by_component_name(component2.component['name'])

        self.connection_list.append({'type' : 'parallel', 'list' : [index1, index2]})
    
    def connect_components_with_close_parallel(self,component1:TBaseCircuitComponent,component2:TBaseCircuitComponent, skip_number=0):
        """!
        @brief make connection with parallel (close parallel circuit)
                 |            |    
            component0   component2
                 |            |            
                 |            |    
            component1        | <- skip number
                 |            |    
                 --------------

        @param component1 component name
        @param component2 component name
        @param skip_number number for adjusting the drawing with schemaDraw 
        """
        component1.add_post_junction(component2.pos_junction['name'])
        component2.add_post_junction(component1.pos_junction['name'])

        index1 = self.find_index_by_component_name(component1.component['name'])
        index2 = self.find_index_by_component_name(component2.component['name'])

        self.connection_list.append({'type' : 'parallel-close', 'list' : [index1, index2], 'skip' : skip_number})

    def connect_components_with_open_parallel(self,component1:TBaseCircuitComponent,component2:TBaseCircuitComponent, offset_x=0, offset_y=0):
        """!
        @brief make connection with parallel (open parallel circuit)

                           offset (x, y)
                 -------------o-------------- 
                 |            |             |    
            component0   component1   component2
                 |            |             |   
                 
        @param component1 component name
        @param component2 component name
        @param offset_x offset postion for reference component 
        @param offset_y offset postion for reference component
        """
        component1.add_pre_junction(component2.pre_junction['name'])
        component2.add_pre_junction(component1.pre_junction['name'])

        index1 = self.find_index_by_component_name(component1.component['name'])
        index2 = self.find_index_by_component_name(component2.component['name'])

        self.connection_list.append({'type' : 'parallel-open', 'list' : [index1, index2], 'x' : offset_x, 'y' : offset_y})

    def connect_with_down_line(self):
        """!
        @brief write line for drawing with schemadraw
        """
        self.connection_list.append({'type' : 'down'})

    def check_diagram(self,prallel_length=2, value_flag=False):
        """!
        @brief draw circuit
        @param prallel_length length of parallel circuit for drawing
        @param value_flag label tilel flag. if true value will be included
        """
        saved_positions = {}
        d = schemdraw.Drawing(unit=2.0, inches_per_unit=3.0)

        for i in range(len(self.connection_list)):

            # print(f'{self.components[self.connection_list[i]['list'][0]].component['name']}', 
            #       f'{self.components[self.connection_list[i]['list'][1]].component['name']}',
            #       self.connection_list[i]['type'])
            
            if self.connection_list[i]['type'] == 'series':
                
                if i == 0:
                    ipos = copy.deepcopy(d.here)
                    itheta = copy.deepcopy(d.theta)
                    saved_positions[f'{self.components[self.connection_list[i]['list'][0]].component['name']}'] = (ipos, itheta)
                    d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][0]].get_component_title(value_flag)))
                                
                ipos = copy.deepcopy(d.here)
                itheta = copy.deepcopy(d.theta)
                saved_positions[f'{self.components[self.connection_list[i]['list'][1]].component['name']}'] = (ipos, itheta)
                d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][1]].get_component_title(value_flag)))
            
            elif self.connection_list[i]['type'] == 'parallel': 
                
                if i == 0:
                    ipos = copy.deepcopy(d.here)
                    itheta = copy.deepcopy(d.theta)
                    saved_positions[f'{self.components[self.connection_list[i]['list'][1]].component['name']}'] = (ipos, itheta)
                    d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][0]].get_component_title(value_flag)))
                
                ipos = copy.deepcopy(d.here)
                itheta = copy.deepcopy(d.theta)
                saved_positions[f'{self.components[self.connection_list[i]['list'][1]].component['name']}'] = (ipos, itheta)
                reference_posision = saved_positions.get(f'{self.components[self.connection_list[i]['list'][0]].component['name']}')

                d.add(elm.Line(d='right',l=prallel_length))
                d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][1]].get_component_title(value_flag)))
                d.add(elm.Line(d='left',l=prallel_length))
         
            elif self.connection_list[i]['type'] == 'parallel-open': 
                
                if i == 0:
                    ipos = copy.deepcopy(d.here)
                    itheta = copy.deepcopy(d.theta)
                    saved_positions[f'{self.components[self.connection_list[i]['list'][1]].component['name']}'] = (ipos, itheta)
                    d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][0]].get_component_title(value_flag)))
        
                ipos = copy.deepcopy(d.here)
                itheta = copy.deepcopy(d.theta)
                reference_posision = saved_positions.get(f'{self.components[self.connection_list[i]['list'][0]].component['name']}')

                dx = reference_posision[0][0] - ipos[0] + self.connection_list[i]['x']
                dy = reference_posision[0][1] - ipos[1] + self.connection_list[i]['y']
                d.move(dx,dy)
                d.theta = reference_posision[1]

                ipos = copy.deepcopy(d.here)
                itheta = copy.deepcopy(d.theta)

                saved_positions[f'{self.components[self.connection_list[i]['list'][1]].component['name']}'] = (ipos, itheta)

                # print(dx, reference_posision[0][0] , ipos[0], dy, reference_posision[0][1] , ipos[1], )

                d.add(elm.Line(d='right',l=prallel_length))
                d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][1]].get_component_title(value_flag)))

            elif self.connection_list[i]['type'] == 'parallel-close': 
                
                if i == 0:
                    ipos = copy.deepcopy(d.here)
                    itheta = copy.deepcopy(d.theta)
                    saved_positions[f'{self.components[self.connection_list[i]['list'][1]].component['name']}'] = (ipos, itheta)
                    d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][0]].get_component_title(value_flag)))
        
                ipos = copy.deepcopy(d.here)
                itheta = copy.deepcopy(d.theta)
                saved_positions[f'{self.components[self.connection_list[i]['list'][1]].component['name']}'] = (ipos, itheta)
                
                d.add(elm.Resistor(d='down', label=self.components[self.connection_list[i]['list'][1]].get_component_title(value_flag)))

                for i in range(self.connection_list[i]['skip']):
                    d.add(elm.Line(d='down'))

                d.add(elm.Line(d='left',l=prallel_length))
            
            elif self.connection_list[i]['type'] == 'down':
                d.add(elm.Line(d='down'))

        d.add(elm.Ground())

        # print(saved_positions)

        d.draw() 

    def build_nodes(self) -> dict:
        """!
        @brief make connection network for simple connection checker
        """
        nodes = {}
        for comp in self.components:
            for junction in [comp.pre_junction, comp.pos_junction]:
                name = junction["name"]
                connected = junction["list"]

                if name in nodes:
                    nodes[name].extend(connected)
                else:
                    nodes[name] = list(connected)

        for k in nodes:
            nodes[k] = list(set(nodes[k]))

        return nodes
    
    def check_connection(self):
        """!
        @brief check connection topology with matplotlib
        """
        nodes = self.build_nodes()

        G = nx.Graph()
        for node, neighbors in nodes.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor)

        pos = nx.spring_layout(G)  
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=12)
        plt.show()

def main():

    circuit = TCircuitComponentsArray()

    circuit.add_circuit_component( TBaseCircuitComponent(cname="R0", ctype="resitor", cvalue=0.5, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R1", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R2", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R3", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R4", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R5", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R6", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R7", ctype="resitor", cvalue=0.5, cunit="M"))

    circuit.add_circuit_component( TBaseCircuitComponent(cname="R8", ctype="resitor",  cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R9", ctype="resitor",  cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R10", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R11", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R12", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R13", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R14", ctype="resitor", cvalue=1, cunit="M"))

    circuit.add_circuit_component( TBaseCircuitComponent(cname="R15", ctype="resitor", cvalue=0.5, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R16", ctype="resitor", cvalue=1,   cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R17", ctype="resitor", cvalue=1,   cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R18", ctype="resitor", cvalue=1,   cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R19", ctype="resitor", cvalue=1,   cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R20", ctype="resitor", cvalue=1,   cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R21", ctype="resitor", cvalue=1,   cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R22", ctype="resitor", cvalue=0.5, cunit="M"))

    circuit.add_circuit_component( TBaseCircuitComponent(cname="R23", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R24", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R25", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R26", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R27", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R28", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R29", ctype="resitor", cvalue=1, cunit="M"))

    circuit.add_circuit_component( TBaseCircuitComponent(cname="R30", ctype="resitor", cvalue=1, cunit="M"))

    circuit.add_circuit_component( TBaseCircuitComponent(cname="R31", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R32", ctype="resitor", cvalue=1, cunit="M"))
    circuit.add_circuit_component( TBaseCircuitComponent(cname="R33", ctype="resitor", cvalue=1, cunit="M"))


    comps = circuit.get_component_list()

    circuit.connect_components_with_series(comps[0],comps[1])
    circuit.connect_components_with_series(comps[1],comps[2])
    circuit.connect_components_with_series(comps[2],comps[3])
    circuit.connect_components_with_series(comps[3],comps[4])
    circuit.connect_components_with_series(comps[4],comps[5])
    circuit.connect_components_with_series(comps[5],comps[6])
    circuit.connect_components_with_series(comps[6],comps[7])

    circuit.connect_components_with_open_parallel(comps[0],comps[8])
    circuit.connect_components_with_series(comps[8],comps[9])
    circuit.connect_components_with_series(comps[9],comps[10])
    circuit.connect_components_with_series(comps[10],comps[11])
    circuit.connect_components_with_series(comps[11],comps[12])
    circuit.connect_components_with_series(comps[12],comps[13])
    # circuit.connect_with_down_line()
    circuit.connect_components_with_close_parallel(comps[7],comps[14],1)

    circuit.connect_components_with_open_parallel(comps[8],comps[15],offset_x=8)
    circuit.connect_components_with_series(comps[15],comps[16])
    circuit.connect_components_with_series(comps[16],comps[17])
    circuit.connect_components_with_series(comps[17],comps[18])
    circuit.connect_components_with_series(comps[18],comps[19])
    circuit.connect_components_with_series(comps[19],comps[20])
    circuit.connect_components_with_series(comps[20],comps[21])
    circuit.connect_components_with_close_parallel(comps[14],comps[22])

    circuit.connect_components_with_open_parallel(comps[15],comps[23],offset_x=8)
    circuit.connect_components_with_series(comps[23],comps[24])
    circuit.connect_components_with_series(comps[24],comps[25])
    circuit.connect_components_with_series(comps[25],comps[26])
    circuit.connect_components_with_series(comps[26],comps[27])
    circuit.connect_components_with_series(comps[27],comps[28])
    # circuit.connect_with_down_line()
    circuit.connect_components_with_close_parallel(comps[21],comps[29],1)

    circuit.connect_components_with_series(comps[7],comps[30])

    circuit.connect_components_with_series(comps[29],comps[31])
    circuit.connect_components_with_series(comps[30],comps[32])
    circuit.connect_components_with_series(comps[31],comps[33])

    # circuit.check_connection()
    circuit.check_diagram(prallel_length=8, value_flag=True)

if __name__ == "__main__":
    main()
