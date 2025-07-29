""" Module with function  bolt_reader"""
import NaxToPy as N2P
from io import open
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARBolt import ARBolt
import os

# The function bolt_reader will obtain a bolts list with the input of a file path and a list of bolts from a model.

def bolt_reader(path_file: str, ARBolt_list: list[ARBolt]) -> list[ARBolt]:
    """Function which reads a csv, txt, etc file containing bolts information: ID, bolt type, nut type, head node and
    designation; and a list of bolts from a model. It compares them in order to obtain the updated data of the bolts
    that are both in the file and the model.

        Args: 
            path_file: str
            ARBolt_list: list[ARBolt]

        Returns:
            bolt list: list[ARBolt]

        Calling example:

                bolts = bolt_reader(path_file = path_file_csv, ARBolt_list = bolts)

    Additional information:

    •	When reading the csv file, if any ID is not an integer, the corresponding fastener will not be taken into consideration.
        A warning message will be displayed.

    •	When reading the csv file, if fastener ID is repeated, it will not be taken into consideration. A warning message
        will be displayed.

    •	If this function is not called, all the bolts will be analysed, the ID will be maintained from the previous functions,
        and the attributes of bolt type, nut type and head will not be filled. But there will not be much extra problem,
        as the program will continue normally.

    •	It is important to remember that for the CBUSH and CBAR cases it is necessary to indicate a bolt diameter, as it
        is not defined in the property card.

    """

    if os.path.exists(path_file) and os.path.isfile(path_file):

        ################################# FILE READING ############################################

        # The file that needs to be studied is opened and read. Please introduce a correct file path.
        with open(path_file, 'r') as file:
            # Lines are read independently
            lines = file.readlines()

        New_ARBolt_List = [] # New list in order to save the data looked for.
        bolt_ids = [] # List in order to check that there is no repeated IDs.
        corrected_syntax_lines = []  # List to store corrected lines by their syntax.
        lists_bolts = []  # List to store the split values of the read lines.
        types_bolt = [] # List to store all the names of the bolt types.
        types_nut = [] # List to store all the names of the nut types.
        heads_nodes = [] # List to store all the heads positions.
        designations = [] # List to store all the designations (fasteners allowables database)
        diameters = [] # List to store all the diameters of the bolts.

        # The iteration throughout the lines is carried out.
        for i, line in enumerate(lines):

            # Lines starting with a '#' character are skipped because they are supposed to be comments.
            if line.startswith("#"):
                continue

            # Lines that do not start with a correct ID for the bolt are discarded .
            if line[0].isdigit():
                # In order to support every kind of file input, the syntax is corrected.
                corrected_syntax_line = line.replace(',', ' ').replace(';',' ').strip()
                corrected_syntax_lines.append(corrected_syntax_line)
                # The lines are split into the 3 data we obtain from the file.
                lists_bolt = corrected_syntax_line.split('\t') if '\t' in corrected_syntax_line else corrected_syntax_line.split(' ')
                if len(lists_bolt) == 3:
                    lists_bolt.append(None)
                lists_bolts.append(lists_bolt)
            elif i == 0:
                continue
            else:
                # A warning message is shown if the ID was not given in a numeric syntax.
                N2P.N2PLog.Warning.user("[bolt_reader] Bolt has been discarded because the bolt ID has a non-numeric definition: in line number: {}".format(i+1))
        for small_lists in lists_bolts:
            bolt_id = small_lists[0]
            # Verify if the bolt has the same ID as any that has already been studied. If it is repeated, discard it.
            if bolt_id in bolt_ids:
                N2P.N2PLog.Warning.user("[bolt_reader] The bolt with ID {} in line {} already exists.".format(bolt_id, i+1))
            else:
                bolt_ids.append(int(bolt_id))

                # Create lists for every data obtained from the csv.
                type_bolt = small_lists[4]
                types_bolt.append(type_bolt)
                type_nut = small_lists[5]
                types_nut.append(type_nut)
                head_node = small_lists[1]
                heads_nodes.append(head_node)
                designation = small_lists[3]
                designations.append(designation)
                diameter = small_lists[2]
                diameters.append(diameter)

                # List stored in memory with the ID, Type of bolt, Type of nut and Head Position from the csv file with corrections.
                bolt_data = [bolt_ids, types_bolt, types_nut, heads_nodes, designations, diameters]
            

        ############################################ COMPARISON FILE VS INPUT LIST ####################################################

        # Comparison between the list of bolt IDs in the path file and the list of bolt IDs in the input ARBolt list.

        # Run through the list of the bolt IDs obtained previously in this function by the path file.
        for j, boltid in enumerate(bolt_ids):

            # Run through the list of elements 1D given by the user as an input.
            for bolt in ARBolt_list:
                new_bolt_Elements1DIDs = [int(item) for item in bolt.Elements1DIDs]
                #Obtain the value for the ID of the element 1D in ARBolt_list in order to compare it to 'boltid'.
                if boltid in new_bolt_Elements1DIDs:
                    # If they are the same, save the data of ID, type of element 1D, type of nut and the data already stored in ARBolt_list in the 
                    # corresponding class attribute. 
                    bolt.ID = boltid
                    bolt.Type = types_bolt[j]
                    bolt.Nut = types_nut[j]
                    bolt.Designation = designations[j]

                    if diameters[j] is not None and diameters[j] != '':
                        bolt.Diameter = float(diameters[j])
                    else:
                        bolt.Diameter = None
                   
                    # When a given element 1D is given to be in the head position, this information is saved in a ARBolt attribute called Head with the form of a dictionary: {Element 1D ID: HEAD}
                    if heads_nodes[j] is not None and heads_nodes[j] != '':
                        bolt.HeadNode = {}
                        bolt.HeadNode[int(heads_nodes[j])] = "HEAD"


                    # Introduce the data in the new list only if it is a new bolt. 
                    if bolt in New_ARBolt_List:
                        pass
                    else:
                        New_ARBolt_List.append(bolt)

        return New_ARBolt_List

    # If the file path is not found or the file is not valid for the study, the function will not be used and it will be intended that another file path is introduced.
    else:
        N2P.N2PLog.Error.user("[bolt_reader] Try and introduce another path direction. The one you selected cannot be found or it is insecure.") 
        return None, None
