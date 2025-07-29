import sys
import NaxToPy as N2P
from NaxToPy.Core import N2PModelContent
from POC_riveting.Core.Classes.ARBolt import ARBolt
from POC_riveting.Core.Classes.AR1DElement import AR1DElement
from POC_riveting.Core.Classes.ARPlate import ARPlate
import numpy as np
import Tcl


def validation_model(ARBolt_list , model):
    ...

    max_length_Elements1D = max(len(bolt.Elements1DIDs) for bolt in ARBolt_list)

    def write_set_bolt_to_tcl(elements_list, output_file_set, set_number):
        with open(output_file_set, 'w') as f:
            f.write(f"*createentity sets cardimage=SET_ELEM name={set_number}Elements1D\n")
            f.write(f"*setvalue sets id={set_number} ids={{elems {' '.join(str(elem) for elem in elements_list)}}}\n")


    def write_midpoint_to_tcl(midpoint_list, output_file_midpoint, set_number):
        with open(output_file_midpoint, 'w') as f:
            f.write(f"*createentity comps name=midpoint_{set_number}Elements1D" + "\n")
            for coords in midpoint_list:
                midpoint_coords = coords
                x = float(midpoint_coords[0]) 
                y = float(midpoint_coords[1])
                z = float(midpoint_coords[2])
                coord_system = 0
                f.write(f"*createpoint " + str(x) + " " + str(y) + " " + str(z) + " " + str(coord_system) + "\n")

    def create_set(ARBolt_list, model, num_elements1D, set_number):
        elements_IDs_list = []
        midpoint_list = []

        for bolt in ARBolt_list:
            if len(bolt.Elements1DIDs) == num_elements1D:
                # List of element IDs
                for Elements1D in bolt.Elements1D:
                    id_cfast = Elements1D.ID
                    elements_IDs_list.append(id_cfast)

                for plate in bolt.Plates:
                    id_plate = plate.ElementIDs[0]
                    elements_IDs_list.append(id_plate)


                # Calculate the coordinates of the midpoint
                first_node = bolt.Elements1D[0].GA
                first = np.array([first_node.X, first_node.Y, first_node.Z])

                last_node = bolt.Elements1D[-1].GB
                last = np.array([last_node.X, last_node.Y, last_node.Z])

                middle_coords = (first + last) / 2
                midpoint_list.append(middle_coords)


        set_IDs_list = list(set(elements_IDs_list))



        output_file_set = f"C:\\Users\\nsesmero\\Desktop\\MODEL_1\\prueba7_{set_number}Elements1D.tcl"
        write_set_bolt_to_tcl(set_IDs_list, output_file_set, set_number)


        output_file_midpoint = f"C:\\Users\\nsesmero\\Desktop\\MODEL_1\\prueba7_midpoint_{set_number}Elements1D.tcl"
        write_midpoint_to_tcl(midpoint_list, output_file_midpoint, set_number)

    
    for i in range(1, max_length_Elements1D + 1):
        create_set(ARBolt_list, model, i, i)

