from NaxToPy import N2PLog
from NaxToPy.Core import N2PModelContent
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PConnector import N2PConnector
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARPlate import ARPlate
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.AR1DElement import AR1DElement
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Functions.ARAuxiliarFunctions import equal_points
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Functions.ARRotation import rotate_tensor2D, project_vector, angle_between_2_systems, transformation_for_interpolation
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Functions.ARBilinearInterpolation import interpolation
from time import time
import numpy as np
import csv


class ARBolt:
    """Class which contains information of every bolted union. Each instance will contain information of one complete
     union.

    Attributes:
        ID: int
        TypeFasteners: str
        Type: str
        Nut: str
        HeadNode: dict
        Diameter: float
        Designation: str
        ContainsConnector: bool
        ConnectorsInBolt: list[N2PConnector]
        ConnectorsIDs: list[int]

        Elements1D: list[AR1DElement]
        Plates: list[ARPlates]
        Elements1DIDs:  list[int]
        FZmax: dict
        AttachingPlates: set
        Pitch: float

        serialized: bool
        """

    def __init__(self, id: int):
        """ARBolt Constructor."""

        self.ID: int = id
        self.TypeFasteners: str = None
        self.Type: str = None
        self.Nut: str = None
        self.Diameter: float = None
        self.HeadNode: dict = {None: None}
        self.Designation: str = None
        self.ContainsConnector: bool = False
        self.ConnectorsInBolt: list[N2PConnector] = []
        self.ConnectorsIDs: list[int] = []

        self.Elements1D: list[AR1DElement] = []
        self.Plates: list[ARPlate] = []

        self.Elements1DIDs: list[int] = []
        self.FZmax: dict = {}

        self.AttachingPlates = set()

        self.Pitch: float = None

        self.serialized: bool = False

    ##################################################################################################
    ####################################### CLASS METHODS ############################################
    ##################################################################################################

    def append_element1D(self, element1D: AR1DElement) -> None:
        """ Method of the class ARBolt which is used in order to add any Element 1D to an already created ARBolt
         instance.

        Args:
            element1D: AR1DElement

        Calling example:

                bolt.append_element1D(element1D = element1D)

        """
        if isinstance(element1D, AR1DElement):
            self.Elements1D.append(element1D)
            self.Elements1DIDs.append(element1D.ID)
        else:
            N2PLog.Warning.W518()

    def append_plate(self, plate: ARPlate) -> None:

        """ Method of the class ARBolt which is used in order to add any plate to an already created ARBolt
         instance.

        Args:
            plate: ARPlate

        Calling example:

                bolt.append_plate(plate = plate)

        """
        if isinstance(plate, ARPlate):
            self.Plates.append(plate)
        else:
            N2PLog.Warning.W517()

    def sort(self) -> None:

        """Method which takes the ARBolt element and sorts the elements in the correct order by their elements 1D's
        actual position in the model, taking into consideration the position of the head as well.

        Calling example:

                bolt.sort()

        Additional information:

        •	When first creating the “ARBolt” instances using the function “get_bolts”, the included fasteners and attached
            plates are introduced in the object without any specific order. This means that inside the “ARBolt” instance,
            the 1D Elements IDs attribute could be [101, 100, 102] and the plates IDs attribute could be [62, 64, 65, 62].

        •	Using this function, the order of these attributes would change leading to [100, 101, 102] in the case of the 1D
            Elements and [62, 63, 64, 65] in the plates case. Furthermore, if in the input csv file, the head node column
            was filled with the node ID 102, the order would be reversed and it would finally show: [102, 101, 100] and
            [65, 64, 63, 62].

        •	In the case when the “head node” column in the input csv is not filled, the bolt organisation will not take into
            account the head position and a warning message will be displayed.

        •	Even though the head position is not given, the organisation will be carried out either way. Nonetheless,
            the order of the fasteners and joined plates (although they are going to be correctly positioned) will be set
            indistinctly. This means that the first plate could be the last or vice versa.


        """

        ############################### ORGANISATION OF ELEMENTS 1D #####################################

        nodes_ordered = []  # List of ordered element1D nodes.
        nodes_disordered = []  # List of disordered element1D nodes.
        bolt_element1Ds_copy = self.Elements1D.copy()  # Copied list for the Elements1D in each bolt

        # The loop regarding the element1Ds will be carried out until every element1D has been studied.
        while len(bolt_element1Ds_copy) > 0:
            for element1D in bolt_element1Ds_copy:
                element1D_nodes = (element1D.ConnectionPlateA, element1D.ConnectionPlateB)  # Tuple with the nodes of the element1D GA and GB.
                # If the list of ordered nodes is empty, append the element1D.
                if len(nodes_ordered) == 0:
                    nodes_ordered.append(element1D_nodes[0])
                    nodes_ordered.append(element1D_nodes[1])

                    # Remove the element1D from the copied list in order to study the remaining ones.
                    bolt_element1Ds_copy.remove(element1D)

                elif any(equal_points(element1D_nodes[0], point) for point in nodes_ordered):
                    # If GA is contained in the ordered nodes list and it is in the first position, reverse the order of "element1D_nodes" and insert it in the first position.
                    if equal_points(element1D_nodes[0], nodes_ordered[0]):
                        nodes_ordered.insert(0, element1D_nodes[1])
                        nodes_ordered.insert(1, element1D_nodes[0])
                    # If GA is contained in the ordered nodes list and it is in the last position, append the element1D to the ordered list in the last position.
                    elif equal_points(element1D_nodes[0], nodes_ordered[-1]):
                        nodes_ordered.append(element1D_nodes[0])
                        nodes_ordered.append(element1D_nodes[1])

                    # Remove the element1D from the copied list in order to study the remaining ones.
                    bolt_element1Ds_copy.remove(element1D)

                elif any(equal_points(element1D_nodes[1], point) for point in nodes_ordered):
                    # If GB is contained in the ordered nodes list and it is in the first position, append the element1D to the ordered list in the first position.
                    if equal_points(element1D_nodes[1], nodes_ordered[0]):
                        nodes_ordered.insert(0, element1D_nodes[0])
                        nodes_ordered.insert(1, element1D_nodes[1])
                    # If GA is contained in the ordered nodes list and it is in the last position, reverse the order of "element1D_nodes" and insert it in the last position.
                    elif equal_points(element1D_nodes[1], nodes_ordered[-1]):
                        nodes_ordered.append(element1D_nodes[1])
                        nodes_ordered.append(element1D_nodes[0])

                    # Remove the element1D from the copied list in order to study the remaining ones.
                    bolt_element1Ds_copy.remove(element1D)

        nodes_disordered = [(element1D.ConnectionPlateA, element1D.ConnectionPlateB) for element1D in self.Elements1D]

        nodes_disordered = [tuple(map(tuple, pair)) for pair in nodes_disordered]

        nodes_ordered_separated = list(zip(nodes_ordered[::2], nodes_ordered[1::2]))

        nodes_ordered_separated = [tuple(map(tuple, pair)) for pair in nodes_ordered_separated]

        # Check for the reversed grid points in the lists.
        nodes_disordered_corrected = []
        for element in nodes_disordered:
            element = tuple(map(tuple, element))
            if element in nodes_ordered_separated:
                nodes_disordered_corrected.append(element)
            else:
                element = (element[1], element[0])
                nodes_disordered_corrected.append(element)

        # List with the indexes of the changes made between the initial (disordered) and final (ordered) nodes lists.
        disordered_index_element1Ds = {element: index for index, element in enumerate(nodes_disordered_corrected)}

        order_changes_element1D = [disordered_index_element1Ds[element] for element in nodes_ordered_separated]

        
        # Switch of the order of each of the items related to the element1Ds themselves (not the plates they are connecting).
        self.Elements1DIDs = [self.Elements1DIDs[i] for i in order_changes_element1D]
        self.Elements1D = [self.Elements1D[i] for i in order_changes_element1D]

        # Organisation of the plates relative to their corresponding element1Ds. In this situation it does not matter the number of element1Ds in the bolt.
        # The plates will be organised for the position of the element1Ds in any case.
        ############################### ORGANISATION OF PLATES #####################################

        platesIDS_ordered = []  # List of ordered plates IDs.
        ARplates_ordered = []  # List of ordered ARPlates
        bolt_element1Ds_copy2 = self.Elements1D.copy()  # Copied list for the element1Ds in each bolt. (ordered)
        bolt_plates_copy = self.Plates.copy()  # Copy of disordered ARPlates list.

        # Obtain the list of plates IDs by the ordered element1Ds obtained previously.
        for element1D in bolt_element1Ds_copy2:
            plateA = element1D.TopPlateID  # Plate A which the element1D is connecting.
            plateB = element1D.BottomPlateID  # Plate B which the element1D is connecting.
            if plateA not in platesIDS_ordered:
                platesIDS_ordered.append(plateA)
            if plateB not in platesIDS_ordered:
                platesIDS_ordered.append(plateB)

        # Obtain the list of ARPlates with the correct order.
        for plateID in platesIDS_ordered:
            for plate in bolt_plates_copy:
                if plateID == plate.ID and plate not in ARplates_ordered:
                    ARplates_ordered.append(plate)

        ARplates_disordered = bolt_plates_copy  # List of lists with plate IDs disordered.

        disordered_index_plates = {element: index for index, element in enumerate(ARplates_disordered)}

        # List with the indexes of the changes made between the initial (disordered) and final (ordered) nodes lists.
        order_changes_plates = [disordered_index_plates[element] for element in ARplates_ordered]

        # Switch of the order of each of the items related to the plates that are connected by their respective element1Ds.
        self.Plates = [self.Plates[i] for i in order_changes_plates]

        #################################### SORTING BY THE HEAD POSITION ######################################################

        # Whenever the bolt does no have information about the head position, the order is maintained. It is assumed that the order is not important.
        if self.HeadNode == {None: None}:
            pass

        # When the head is given to be in a element1D which is not the first or last one, an error is given.
        elif any(self.HeadNode.get(node) == "HEAD" for node in nodes_ordered[1:-1]):
            N2PLog.Error.E503(self)
            self.HeadNode["Error"] = "Head in the middle of the bolt."

        # If the head is positioned in the last element1D of the bolt, switch its order.
        elif self.HeadNode.get(nodes_ordered[-1]) == "HEAD":
            self.Elements1DIDs.reverse()
            self.Elements1D.reverse()
            self.Plates.reverse()
            for element1D in self.Elements1D:
                element1D.ConnectionPlateA, element1D.ConnectionPlateB = element1D.ConnectionPlateB, element1D.ConnectionPlateA

        # Attribute called Element1DIDsJoined is defined and added to ARPlate.
        bolt_element1Dsids_copy = self.Elements1DIDs.copy()
        element1Dsjoined = []

        # Iteration through the element1Ds IDs in order to obtain a list with the length of the plates, showing each of the plates´ joined element1Ds. (ONLY FOR COMFORTABILITY IN EXPORTATION)

        if len(bolt_element1Dsids_copy) == 1:
            element1Dsjoined = [[bolt_element1Dsids_copy[0], 0], [bolt_element1Dsids_copy[0], 0]]
        else:
            for i in range(len(bolt_element1Dsids_copy) + 1):
                if i == 0:
                    first_element = [bolt_element1Dsids_copy[i], 0]
                    element1Dsjoined.append(first_element)
                elif 0 < i < len(bolt_element1Dsids_copy):
                    next_tuple = [bolt_element1Dsids_copy[i - 1], bolt_element1Dsids_copy[i]]
                    element1Dsjoined.append(next_tuple)
                elif i == len(bolt_element1Dsids_copy):
                    final_element = [bolt_element1Dsids_copy[i - 1], 0]
                    element1Dsjoined.append(final_element)

        for j, plate in enumerate(self.Plates):
            plate.Element1DIDsJoined = element1Dsjoined[j]

        return self

    def get_distance_to_edges(self, model: N2PModelContent) -> None:

        """Method that calculates the distance of each bolt to the edge for every plate in the union.

        Args:
            model: N2PModelContent

        Calling example:

                bolt.get_distance_to_edges(model = model1)

        Additional information:

        •	First, the intersection points of the bolt with each of the plates that are contained in the union is obtained.
            These will be the points to be used in each of the plates to get the distance to the edge.

        •	Next, all the elements that are attached to the element where the intersection point is are retrieved using
            the NaxToPy function called “get_elements_attached”. Right after this, the function “get_free_edges” outputs
            a list of segments from the attached elements which define the free edges of the selection.

        •	Thus, the distance from the intersection point to each of the segments is obtained and compared to the rest
            in order to get the minimum one, which is the desired value.

        """

        # Specify supported elements in plates
        supported_elements = ["CQUAD4", "CTRIA3"]

        # First, get domain of all CTRIA and CQUAD in model
        domain = [element for element in model.get_elements() if
                  element.TypeElement in supported_elements]

        # Get the x axis of the vector. It is defined by a point and a vector.
        # It is assumed that all element1D ends in the bolt are colinear. Only the first and last points are used.

        origin = np.array(self.Elements1D[0].ConnectionPlateA)
        end = np.array(self.Elements1D[-1].ConnectionPlateB)

        # x axis of the element1D
        element1D_vector = end - origin

        # One distance will be needed for every plate in the bolt
        for plate in self.Plates:

            # First, it is checked if the plate elements info is complete. If not, the plate is skipped.
            if len(plate.Elements) == 0:
                N2PLog.Warning.W512(plate, self)
                continue

            # the first element will define the plate plane
            plate_element = plate.Elements[0].Element

            # Find the intersection of the bolt axis with the plane of the element
            node1 = np.array([plate_element.Nodes[0].X, plate_element.Nodes[0].Y, plate_element.Nodes[0].Z])
            node2 = np.array([plate_element.Nodes[1].X, plate_element.Nodes[1].Y, plate_element.Nodes[1].Z])
            node3 = np.array([plate_element.Nodes[2].X, plate_element.Nodes[2].Y, plate_element.Nodes[2].Z])
            plane_normal = np.cross(node3 - node1, node2 - node1) / np.linalg.norm(
                np.cross(node3 - node1, node2 - node1))

            plate.Normal = tuple(plane_normal.tolist())

            t = np.dot(plane_normal, node1 - origin) / np.dot(plane_normal, element1D_vector)

            # intersection point of bolt x axis with plate plane
            intersection = origin + t * element1D_vector

            plate.IntersectionPoint = tuple(intersection.tolist())

            # Get free edges of plate
            attached_elems = model.get_elements_attached(cells=[plate_element],
                                                         domain=domain)
            free_edges = model.get_free_edges(attached_elems)


            # Loop for all free edges segments and store the minimum distance

            stored_distance = float('inf')
            for segment in free_edges:

                # Ends of the segment
                A = np.array([segment[1].X, segment[1].Y, segment[1].Z])
                B = np.array([segment[2].X, segment[2].Y, segment[2].Z])
                segment_length = np.linalg.norm(B - A)

                # Parameter that defines if the closest point to the line of the segment on the segment or outside
                ts = np.dot(intersection - A, B - A) / segment_length ** 2

                if ts <= 0:
                    # Closest point is A
                    distance = np.linalg.norm(A - intersection)
                elif ts >= 1:
                    # Closest point is B
                    distance = np.linalg.norm(B - intersection)
                else:
                    # Closest point is on the line segment
                    C = A + ts * (B - A)
                    distance = np.linalg.norm(C - intersection)

                # store the minimum distance
                if distance < stored_distance:
                    stored_distance = distance

            # Store distance
            plate.DistanceToEdge = stored_distance
        return self
    
    def _organise_forces(self, forcesmomentslist:list) -> list:
         """Method which takes a list of forces defined in the following format: [[FX, FY, FZ], [FX, FY, FZ], ..., [FX, FY, FZ]] and
         organises it in order to be consistent with the plates order and to be comfortable to export.
    
         Args:
             forcesmomentslist: list
    
         Returns:
             element1Dsjoinedforces: list

         Calling example:

                    organised_forces = bolt._organise_forces(forcesmomentslist = forces)
    
         """
    
         # Iteration through the element1Ds IDs in order to obtain a list with the length of the plates, showing each of the plates´ joined element1Ds.
         element1Dsjoinedforces = []
         if len(forcesmomentslist) == 1:
             element1Dsjoinedforces = [[forcesmomentslist[0], [0, 0, 0]],
                                         [forcesmomentslist[0], [0, 0, 0]]]
         else:
             for i in range(len(forcesmomentslist) + 1):
                 if i == 0:
                     first_element = [forcesmomentslist[i], [0, 0, 0]]
                     element1Dsjoinedforces.append(first_element)
                 elif 0 < i < len(forcesmomentslist):
                     next_tuple = [forcesmomentslist[i - 1], forcesmomentslist[i]]
                     element1Dsjoinedforces.append(next_tuple)
                 elif i == len(forcesmomentslist):
                     final_element = [forcesmomentslist[i - 1], [0, 0, 0]]
                     element1Dsjoinedforces.append(final_element)
    
         return element1Dsjoinedforces

    def get_forces(self,
                   results: dict) -> None:
        """Method which takes the ARBolt element and obtains the 1D Forces of each of the element1Ds belonging to each
        bolt. It will be done for each of the loadcases contained in the results dictionary. It also obtains the
        maximum Fz and FShear for each bolt.

        Forces will be introduced as an “AR1DElement” or “ARPlate” attribute in the form of a dictionary like:
        {Load Case ID: [FX, FY, FZ]}. FZmax and FShearmax will be introduced as an “ARBolt” attribute in the form of a
        dictionary like: {Load Case ID: FZmax}.


        Args:
            results: dict
            analysis_type: str

        Calling example:

                    bolt.get_forces(results = results, analysis_type = analysis_type)

        Additional information:

        •	F_shear: dictionary in the form {Load Case ID: Shear Force} which is represented in the 1D element reference
            frame.

        •	F_axial: dictionary in the form {Load Case ID: Axial Force} which is represented in the material system of
            the first plate in the bolt. This value will be the corresponding positive value if the fastener is in
            extension regime or 0 if it is in compression regime.

        •	F_ElementLocalSystem: dictionary in the form {Load Case ID: [FX, FY, FZ]} which is represented in the material
            system of the first plate in the bolt.

        •	F_BottomPlateSystem: dictionary in the form {Load Case ID: [FX, FY, FZ]} which is represented in the material
            system of the bottom plate regarding the fastener itself (not the whole bolt).

        •	F_TopPlateSystem: dictionary in the form {Load Case ID: [FX, FY, FZ]} which is represented in the material
            system of the top plate regarding the fastener itself (not the whole bolt).

        •	F_1D_PlatesOrganisation: “ARPlate” attribute, dictionary in the form {Load Case ID: [[FX, FY, FZ], [FX, FY, FZ]]}
            which is represented in a Local Reference Frame. This reference frame has as x-axis the material reference
            frame of the plate x-axis, the z-axis is coincident with the axial direction of the bolt and the y-axis is
            obtained via cross product. Each of the lists in the dictionary show the 1D forces corresponding to the
            fasteners that are joined to the plate. If there is only one fastener joined to the plate, the second list
            will be [0, 0, 0].

        •	F_1D_Altair: “ARPlate” attribute which is a dictionary in the form {Load Case ID: [FX, FY, FZ]} which is
            represented in the material reference frame of the first plate. This attribute takes into consideration if there
            are two fasteners joined to the plate and sums up the contributions.

        •	In addition, an attribute in the “ARBolt” instance called “FZmax” is filled showing the maximum axial force
            in the whole bolt, as well as the Load Angle.

        """

        material_system_1st_plate = self.Plates[0].Elements[0].Element.MaterialSystemArray

        for lc_id, result in results.items():
            forceslist_element_local_axis = []
            forceslist_material_1plate_axis = []
            for element1d in self.Elements1D:
                id = element1d.InternalID
                elem1d_system = element1d.Element.ElemSystemArray

                # X and Z forces are asked in switched position because FastPPH uses the 1D direction as the X-axis. 
                element1d_force = [result.get('FZ1D')[id], result.get('FY1D')[id], result.get('FX1D')[id]]
                # Local Reference Frame definition
                xlocal = material_system_1st_plate[0:3]
                zlocal = elem1d_system[0:3]
                ylocal = np.cross(zlocal, xlocal)
                LocalSystem = [xlocal[0], xlocal[1], xlocal[2], ylocal[0], ylocal[1], ylocal[2], zlocal[0], zlocal[1], zlocal[2]]

                #################################### SHEAR ###########################################

                # F shear calculation all in material axis of the first plate defined in the bolt.
                F_shear = np.array([element1d_force[1], element1d_force[2]])
                alpha = angle_between_2_systems(from_system=elem1d_system,
                                                to_system=material_system_1st_plate,
                                                plane_normal=material_system_1st_plate[6:9])

                R = np.array([[np.cos(alpha), np.sin(alpha)],
                             [-np.sin(alpha), np.cos(alpha)]])

                F_shear_rotated = np.matmul(R, F_shear)

                #################################### FORCES 1D ###########################################

                forces_to_rotate = [element1d_force[0], element1d_force[1]]

                ################################## LOCAL SYSTEM ############################

                betha_local = angle_between_2_systems(from_system=elem1d_system,
                                                to_system=LocalSystem,
                                                plane_normal=LocalSystem[6:9])

                R2_local = np.array([[np.cos(betha_local), np.sin(betha_local)],
                             [-np.sin(betha_local), np.cos(betha_local)]])

                F_1D_rotated_local_xy = np.matmul(R2_local, forces_to_rotate)
                F_1D_rotated_local = [F_1D_rotated_local_xy[0], F_1D_rotated_local_xy[1], element1d_force[2]]

                forceslist_element_local_axis.append(F_1D_rotated_local)

                ################################## 1ST PLATE MATERIAL SYSTEM ################

                betha = angle_between_2_systems(from_system=elem1d_system,
                                                to_system=material_system_1st_plate,
                                                plane_normal=material_system_1st_plate[6:9])

                R2 = np.array([[np.cos(betha), np.sin(betha)],
                             [-np.sin(betha), np.cos(betha)]])

                F_1D_rotated_prev = np.matmul(R2, forces_to_rotate)
                F_1D_rotated = [F_1D_rotated_prev[0], F_1D_rotated_prev[1], element1d_force[2]]

                forceslist_material_1plate_axis.append(F_1D_rotated)

                ################## FORCES IN ELEMENT1D LOCAL SYSTEM #########################

                element1d.F_ElementLocalSystem[lc_id] = F_1D_rotated
                element1d.F_axial[lc_id] = max(0, F_1D_rotated[2])
                element1d.F_shear[lc_id] = np.linalg.norm(np.array([element1d_force[1], element1d_force[2]]))
                element1d.LoadAngle[lc_id] = (np.rad2deg(np.arctan2(F_shear_rotated[1], F_shear_rotated[0])) + 360) % 360

                ################## FOR FASTPPH CSV #########################
                # BOTTOM PLATE
                bottom_plate = [plate for plate in self.Plates if plate.ID == element1d.BottomPlateID][0] # Validation of bottom plate
                to_system_bottom = bottom_plate.Elements[0].Element.MaterialSystemArray

                betha_bottom = angle_between_2_systems(from_system=elem1d_system,
                                                to_system=to_system_bottom,
                                                plane_normal=to_system_bottom[6:9])

                R2_bottom = np.array([[np.cos(betha_bottom), np.sin(betha_bottom)],
                               [-np.sin(betha_bottom), np.cos(betha_bottom)]])

                F_1D_rotated_bottom_xy = np.matmul(R2_bottom, forces_to_rotate)
                F_1D_rotated_bottom = [F_1D_rotated_bottom_xy[0], F_1D_rotated_bottom_xy[1], element1d_force[2]]


                element1d.F_BottomPlateSystem[lc_id] = F_1D_rotated_bottom

                # TOP PLATE
                top_plate = [plate for plate in self.Plates if plate.ID == element1d.TopPlateID][0] # Validation of top plate
                to_system_top = top_plate.Elements[0].Element.MaterialSystemArray

                betha_top = angle_between_2_systems(from_system=elem1d_system,
                                                to_system=to_system_top,
                                                plane_normal=to_system_top[6:9])

                R2_top = np.array([[np.cos(betha_top), np.sin(betha_top)],
                               [-np.sin(betha_top), np.cos(betha_top)]])

                F_1D_rotated_top_xy = np.matmul(R2_top, forces_to_rotate)

                F_1D_rotated_top = [F_1D_rotated_top_xy[0], F_1D_rotated_top_xy[1], element1d_force[2]]

                element1d.F_TopPlateSystem[lc_id] = F_1D_rotated_top
                
                ###########################################################################################

                # Get the organised lists in order to have a more comfortable exportation later on.

                element1Dsjoinedforces_material_1plate_axis = self._organise_forces(forceslist_material_1plate_axis)
                element1Dsjoinedforces_element_local_axis = self._organise_forces(forceslist_element_local_axis)

            self.FZmax[lc_id] = max([element1D.F_axial[lc_id] for element1D in self.Elements1D])

            ############################### FORCES 1D APPLIED IN EACH PLATE ###############################

            # Each plate gives the corresponding 1D forces that are applied on it. In plates where only one fastener is joined, the
            # forces are straight forward. However, when double joints (one fastener in each side of the plate) are taken into account,
            # the procedure is the following. The forces of both fasteners are obtained in the

            for j, plate in enumerate(self.Plates):
                # Attribute with forces in Local Reference Frame
                plate.F_1D_PlatesOrganisation[lc_id] = element1Dsjoinedforces_element_local_axis[j]

                # Forces in Material Reference Frame of each plate.
                forces = project_vector(vector = element1Dsjoinedforces_material_1plate_axis[j],
                                        from_system= material_system_1st_plate,
                                        to_system= plate.Elements[0].Element.MaterialSystemArray)

                # Case of plate with two fasteners connected.
                if len(forces) > 1:
                    forces = [x - y for x, y in zip(forces[1], forces[0])]

                plate.F_1D_Altair[lc_id] = forces

        return self

    def get_bypass_loads(self, model: N2PModelContent,
                         results: dict,
                         corner: bool,
                         area_factor: float = 2.5,
                         material_factor_list: list = [4.0, 4.5],
                         box_tol = 1e-3,
                         proj_tol = 0,
                         max_iter=200) -> None:

        """ Method which takes an ARbolt and a model with results information and obtains de bypass forces for each of
        the plates related to it. It is highly recommended to maintain the default values when using this function.
        However, if the user desired to vary any values, the area factor, material factor, box tolerance and max
        iterations could be defined by hand.

        Args:
            bolt:ARBolt
            model: N2PModelContent
            results: dict
            analysis_type: str
            area_factor: float (Default value is 2.5)
            material_factor: list (Default value is [4.0, 4.5]) which is [metallic material factor, composite material factor]
            box_tol: float (Default value is 1e-3)
            max_iter: int (Default value is 200)

        Calling example:

                    bolt.get_bypass_loads(model = model1, results = results, corner = corner_data , analysis_type = analysis_type)


        Procedure and methodology:

        •	The procedure carried out will be based on the crown method. Thus, the fluxes will be calculated using a
            square shaped box around the bolt in the plate plane and applying the conditions that will be now introduced.

        •	The first step in the calculation of bypass loads is the obtention of the box that will help define the area
            where the calculations will be made. This box dimension is defined using the following expression:

                                            a = 0.4 · area_factor · material_factor · Diameter

        •	Knowing the box dimension, the box should be defined using a specific orientation and order. This orientation
            is defined by the Box Reference Frame, which is coincident with the material system of the element where the
            bolt is pierced. This may experience a small variation because the z-axis is defined as the axial direction
            of the bolt, and sometimes the material system z-axis and the axial direction of the bolt do not fully coincide.

        •	Then, locating the Box System in the center of the box, the first point would be located in the point (-a, a)
            and it would continue in clockwise direction.

        •	It is important to take into consideration that this point disposal does not always coincide with what Altair
            displays. This is not important, because the final results for the bypass and total fluxes will be invariant.

        •	Adjacent elements will be evaluated until the distance from the bolt to them is greater than the semi diagonal
            of the box. After this, it is assured that no more points will be found far away and it does not make sense
            to keep looking. In the case that some points are still to be assigned, we can conclude that they lie outside
            the edge of the plate and should be projected.

        •	Therefore, in the case where all the points of the box lie within the free edges is quite straight forward.
            As already mentioned, the adjacent elements to the pierced one are evaluated in case any point is inside of it.
            This is done taking into consideration de so-called box tolerance, stopping the iterations when the element that
            is being analysed is far away from the box location.

        •	However, there are two possibilities where the box point location is not as straight forward. The first and
            clearer one is the case where the box points are outside the free edges. In this situation, the points are
            projected onto the mesh orthogonally. In the FastPPH tool used by Altair this projection does not always follow
            the same procedure, as sometimes the points are projected perpendicularly, other they are projected onto a close
            node, and others they are projected following a linear interpolation. In order to simplify this methodology,
            the projection in the case of this tool is selected to be always an orthogonal projection.

         •	The second critical case is when having a box that crosses a T-edge  or that gets out of a surface which
            does not finish in a free edge. The first of these two cases (where the box crosses a T-edge) is treated as the
            case where all points are located within the free edges; therefore, there should not be any projection to any
            surface. Nonetheless, when the box gets out of the borders of a surface and these borders are not free edges,
            they are treated as so. Thus, the same procedure as when having points outside the free edges: they are
            orthogonally projected onto the edge.

        •	The following step is to obtain the fluxes in each of the points of the boxes for each load case in order to
            obtain the final values for bypass and total loads afterwards. There are two options that are needed to be taken
            into account depending on the way that the results are asked for in the result files.

            -   CORNER DATA:

                This case takes place when the user asks for results in corner when running the model and obtaining the
                corresponding results. This can be done by selecting the CORNER or BILIN describer in the FORCE card.

                This means that the results will be directly given by node and not by element, giving several values for
                a node, related to the element where it is (as a node is share by several elements). Thus, the obtention
                of results from the op2s files is different when having corner data or not. It is important to understand
                that it is more accurate to use the results in corner, as there are more values to be used. This is the
                reason why when selecting Corner Data as False in the configuration file, a warning message is displayed.

                In the already explained function “get_results”, the function “get_result_ndarray” is in charge of retrieving
                a list of values of a desired magnitude. It has some inputs that are of interest taking into consideration
                that different type of results can be asked for. The first input is called “cornerData”, and it is a
                Boolean selecting the type of results wanted; and the next interesting input is “aveNodes” which serves
                to elect the operation in the nodes when corner data is selected. In the case now studied, “cornerData”
                should be “True” and “aveNodes” should be 0, which means that the actual value is taken, neither the
                average nor the max or min in the node. In addition, there is also another important input parameter that
                will be maintained with the default value this time, which is “coordsys”. The default value is the element
                reference frame; and it will be explained in the following paragraphs the reason why it is not important
                where to represent the forces at first.

                Taking each of the points of the box, the same procedure is carried out. First, all the results for all
                the nodes that form the element where the box point is are retrieved. These results are represented in
                the element reference frame of the element to which they are. This means that if a node is part of 5
                different elements, there would be 5 different values represented in 5 different reference frames.
                Therefore, all the force values are transformed in order to be represented in the element system of the
                element where the box point is located. This is in part done in order to be able to make the average
                between the values of a same node, which is the following step.

                Once the 4 or 3 values for the nodes (depending if the element where the box point is, is a QUAD or a
                TRIA element) are obtained, the next step is to use a bilinear interpolation to the box point from the
                node locations, using the forces just obtained to get the actual value in the selected point. This
                interpolation can be seen in module ARBilinearInterpolation.

            -   NO CORNER DATA:

                 In this case, the results in the result files are retrieved in the centroid of each element. As before,
                 this will be asked in the launcher file by selecting “CENTER”. It is important to remind that the results
                 obtained using this data may not be as precise as the ones using corner data. This can be due to the fact
                 that in the procedure that will be now explained, the data from the centroids are used in order to get
                 the interpolated corresponding data in the corners; whereas in the corner data case, these values are
                 already known directly, saving an “approximation”.

                 In the process to get results, as before, the function “get_result_ndarray” is used. However, it is now
                 left with the default inputs. This means that the results will be obtained in the centroid and in element
                 reference frame.

                 Thus, the same methodology is now followed for each of the points of the box. As in the corner data case,
                 the final interpolation must be done between the corners of the element where the point is and the actual
                 point location. Nevertheless, unlike previously, where the corner data was directly retrieved, now the
                 results in the corner must be done by an average between the adjacent elements. Therefore, all the results
                 from the elements that are adjacent to a node of interest would be gotten from the results dictionary,
                 transformed to the box point element reference frame and then a linear mean would be done in order to
                 obtain the corresponding result data in the node. Next, the data for each of the nodes of the element
                 where the box point is located would be used in order to obtain the flux in the point itself.

                 Finally, all the results should be transformed again into the material system of the element where the
                 bolt is pierced.

        Additional information:

        There are several checks that are done in order to calculate only the bolts that are correctly created:

            -   The bolt must be connected to a minimum of 2 plates. This means that all the fasteners of the bolt must
                connect 2 plates. None of the fastener nodes can be free.

            -   As the study is made for each of the plates connected to the bolt, the following data must be filled:
                Intersection point, distance to edge and normal vector to the plate.

            -   The element where the bolt is pierced must be surrounded by more coplanar elements.

            -   The forces either in the used elements or in their corners must be in the results dictionary in order to
                carry out the analysis.


        """

        t11 = time()

        corner_data = corner

        # Specify supported elements in plates
        supported_elements = ["CQUAD4", "CTRIA3"]

        # First, get domain of all CTRIA and CQUAD in model
        domain = [element for element in model.get_elements() if
                  element.TypeElement in supported_elements]

        # Watch out the case where the bolt is not connected to 2 plates. (Error)
        if len(self.Plates) < 2:
            N2PLog.Error.E505(self)
            return None


        # FOR EVERY PLATE IN THE BOLT
        for plate in self.Plates:

            # Check if plate intersection and normal are defined
            if plate.IntersectionPoint is None:
                N2PLog.Warning.W513(self)
                continue

            if plate.Normal is None:
                N2PLog.Warning.W514(self)
                continue

            if plate.DistanceToEdge is None:
                N2PLog.Warning.W515(self)
                continue

            if len(plate.Elements) == 0:
                N2PLog.Warning.W516(self)
                continue

            t1=time()
            ############################################################################################################

            # 1. GET BOUNDARY BOX

            ############################################################################################################

            # Select material factor depending on the plate type.
            if plate.Elements[0].Property.PropertyType == "PCOMP":
                material_factor = material_factor_list[1]
            else:
                material_factor = material_factor_list[0]

            # If the diameter was not provided in the input file, we use the diameter of the first element. (This only
            # happens in the CFAST case because in the other cases the diameter must be defined by the user and not via the property.)
            if self.TypeFasteners == "CFAST" and self.Diameter is None:
                self.Diameter = self.Elements1D[0].Property.D

            if self.Diameter is None:
                N2PLog.Error.E506(self)
                return None

            a = 0.4 * area_factor * material_factor * self.Diameter
            box_semidiag = (2 ** 0.5) * (a / 2)
            bolt_element = model.get_elements((plate.Elements[0].Element.ID, 0))
            intersection = np.array(plate.IntersectionPoint)

            plate.BoxDimension = a

            ### BOX AXES DEFINITION
            # Xbox is defined as the vector connecting the nodes that form the smallest angle with material x axis

            ###########################################################################################################
            xmat = np.array(bolt_element.MaterialSystemArray[0:3])

            # X box points
            xbox = xmat
            # Axis Z is the normal no the element
            zbox = np.array(bolt_element.ElemSystemArray[6:9])
            ybox = np.cross(zbox, xbox)

            BoxSystem = [xbox[0], xbox[1], xbox[2], ybox[0], ybox[1], zbox[2], zbox[0], zbox[1], zbox[2]]

            plate.BoxSystem = BoxSystem

            # BOUNDARY BOX
            # Box points coordinates in element system

            ax = np.array([[-1.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0]])
            ay = np.array([[ 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, -1.0, 0.0]])

            # Boundary box points
            box_points = intersection + (a / 2) * np.matmul(ax.transpose(), xbox.reshape((1, 3))) + (a / 2) * np.matmul(
                ay.transpose(), ybox.reshape((1, 3)))
            box_points = {i + 1: box_points[i] for i in range(len(box_points))}

            ############################################################################################################

            # 2. IDENTIFY ELEMENT THAT CONTAINS EACH BOUNDARY BOX POINT

            ############################################################################################################
            # For each point in box points we should identify the element in which they are contained
            box_points_found = {key: False for key in box_points.keys()}
            box_points_elements = {key: None for key in box_points.keys()}

            # We will cycle through concentric rings of adjacent elements starting from the element of the bolt.
            candidate_elements = [bolt_element]
            seen_candidates = []

            # Initialize minimum distances
            min_distance_to_candidate_elements = 0

            # 1st loop. Keep going while there are elements to be found
            iterations = 0
            while not all(box_points_found.values()):
                iterations += 1

                # Set max iterations to not fall in inf loop
                if iterations > max_iter:
                    N2PLog.Error.E507(self)
                    return 0

                # Adjacent elements will be evaluated until the distance from the bolt to them is greater than the
                # semidiagonal of the box. After this it is assured that no more points will be found far away and it
                # does not make sense to keep looking. The exception is when the element size is greater than the
                # box. In this case the distance condition alone fails, that is why while iterations are smaller than
                # 2 it is ignored. In the case that some points are still be assigned, we can conclude that they lie
                # outside the edge of the plate and should be projected

                # STEP 1. LOCATE ALL POINTS WITHIN FREE EDGES
                if min_distance_to_candidate_elements < box_semidiag or iterations < 3:
                    # 2nd loop. Loop through box points
                    for point in box_points.keys():
                        # Skip points that have already been found
                        if not box_points_found.get(point):
                            # 3rd loop. Loop through candidate elements.

                            for check_elem in candidate_elements:

                                # Vertices of the element to check
                                vertices = [node.GlobalCoords for node in check_elem.Nodes]

                                # Check if element is inside the element
                                normal = np.cross(np.subtract(vertices[1], vertices[0]),
                                                  np.subtract(vertices[2], vertices[0]))
                                normal = normal/np.linalg.norm(normal)
                                point_plane_distance = abs(np.dot(normal, box_points.get(point)) -np.dot(normal, vertices[0]))
                                if point_plane_distance > box_tol:
                                    continue

                                # Check if the point is inside the convex hull of the element
                                inside = [False] * len(vertices)
                                for i in range(len(vertices)):
                                    edge_start = vertices[i]
                                    edge_end = vertices[(i + 1) % len(vertices)]
                                    edge_vector = np.subtract(edge_end, edge_start)
                                    to_point_vector = np.subtract(box_points.get(point), edge_start)
                                    cross_product = np.cross(edge_vector, to_point_vector)
                                    if np.dot(normal, cross_product) > 0:
                                        inside[i] = True

                                # If all conditions are not met, the element is inside the convex hull
                                if all(inside):
                                    # When this condition is reached for all box point, the while loop is exited.
                                    box_points_found[point] = True
                                    box_points_elements[point] = check_elem

                    # Update candidate element list
                    seen_candidates = list(set(seen_candidates + candidate_elements))

                    elements_adjacents = [elements for elements in model.get_elements_adjacent(candidate_elements,  domain=domain)
                                          if ( isinstance(elements, N2PElement) and elements.TypeElement in supported_elements)]

                    candidate_elements = list(set(elements_adjacents).difference(set(seen_candidates)))

                    # Check in case there are no adjacent elements where to look for point locations.
                    if len(candidate_elements) == 0:
                        N2PLog.Error.E508(self)
                        return None

                    candidate_elements_nodes = np.array(list(set([node.GlobalCoords for e in candidate_elements for node in e.Nodes])))

                    min_distance_to_candidate_elements = np.min( np.linalg.norm(intersection.transpose() - candidate_elements_nodes, axis=1))

                # STEP 2. LOCATE ALL POINTS OUTSIDE OF FREE EDGES OR T-EDGES.
                else:

                    # We are only interested in the plane where the bolt is. So a T-edge is considered also as a free edge.
                    elements_in_face = model.get_elements_by_face(bolt_element, domain = seen_candidates)
                    free_edges = model.get_free_edges(domain=elements_in_face)
                    # 2nd loop. Loop through box points
                    for point in box_points.keys():
                        # Skip points that have already been found
                        if not box_points_found.get(point):

                            A = np.array([[segment[1].X, segment[1].Y, segment[1].Z] for segment in free_edges])
                            B = np.array([[segment[2].X, segment[2].Y, segment[2].Z] for segment in free_edges])

                            # Calculate the vectors for each segment
                            segment_vector = B - A
                            point_vector = box_points.get(point) - A

                            # Calculate the projection of point_vector onto segment_vector
                            projection = np.sum(point_vector * segment_vector, axis=1) / np.sum(
                                segment_vector * segment_vector, axis=1)

                            projected_point = []
                            for i in range(A.shape[0]):
                                if projection[i] < 0 + np.linalg.norm(segment_vector)*proj_tol:
                                    projected_point.append(A[i])
                                elif projection[i] > 1 -np.linalg.norm(segment_vector)*proj_tol :
                                    projected_point.append(B[i])
                                else:
                                    projected_point.append(A[i] + projection[i] * segment_vector[i])

                            # Calculate the projection of point_vector onto segment_vector
                            distance_to_projected_point = [np.linalg.norm(box_points.get(point) - proj_point) for
                                                           proj_point in projected_point]

                            # Keep the closest projected point, discard the rest
                            index = distance_to_projected_point.index(np.nanmin(distance_to_projected_point))
                            box_points_elements[point] = free_edges[index][0]
                            box_points[point] = projected_point[index]
                            box_points_found[point] = True

            # At this stage all box points are placed and their container elements are identified
            plate.BoxPoints = box_points

            ##################################################################################

            # WHEN THERE IS CORNER DATA.

            if corner_data:
                result_dict = {}
                element_nodal = model.elementnodal()

                box_points_forces = {point: None for point in box_points.keys()}
                # Get forces and moments in each box points
                for point in box_points.keys():
                    point_element = box_points_elements.get(point)

                    element_system_box_point = point_element.ElemSystemArray
                    element_forces = []
                    result_for_point = {loadcase: None for loadcase in results.keys()}

                    result_for_node = {node.ID: None for node in point_element.Nodes}

                    for node in point_element.Nodes:

                        unsew_node = [us_node for us_node in element_nodal.keys() if
                                      node.ID == element_nodal.get(us_node)[1]]

                        unsew_element_ids = [element_nodal.get(us_node)[2] for us_node in element_nodal.keys() if
                                             node.ID == element_nodal.get(us_node)[1]]
                        # Elements of the node
                        unsew_element_2 = [element for element in node.Connectivity if (isinstance(element, N2PElement)
                                                                                        and element.TypeElement in supported_elements)
                                   ]

                        unsew_element_2_ids = [element.ID for element in unsew_element_2]
                        index_no_element = [i for i, element in enumerate(unsew_element_ids) if
                                            element not in unsew_element_2_ids]
                        for i in reversed(index_no_element):
                            del unsew_element_ids[i]
                            del unsew_node[i]
                        unsew_element = sorted(unsew_element_2, key=lambda x: unsew_element_ids.index(x.ID))

                        # Element Systems for the elements.
                        element_frames = [element.ElemSystemArray for element in unsew_element]

                        # It looks like Altair ignores elements that are not coplanar when obtaining the forces in the box points.
                        elements_adjacents = [elements for elements in
                                              model.get_elements_adjacent(point_element, domain=domain)
                                              if (isinstance(elements,
                                                             N2PElement) and elements.TypeElement in supported_elements)]

                        elements_adjacents_bolt = [elements for elements in
                                                   model.get_elements_adjacent(bolt_element, domain=domain)
                                                   if (isinstance(elements,
                                                                  N2PElement) and elements.TypeElement in supported_elements)]

                        elements_in_face = model.get_elements_by_face(bolt_element,
                                                                      domain=elements_adjacents + elements_adjacents_bolt,
                                                                      tolerance_angle=15)

                        eliminate_index = [i for i, element in enumerate(unsew_element) if
                                           element not in elements_in_face]

                        # Eliminate elements from lists using the stored indexes.
                        for index in reversed(eliminate_index):
                            del element_frames[index]
                            del unsew_node[index]
                            del unsew_element[index]
                            del unsew_element_ids[index]


                        result_for_node_lc = {loadcase: None for loadcase in results.keys()}

                        # Obtain results in the nodes for each of the load cases.

                        for lc_id, result in results.items():

                            # Results call in corner.

                            fx_corner = result.get("FX CORNER")
                            fy_corner = result.get("FY CORNER")
                            fxy_corner = result.get("FXY CORNER")
                            mx_corner = result.get("MX CORNER")
                            my_corner = result.get("MY CORNER")
                            mxy_corner = result.get("MXY CORNER")

                            element_forces = []
                            unsew_nodes_forces = [[fx_corner[nodes], fy_corner[nodes], fxy_corner[nodes], mx_corner[nodes], my_corner[nodes], mxy_corner[nodes]]
                                                  for nodes in unsew_node]

                            # Rotate from Element System where the forces are obtained to the Element System of the point element.
                            for forces in unsew_nodes_forces:
                                if len(forces) != 6:
                                    N2PLog.Error.E509(self)
                                    return None
                            unsew_nodes_forces_rotated = [rotate_tensor2D(
                                from_system=element_frames[position],
                                to_system=element_system_box_point,
                                plane_normal=element_system_box_point[6:9],
                                tensor=unsew_nodes_forces[position]) for position in range(len(unsew_node))]

                            # Obtain the mean of the forces in the node
                            mean_forces = np.mean(unsew_nodes_forces_rotated, axis=0)

                            result_for_node_lc[lc_id]= mean_forces

                        result_for_node[node.ID] = result_for_node_lc

                    keys_first_elem = set(result_for_node[next(iter(result_for_node))].keys())
                    element_forces = {key_dic_nodes: [] for key_dic_nodes in keys_first_elem}
                    for key_dic_nodes in keys_first_elem:
                        for element in result_for_node.values():
                            if key_dic_nodes in element:
                                element_forces[key_dic_nodes].append(element[key_dic_nodes])
                            else:
                                element_forces[key_dic_nodes].append(None)

                    for lc_id, result in element_forces.items():

                        # INTERPOLATION FROM CORNERS TO BOX POINT
                        corner_coordinates_global = np.array([node.GlobalCoords for node in point_element.Nodes])
                        centroid = point_element.Centroid
                        corner_coord_elem, point_coord_elem = transformation_for_interpolation(
                            corner_coordinates_global, centroid,
                            point=box_points.get(point),
                            element_system=element_system_box_point)

                        interpolated_forces = interpolation(point_coord_elem, corner_coord_elem, result)

                        # Forces are rotated from Global System to Element System of the element where the box point is located.
                        interpolated_forces_rotated = rotate_tensor2D(
                            from_system=element_system_box_point,
                            to_system=bolt_element.MaterialSystemArray,
                            plane_normal=element_system_box_point[6:9],
                            tensor=interpolated_forces)

                        result_for_point[lc_id] = interpolated_forces_rotated

                    box_points_forces[point] = result_for_point

                for ext_key, int_dict in box_points_forces.items():
                    for int_key, value_dic in int_dict.items():
                        if int_key not in result_dict:
                            result_dict[int_key] = {}
                        result_dict[int_key][ext_key] = value_dic

            # WHENE THERE IS NO CORNER DATA.

            else:
                result_dict = {}
                # Get forces and moments in each box points
                box_points_forces = {point: None for point in box_points.keys()}
                for point in box_points.keys():

                    point_element = box_points_elements.get(point)
                    element_system_box_point = point_element.ElemSystemArray
                    neighbor_elements = [elem for elem in model.get_elements_adjacent(cells=point_element) if
                                         (isinstance(elem, N2PElement) and elem.TypeElement in supported_elements)]

                    # See if the elements are coplanar.

                    elements_adjacents_bolt = [elements for elements in
                                               model.get_elements_adjacent(bolt_element, domain=domain)
                                               if (isinstance(elements,
                                                              N2PElement) and elements.TypeElement in supported_elements)]

                    # It looks like Altair ignores elements that are not coplanar when obtaining the forces in the box points.
                    elements_in_face_prev = model.get_elements_by_face(bolt_element, domain=neighbor_elements + elements_adjacents_bolt) \
                                          + model.get_elements_by_face(point_element, domain=neighbor_elements + elements_adjacents_bolt)

                    elements_in_face = [element for element in neighbor_elements if
                                        element in elements_in_face_prev]

                    neighbor_elements = elements_in_face

                    result_for_point = {loadcase: None for loadcase in results.keys()}
                    for lc_id, result in results.items():

                        # Results call in centroid

                        fx = result.get("FX")
                        fy = result.get("FY")
                        fxy = result.get("FXY")
                        mx = result.get("MX")
                        my = result.get("MY")
                        mxy = result.get("MXY")

                        element_forces = []
                        for corner in point_element.Nodes:
                            node_forces = []
                            for neighbor in neighbor_elements:
                                if corner in neighbor.Nodes:
                                    elem_system_neighbor = neighbor.ElemSystemArray  # Element system from neighbour.
                                    i = neighbor.InternalID
                                    neighbor_forces = [fx[i], fy[i], fxy[i], mx[i], my[i], mxy[i]]

                                    if len(neighbor_forces) != 6:
                                        N2PLog.Error.E509(self)
                                        return None

                                    # Rotate from Element System where the forces are obtained to the Element System of the point element.
                                    neighbor_forces = rotate_tensor2D(
                                        from_system=elem_system_neighbor,
                                        to_system=element_system_box_point,
                                        plane_normal=element_system_box_point[6:9],
                                        tensor=neighbor_forces)

                                    node_forces.append(neighbor_forces)

                            node_forces = np.array(node_forces)
                            # Average of nodes across the neighbor elements
                            average_node_forces = np.mean(node_forces, axis=0)
                            element_forces.append(average_node_forces.tolist())

                        element_forces = np.array(element_forces)

                        # INTERPOLATION FROM CORNERS TO BOX POINT
                        corner_coordinates_global = np.array([node.GlobalCoords for node in point_element.Nodes])
                        centroid = point_element.Centroid
                        corner_coord_elem, point_coord_elem = transformation_for_interpolation(
                            corner_coordinates_global, centroid,
                            point=box_points.get(point),
                            element_system=element_system_box_point)

                        interpolated_forces = interpolation(point_coord_elem, corner_coord_elem, element_forces)

                        # Forces are rotated from Global System to Element System of the element where the box point is located.
                        interpolated_forces_rotated = rotate_tensor2D(
                            from_system=element_system_box_point,
                            to_system=bolt_element.MaterialSystemArray,
                            plane_normal=element_system_box_point[6:9],
                            tensor=interpolated_forces)

                        result_for_point[lc_id] = interpolated_forces_rotated

                    box_points_forces[point] = result_for_point

                for ext_key, int_dict in box_points_forces.items():
                    for int_key, value_dic in int_dict.items():
                        if int_key not in result_dict:
                            result_dict[int_key] = {}
                        result_dict[int_key][ext_key] = value_dic

            plate.BoxFluxes = result_dict

            # At this point, for each load case every set of forces and moments is obtained for each box point

            ########################################################################################################

            # 4. FASTPPH METHOD

            ########################################################################################################

            for lc_id, fluxes in result_dict.items():

                # Calculate fluxes
                side = {1: [1, 2, 3],
                        2: [3, 4, 5],
                        3: [5, 6, 7],
                        4: [7, 8, 1]}

                # X FLUXES
                nx2 = np.array([fluxes.get(point)[0] for point in side[2]]).mean()
                nx4 = np.array([fluxes.get(point)[0] for point in side[4]]).mean()
                nx_bypass = min((nx2, nx4), key=abs)
                nx_total = max((nx2, nx4), key=abs)

                mx2 = np.array([fluxes.get(point)[3] for point in side[2]]).mean()
                mx4 = np.array([fluxes.get(point)[3] for point in side[4]]).mean()
                # Added a minus sign to the expression in order to coincide with the results obtained by FastPPh in Hypermesh.
                mx_total = -0.5 * (mx2 + mx4)

                # Y FLUXES
                ny1 = np.array([fluxes.get(point)[1] for point in side[1]]).mean()
                ny3 = np.array([fluxes.get(point)[1] for point in side[3]]).mean()
                ny_bypass = min((ny1, ny3), key=abs)
                ny_total = max((ny1, ny3), key=abs)

                my1 = np.array([fluxes.get(point)[4] for point in side[1]]).mean()
                my3 = np.array([fluxes.get(point)[4] for point in side[3]]).mean()
                # Added a minus sign to the expression in order to coincide with the results obtained by FastPPh in Hypermesh.
                my_total = -0.5 * (my1 + my3)

                #  XY FLUXES
                nxy1 = np.array([fluxes.get(point)[2] for point in side[1]]).mean()
                nxy2 = np.array([fluxes.get(point)[2] for point in side[2]]).mean()
                nxy3 = np.array([fluxes.get(point)[2] for point in side[3]]).mean()
                nxy4 = np.array([fluxes.get(point)[2] for point in side[4]]).mean()
                nxy_bypass = min((nxy1, nxy2, nxy3, nxy4), key=abs)
                nxy_total = max((nxy1, nxy2, nxy3, nxy4), key=abs)

                mxy1 = np.array([fluxes.get(point)[5] for point in side[1]]).mean()
                mxy2 = np.array([fluxes.get(point)[5] for point in side[2]]).mean()
                mxy3 = np.array([fluxes.get(point)[5] for point in side[3]]).mean()
                mxy4 = np.array([fluxes.get(point)[5] for point in side[4]]).mean()
                # Added a minus sign to the expression in order to coincide with the results obtained by FastPPh in Hypermesh.
                mxy_total = -0.25 * (mxy1 + mxy2 + mxy3 + mxy4)

                ########################################################################################################

                # 5. ROTATE BYPASS TENSORS

                ########################################################################################################

                MaterialSystem = bolt_element.MaterialSystemArray

                # It is given a list of tensor components. The function rotate_tensor_2D internally reshapes it properly.
                tensor_to_rotate = [nx_bypass, ny_bypass, nxy_bypass,
                                    nx_total, ny_total, nxy_total,
                                    mx_total, my_total, mxy_total]
                for value in tensor_to_rotate:
                    if not isinstance(value, float):
                        N2PLog.Error.E509(self)
                        return None

                rotated_tensor = rotate_tensor2D(from_system=BoxSystem,
                                    to_system=MaterialSystem,
                                    plane_normal=MaterialSystem[6:9],
                                    tensor=tensor_to_rotate)

                # ASSIGN FINAL RESULTS

                plate.NxBypass[lc_id] = rotated_tensor[0]
                plate.NyBypass[lc_id] = rotated_tensor[1]
                plate.NxyBypass[lc_id] = rotated_tensor[2]

                plate.NxTotal[lc_id] = rotated_tensor[3]
                plate.NyTotal[lc_id] = rotated_tensor[4]
                plate.NxyTotal[lc_id] = rotated_tensor[5]

                plate.MxTotal[lc_id] = rotated_tensor[6]
                plate.MyTotal[lc_id] = rotated_tensor[7]
                plate.MxyTotal[lc_id] = rotated_tensor[8]

                # Added a minus sign to the expression in order to coincide with the results obtained by FastPPh in Hypermesh.
                plate.MxyTotal[lc_id] = -0.25 * (mxy1 + mxy2 + mxy3 + mxy4)

                # Calculate the max and min bypass principals, as well as the load angle (in degrees).

                plate.BypassMaxPpal[lc_id] = (plate.NxBypass[lc_id] + plate.NyBypass[lc_id]) / 2 + (
                        ((plate.NxBypass[lc_id] - plate.NyBypass[lc_id]) / 2) ** 2 + plate.NxyBypass[
                    lc_id] ** 2) ** 0.5
                plate.BypassMinPpal[lc_id] = (plate.NxBypass[lc_id] + plate.NyBypass[lc_id]) / 2 - (
                        ((plate.NxBypass[lc_id] - plate.NyBypass[lc_id]) / 2) ** 2 + plate.NxyBypass[
                    lc_id] ** 2) ** 0.5


        t7 = time()
        # print("time for bolt {}: {}".format(self.ID, t7-t11))
        return self

    def export_forces_csv_fastpph(self, path_file: str, analysis_name: str, results: dict) -> None:
        """Method which takes an ARBolt element and a directory path in order to export the corresponding data for
        forces and bypasses in the plates in a csv file. The output format is set to be almost the same as the one that
        Hypermesh exports using FastPPH. The csv file is created in the path file if it does not exist, and the new
        information is added at the end if the csv file already exists.

        Args:
            path_file: str
            analysis_name: str with name of the analysis
            results: dict

        Returns:
            Output csv file

        Calling example:

                    bolt.export_forces_csv_fastpph(path_file = output_path_file, analysis_name = analysis_name, results = results)

        Information retrieved and added to the csv file:

        •	Element ID: ID of the plate that is been pierced.

        •	Connector 1 ID: fastener 1 connected to the plate.

        •	Connector 2 ID: fastener 2 connected to the plate. If only one fastener is pierced to the plate, this attribute
            will be empty.

        •	Load Case: ID of the load case that is been analysed.

        •	Analysis Name: name of the analysis.

        •	Box Dimension: dimension “a” of the box used for the calculation of fluxes.

        •	Box System: reference frame defined by the box sides. (should coincide with the material reference system of
            the plate)

        •	Pierced Location: location in global coordinates of the point where the fastener/s is/are pierced.

        •	FX, FY and FZ Altair: 1D forces of the fastener/s expressed in the coordinate system and in the same way as
            Altair would do, summing up the contribution of both of the fastener’s forces in the case there are two of them.

        •	Fx, Fy and Fz Connector 1: 1D forces of fastener 1 expressed in the local reference frame.

        •	Fx, Fy and Fz Connector 2: 1D forces of fastener 2 expressed in the local reference frame.

        •	MaxFz: maximum axial force. It will be 0 if it is in compression.

        •	p1, p2, p3, …, p8: location in global coordinates of the points that define the box.

        •	Fxx, Fyy and Fxy p: fluxes calculated in each of the points of the box.

        •	Mxx, Myy and Mxy p: moments calculated in each of the points of the box.

        •	Nx, Ny and Nxy Bypass: bypass loads obtained in the plate.

        •	Nx, Ny and Nxy Total: total loads obtained in the plate.

        •	Mx, My and Mxy Total: total moments obtained in the plate.


        """

        # Definition of the top headline of the csv file.
        headline = ["Element ID", "Connector 1 ID", "Connector 2 ID", "Load Case", "Analysis Name", "Box Dimension", "Box System",
                    "Pierced Location", "FX Altair", "FY Altair", "FZ Altair", "Fx Connector 1", "Fy Connector 1", "Fz Connector 1",
                    "Fx Connector 2","Fy Connector 2",
                    "Fz Connector 2", "MaxFz", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "Fxx p1", "Fxx p2",
                    "Fxx p3", "Fxx p4", "Fxx p5", "Fxx p6", "Fxx p7", "Fxx p8", "Fyy p1", "Fyy p2", "Fyy p3", "Fyy p4",
                    "Fyy p5", "Fyy p6", "Fyy p7", "Fyy p8", "Fxy p1", "Fxy p2", "Fxy p3", "Fxy p4", "Fxy p5", "Fxy p6",
                    "Fxy p7", "Fxy p8", "Mxx p1", "Mxx p2", "Mxx p3", "Mxx p4", "Mxx p5", "Mxx p6", "Mxx p7", "Mxx p8",
                    "Myy p1", "Myy p2", "Myy p3", "Myy p4", "Myy p5", "Myy p6", "Myy p7", "Myy p8", "Mxy p1", "Mxy p2",
                    "Mxy p3", "Mxy p4", "Mxy p5", "Mxy p6", "Mxy p7", "Mxy p8", "Nx Bypass", "Nx Total", "Ny Bypass",
                    "Ny Total", "Nxy Bypass", "Nxy Total", "Mx Total", "My Total", "Mxy Total"]

        path_file_new = "{}\\{}_fastpph.csv".format(path_file, analysis_name)

        with open(path_file_new, 'a+', newline='') as file_csv:

            writer_csv = csv.writer(file_csv)

            if file_csv.tell() == 0:  # If the file is non-existent, the headline is written, if it already exists, if keeps adding the new bolts studied.
                writer_csv.writerow(headline)

            for plate in self.Plates:

                # If we have several elements (more than one loadcases), it iterates throughout all the different loadcases.
                for loadcase, result in results.items():
                    data = [plate.ElementIDs[0], plate.Element1DIDsJoined[0], plate.Element1DIDsJoined[1], loadcase, analysis_name,
                        plate.BoxDimension, plate.BoxSystem, plate.IntersectionPoint, plate.F_1D_Altair[loadcase][0], plate.F_1D_Altair[loadcase][1],
                        plate.F_1D_Altair[loadcase][2], plate.F_1D_PlatesOrganisation[loadcase][0][0],
                        plate.F_1D_PlatesOrganisation[loadcase][0][1], plate.F_1D_PlatesOrganisation[loadcase][0][2],
                        plate.F_1D_PlatesOrganisation[loadcase][1][0], plate.F_1D_PlatesOrganisation[loadcase][1][1],
                        plate.F_1D_PlatesOrganisation[loadcase][1][2], self.FZmax[loadcase], plate.BoxPoints[1],
                        plate.BoxPoints[2], plate.BoxPoints[3], plate.BoxPoints[4], plate.BoxPoints[5],
                        plate.BoxPoints[6], plate.BoxPoints[7], plate.BoxPoints[8], plate.BoxFluxes[loadcase][1][0], plate.BoxFluxes[loadcase][2][0],
                        plate.BoxFluxes[loadcase][3][0], plate.BoxFluxes[loadcase][4][0], plate.BoxFluxes[loadcase][5][0], plate.BoxFluxes[loadcase][6][0],
                        plate.BoxFluxes[loadcase][7][0], plate.BoxFluxes[loadcase][8][0], plate.BoxFluxes[loadcase][1][1], plate.BoxFluxes[loadcase][2][1],
                        plate.BoxFluxes[loadcase][3][1], plate.BoxFluxes[loadcase][4][1], plate.BoxFluxes[loadcase][5][1], plate.BoxFluxes[loadcase][6][1],
                        plate.BoxFluxes[loadcase][7][1], plate.BoxFluxes[loadcase][8][1], plate.BoxFluxes[loadcase][1][2], plate.BoxFluxes[loadcase][2][2],
                        plate.BoxFluxes[loadcase][3][2], plate.BoxFluxes[loadcase][4][2], plate.BoxFluxes[loadcase][5][2], plate.BoxFluxes[loadcase][6][2],
                        plate.BoxFluxes[loadcase][7][2], plate.BoxFluxes[loadcase][8][2], plate.BoxFluxes[loadcase][1][3], plate.BoxFluxes[loadcase][2][3],
                        plate.BoxFluxes[loadcase][3][3], plate.BoxFluxes[loadcase][4][3], plate.BoxFluxes[loadcase][5][3], plate.BoxFluxes[loadcase][6][3],
                        plate.BoxFluxes[loadcase][7][3], plate.BoxFluxes[loadcase][8][3], plate.BoxFluxes[loadcase][1][4], plate.BoxFluxes[loadcase][2][4],
                        plate.BoxFluxes[loadcase][3][4], plate.BoxFluxes[loadcase][4][4], plate.BoxFluxes[loadcase][5][4], plate.BoxFluxes[loadcase][6][4],
                        plate.BoxFluxes[loadcase][7][4], plate.BoxFluxes[loadcase][8][4], plate.BoxFluxes[loadcase][1][5], plate.BoxFluxes[loadcase][2][5],
                        plate.BoxFluxes[loadcase][3][5], plate.BoxFluxes[loadcase][4][5], plate.BoxFluxes[loadcase][5][5], plate.BoxFluxes[loadcase][6][5],
                        plate.BoxFluxes[loadcase][7][5], plate.BoxFluxes[loadcase][8][5], plate.NxBypass[loadcase],
                        plate.NxTotal[loadcase], plate.NyBypass[loadcase], plate.NyTotal[loadcase], plate.NxyBypass[loadcase],
                        plate.NxyTotal[loadcase], plate.MxTotal[loadcase], plate.MyTotal[loadcase], plate.MxyTotal[loadcase]]
                    writer_csv.writerow(data)

    def serialize(self):
        '''
        Serialize method substitutes all N2P objects by integer or tuple IDs so that ARBolt can be serialized by pickle.
        ARElement1D and ARPlate serialize methods all called.

        Returns: self
        '''

        if not self.serialized:
            for element1D in self.Elements1D:
                element1D.serialize()

            for plate in self.Plates:
                plate.serialize()

            self.serialized = True

        return self

    def deserialize(self, model: N2PModelContent):
        '''
        Deserialize method rebuilds ARBolt using the model and the IDs left by the serialize method.
        ARElement1D and ARPlate deserialize methods all called.

        Returns: self
        '''
        if self.serialized:
            for element1D in self.Elements1D:
                element1D.deserialize(model)

            for plate in self.Plates:
                plate.deserialize(model)

            self.serialized = False

        return self

    ##################################################################################################
    ######################################### STATIC METHODS #########################################
    ##################################################################################################
    @staticmethod
    def merge_3_bolts(bolt_A, new_element1D: AR1DElement, bolt_B):
        merged_bolt = ARBolt(bolt_A.ID)

        merged_bolt.Elements1D = bolt_A.Elements1D + [new_element1D] + bolt_B.Elements1D
        merged_bolt.Plates = bolt_A.Plates + bolt_B.Plates
        merged_bolt.Elements1DIDs = bolt_A.Elements1DIDs + [new_element1D.ID] + bolt_B.Elements1DIDs

        return merged_bolt
