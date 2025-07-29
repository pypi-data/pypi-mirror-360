import NaxToPy as N2P
from NaxToPy.Core import N2PModelContent
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PConnector import N2PConnector
from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToPy.Core.Classes.N2PNastranInputData import * 
from NaxToPy.Core.Classes.N2PAbaqusInputData import * 
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARBolt import ARBolt
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.AR1DElement import AR1DElement
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARPlate import ARPlate
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARPlateElements import ARPlateElements
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Functions.ARAuxiliarFunctions import point_in_element, equal_points, same_direction
import numpy as np


def get_bolts(model: N2PModelContent) -> list[ARBolt]:
    """ This function takes as input a NaxToPy model read from a mesh file, processes all elements 1D along with their
    properties and attached plates, and groups them into ARBolt instances. It returns the list of all bolts found in
    the model. Note that the order of the elements 1D and plates inside the ARBolt instances may be incorrect for
    bolts of more than 3 elements 1D.

    There are several types of elements 1D that can be processed: CFAST, CBUSH, CBAR; which can be at the same time (in
    the case of CBAR and CBUSH) connected to different connectors as RBE3 or RBE2.

    Args:
        model: N2PModelContent

    Returns:
        list[ARBolt]

    Calling example:

            bolts = get_bolts(model=model1)

    Additional information:

    •	In order to understand the procedure used in order to get the bolts, the following explanation is shown. Two or more
        fasteners are considered part of the same bolt when their intersection with the same plate coincides and they have
        an almost same 1D direction. In the cases of CFAST, CBUSH or CBAR elements when they are directly connected to the
        mesh, it is pretty straight forward to do this; as the nodes defining the fasteners are the same points as the
        intersection points with the corresponding plates.

    •	However, the case in which the fasteners are joined to a connector and the connector is the one which connects the
        mesh is different. In this case, the projection along the axial direction of the 1D element is done onto the mesh,
        obtaining this way the hypothetic intersection of the fastener with the plate. Thus, in this case, the verification
        to create the bolt containing several fasteners is made using these points and not the nodes themselves.


    """

    if model._N2PModelContent__vzmodel.NastranInfoInputFileData is not None: 
        class ListaCards:
            def __init__(self, lista_cards: list[N2PCard]):
                self._lista_cards = lista_cards

            def __getitem__(self, index):
                if isinstance(index, slice):
                    item = self._lista_cards[index]
                    return [CONSTRUCTDICT[i.CardType.ToString()](i) for i in item]
                else:
                    item = self._lista_cards[index]
                    return CONSTRUCTDICT[item.CardType.ToString()](item)

        CONSTRUCTDICT = construct_dict() 
        
        cslistbulkdatacards = list(model._N2PModelContent__vzmodel.NastranInfoInputFileData.ListBulkDataCards)
        cards = list(ListaCards(cslistbulkdatacards))
    else: 
        N2PLog.Error.E527() 

    # Create Bolt list
    ARBolt_list = []
    supported_elements = ["CQUAD4", "CTRIA3"]
    supported_connectors = ["RBE3", "RBE2"]
    all_elements = model.get_elements()

    # Extract Elements, Properties and materials

    CFAST_list = [element for element in all_elements if element.TypeElement == "CFAST"]  # List of CFAST N2PElements

    CBUSH_list = [element for element in all_elements if element.TypeElement == "CBUSH"]  # List of CBUSH N2PElements

    CBAR_list = [element for element in all_elements if element.TypeElement == "CBAR"]  # List of CBAR N2PElements

    fasteners_list = CBUSH_list + CFAST_list + CBAR_list  # All fasteners

    bushes_special = [bush for bush in CBUSH_list if
                      bush.NodesIds[0] == bush.NodesIds[1]]  # CBUSHES defined with coincident nodes.

    for bush in bushes_special:
        N2P.N2PLog.Warning.W501(bush)

    fasteners_list = [fastener for fastener in fasteners_list if
                      fastener not in bushes_special]  # Update of all fasteners without considering the list above.

    # Auxiliar set and dictionary
    seen_nodes = set()
    node_to_bolt_dict = dict()
    seen_points = []
    point_to_bolt_dict = dict()

    ###################################################################################
    ### MAIN LOOP
    ##################################################################################

    plate_id_iterator = 0
    bolt_id_iterator = 0

    for fastener in fasteners_list:
        plate_id_iterator += 2
        has_connector = False
        connectors_joined = []
        connectors_joined_ids = []

        ####################### CFAST CASE ##############################

        if fastener.TypeElement == "CFAST":

            # Get CFAST card

            fastener_card = [i for i in get_cards_by_field2(model, cards, str(fastener.ID), 0, 1) if 
                             i.CharName.upper().strip() == 'CFAST'][0]

            # Check if CFAST is defined as ELEM
            if fastener_card.TYPE == "PROP":
                N2P.N2PLog.Warning.W502(fastener)
                continue

            # Property of CFAST

            prop_card = [i for i in get_cards_by_field2(model, cards, str(fastener.Prop), 0, 1) if 
                         i.CharName == 'PFAST']

            if len(prop_card) == 1:
                prop_card = prop_card[0]
            else:
                N2P.N2PLog.Warning.W503(fastener)
                continue

            # Get Nodes the CFAST is connected to.
            GA = fastener.Nodes[0]
            GB = fastener.Nodes[1]

            GA_coords = [GA.X, GA.Y, GA.Z]
            GB_coords = [GB.X, GB.Y, GB.Z]

            # Get Plates the CFAST is connected to.

            platesA = [fastener_card.IDA]
            platesB = [fastener_card.IDB]

            if len(platesA) == 0 or len(platesB) == 0:
                N2P.N2PLog.Warning.W504(fastener)
                continue

        ####################### CBUSH CASE ##############################

        if fastener.TypeElement == "CBUSH":
            # Get CBUSH card

            fastener_card = [i for i in get_cards_by_field2(model, cards, str(fastener.ID), 0, 1) if 
                        i.CharName.upper().strip() == 'CBUSH'][0]

            # Property of CBUSH

            prop_card = [i for i in get_cards_by_field2(model, cards, str(fastener.Prop), 0, 1) if 
                         i.CharName == 'PBUSH']
            
            if len(prop_card) == 1:
                prop_card = prop_card[0]
            else:
                N2P.N2PLog.Warning.W503(fastener)
                continue

            # Get Nodes the CBUSH is connected to.
            GA = fastener.Nodes[0]
            GB = fastener.Nodes[1]

            # Get Plates the CBUSH is connected to.

            platesA_elems = [element for element in GA.Connectivity if
                             (isinstance(element, N2PElement) and element.TypeElement in supported_elements)
                             or (isinstance(element, N2PConnector) and element.TypeConnector in supported_connectors)]

            platesB_elems = [element for element in GB.Connectivity if
                             (isinstance(element, N2PElement) and element.TypeElement in supported_elements)
                             or (isinstance(element, N2PConnector) and element.TypeConnector in supported_connectors)]

            # Case where CBUSH connected to RBE3 or RBE2 element.

            if isinstance(platesA_elems[0], N2PConnector):
                connectors_joined.append(platesA_elems[0])
                connectors_joined_ids.append(platesA_elems[0].ID)
                # Nodes of connector (Dependent + Independent)
                nodes = [model.NodesDict[node] for node in platesA_elems[0].FreeNodes + platesA_elems[0].SlaveNodes]

                results, elements_close_nodes, intersection_point = final_step_intersection(nodes, model, GA, GB, GA)

                if any(var is None for var in results) or any(var is None for var in elements_close_nodes) or any(var is None for var in intersection_point):
                    N2P.N2PLog.Warning.W506(fastener)
                    continue

                platesA_elems = [elements_close_nodes[i] for i, res in enumerate(results) if res]

                GA_coords = intersection_point

                has_connector = True
            else:
                GA_coords = [GA.X, GA.Y, GA.Z]

            if isinstance(platesB_elems[0], N2PConnector):
                connectors_joined.append(platesB_elems[0])
                connectors_joined_ids.append(platesB_elems[0].ID)
                # Nodes of connector (Dependent + Independent)
                nodes = [model.NodesDict[node] for node in platesB_elems[0].FreeNodes + platesB_elems[0].SlaveNodes]

                results, elements_close_nodes, intersection_point = final_step_intersection(nodes, model, GA, GB, GB)

                if any(var is None for var in results) or any(var is None for var in elements_close_nodes) or any(var is None for var in intersection_point):
                    N2P.N2PLog.Warning.W506(fastener)
                    continue

                platesB_elems = [elements_close_nodes[i] for i, res in enumerate(results) if res]

                GB_coords = intersection_point

                has_connector = True
            else:
                GB_coords = [GB.X, GB.Y, GB.Z]

            # Get plates
            platesA = [element.ID for element in platesA_elems]
            platesB = [element.ID for element in platesB_elems]

            if len(platesA) == 0 or len(platesB) == 0:
                N2P.N2PLog.Warning.W504(fastener)
                continue

            # Check if all plates have the same property.

            if not all(plate.Prop == platesA_elems[0].Prop for plate in platesA_elems):
                N2P.N2PLog.Warning.W507(fastener)
                continue

            if not all(plate.Prop == platesB_elems[0].Prop for plate in platesB_elems):
                N2P.N2PLog.Warning.W507(fastener)
                continue

                ####################### CBAR CASE ##############################

        if fastener.TypeElement == "CBAR":
            # Get CBAR card
            
            fastener_card = [i for i in get_cards_by_field2(model, cards, str(fastener.ID), 0, 1) if 
                             i.CharName.upper().strip() == 'CBAR'][0]
            
            # Property of CBAR
            
            prop_card = [i for i in get_cards_by_field2(model, cards, str(fastener.Prop), 0, 1) if 
                         i.CharName == 'PBAR']
            
            if len(prop_card) == 1:
                prop_card = prop_card[0]
            else:
                N2P.N2PLog.Warning.W503(fastener)
                continue

            # Get Nodes the CBAR is connected to.
            GA = fastener.Nodes[0]
            GB = fastener.Nodes[1]

            # Get Plates the CBAR is connected to.

            platesA_elems = [element for element in GA.Connectivity if
                             (isinstance(element, N2PElement) and element.TypeElement in supported_elements)
                             or (isinstance(element,
                                            N2PConnector) and element.TypeConnector in supported_connectors)]

            platesB_elems = [element for element in GB.Connectivity if
                             (isinstance(element, N2PElement) and element.TypeElement in supported_elements)
                             or (isinstance(element,
                                            N2PConnector) and element.TypeConnector in supported_connectors)]

            # Case where CBAR connected to a connector.

            # GA connected to a Connector.
            if isinstance(platesA_elems[0], N2PConnector):
                connectors_joined.append(platesA_elems[0])
                connectors_joined_ids.append(platesA_elems[0].ID)
                # Nodes of connector (Dependent + Independent)
                nodes = [model.NodesDict[node] for node in platesA_elems[0].FreeNodes + platesA_elems[0].SlaveNodes]

                # Obtain intersection point and where it is located.
                results, elements_close_nodes, intersection_point = final_step_intersection(nodes, model, GA, GB, GA)

                if any(var is None for var in results) or any(var is None for var in elements_close_nodes) or any(var is None for var in intersection_point):
                    N2P.N2PLog.Warning.W506(fastener)
                    continue

                platesA_elems = [elements_close_nodes[i] for i, res in enumerate(results) if res]

                # Coordinates of the intersection point of the 1D element with the plate.
                GA_coords = intersection_point

                has_connector = True
            # When the 1D element is connected directly to the plate.
            else:
                GA_coords = [GA.X, GA.Y, GA.Z]

            if isinstance(platesB_elems[0], N2PConnector):
                connectors_joined.append(platesB_elems[0])
                connectors_joined_ids.append(platesB_elems[0].ID)
                # Nodes of connector (Dependent + Independent)
                nodes = [model.NodesDict[node] for node in platesB_elems[0].FreeNodes + platesB_elems[0].SlaveNodes]

                # Obtain intersection point and where it is located.
                results, elements_close_nodes, intersection_point = final_step_intersection(nodes, model, GA, GB, GB)

                if any(var is None for var in results) or any(var is None for var in elements_close_nodes) or any(var is None for var in intersection_point):
                    N2P.N2PLog.Warning.W506(fastener)
                    continue

                platesB_elems = [elements_close_nodes[i] for i, res in enumerate(results) if res]

                # Coordinates of the intersection point of the 1D element with the plate.
                GB_coords = intersection_point

                has_connector = True
            # When the 1D element is connected directly to the plate.
            else:
                GB_coords = [GB.X, GB.Y, GB.Z]

            # Get plates
            platesA = [element.ID for element in platesA_elems]
            platesB = [element.ID for element in platesB_elems]

            if len(platesA) == 0 or len(platesB) == 0:
                N2P.N2PLog.Warning.W504(fastener)
                continue

            # Check if all plates have the same property.

            if not all(plate.Prop == platesA_elems[0].Prop for plate in platesA_elems):
                N2P.N2PLog.Warning.W507(fastener)
                continue

            if not all(plate.Prop == platesB_elems[0].Prop for plate in platesB_elems):
                N2P.N2PLog.Warning.W507(fastener)
                continue

        ###################################################################################
        ### CHECK EXISTING OR NEW BOLT
        ##################################################################################

        # CASE 1. Existing Bolt: Repeated Grid A
        if (GA in seen_nodes) and (GB not in seen_nodes):

            # CASE 1.1 - GB is not one of the points generated by connector usage.
            if not any(equal_points(GB_coords, point) for point in seen_points):
                # Get existing bolt
                Existing_bolt = ARBolt_list[node_to_bolt_dict.get(GA)]

                # Create new plate
                plate_id_iterator += 1
                bottom_plate_id = plate_id_iterator
                bottom_plate_elements = tuple(platesB)
                Plate_B = _create_plate(model, bottom_plate_elements, bottom_plate_id)
                Existing_bolt.append_plate(Plate_B)

                # Create new element1D
                top_plate_id = [plate.ID for plate in Existing_bolt.Plates if platesA[0] in plate.ElementIDs][0]
                element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                element1D.ConnectionPlateA = tuple(GA_coords)
                element1D.ConnectionPlateB = tuple(GB_coords)
                Existing_bolt.append_element1D(element1D)

                # Update bolt info to know it has connectors in it.
                if has_connector == True:
                    Existing_bolt.ContainsConnector = has_connector
                    Existing_bolt.ConnectorsInBolt.extend(connectors_joined)
                    Existing_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                seen_points.append(GB_coords)
                seen_nodes.add(GB)
                node_to_bolt_dict[GB] = ARBolt_list.index(Existing_bolt)
                point_to_bolt_dict[tuple(GB_coords)] = ARBolt_list.index(Existing_bolt)

            # CASE 1.2 - GB is one of the points generated by connector usage.
            else:
                # Extract existing bolt A
                Existing_bolt_A = ARBolt_list[node_to_bolt_dict.get(GA)]

                # Correction of node_to_bolt_dict to account for the deletion of the instance
                for node, bolt in node_to_bolt_dict.items():
                    if bolt > ARBolt_list.index(Existing_bolt_A):
                        node_to_bolt_dict[node] = bolt - 1

                # Remove exisitng bolt A from list
                ARBolt_list.remove(Existing_bolt_A)

                # Extract existing bolt B
                Existing_bolt_B = ARBolt_list[point_to_bolt_dict.get(tuple(GB_coords))]

                # Correction of node_to_bolt_dict to account for the deletion of the instance
                for node, bolt in point_to_bolt_dict.items():
                    if bolt > ARBolt_list.index(Existing_bolt_B):
                        point_to_bolt_dict[node] = bolt - 1

                # Remove exisitng bolt B from list
                ARBolt_list.remove(Existing_bolt_B)

                # Create updated instance
                top_plate_id = [plate.ID for plate in Existing_bolt_A.Plates if platesA[0] in plate.ElementIDs][0]
                bottom_plate_id = [plate.ID for plate in Existing_bolt_B.Plates if platesB[0] in plate.ElementIDs][0]
                element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                element1D.ConnectionPlateA = tuple(GA_coords)
                element1D.ConnectionPlateB = tuple(GB_coords)
                New_bolt = ARBolt.merge_3_bolts(Existing_bolt_A, element1D, Existing_bolt_B)

                ARBolt_list.append(New_bolt)

                if has_connector == True:
                    New_bolt.ContainsConnector = has_connector
                    New_bolt.ConnectorsInBolt.extend(connectors_joined)
                    New_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                node_to_bolt_dict[element1D.GA] = ARBolt_list.index(New_bolt)
                node_to_bolt_dict[element1D.GB] = ARBolt_list.index(New_bolt)
                point_to_bolt_dict[element1D.ConnectionPlateA] = ARBolt_list.index(New_bolt)
                point_to_bolt_dict[element1D.ConnectionPlateB] = ARBolt_list.index(New_bolt)

        # CASE 2. Existing Bolt: Repeated Grid B
        elif (GB in seen_nodes) and (GA not in seen_nodes):

            # CASE 2.1 - GA is not one of the points generated by connector usage.
            if not any(equal_points(GA_coords, point) for point in seen_points):

                # Get existing bolt
                Existing_bolt = ARBolt_list[node_to_bolt_dict.get(GB)]

                # Create new plate
                plate_id_iterator += 1
                top_plate_id = plate_id_iterator
                top_plate_elements = tuple(platesA)
                Plate_A = _create_plate(model, top_plate_elements, top_plate_id)
                Existing_bolt.append_plate(Plate_A)

                # Create new element1D
                bottom_plate_id = [plate.ID for plate in Existing_bolt.Plates if platesB[0] in plate.ElementIDs][0]
                element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                element1D.ConnectionPlateA = tuple(GA_coords)
                element1D.ConnectionPlateB = tuple(GB_coords)
                Existing_bolt.append_element1D(element1D)

                if has_connector == True:
                    Existing_bolt.ContainsConnector = has_connector
                    Existing_bolt.ConnectorsInBolt.extend(connectors_joined)
                    Existing_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                seen_points.append(GA_coords)
                seen_nodes.add(GA)
                node_to_bolt_dict[GA] = ARBolt_list.index(Existing_bolt)
                point_to_bolt_dict[tuple(GA_coords)] = ARBolt_list.index(Existing_bolt)

            # CASE 2.2 - GA is one of the points generated by connector usage.
            else:
                # Extract existing bolt A
                Existing_bolt_A = ARBolt_list[point_to_bolt_dict.get(tuple(GA_coords))]

                # Correction of node_to_bolt_dict to account for the deletion of the instance
                for node, bolt in point_to_bolt_dict.items():
                    if bolt > ARBolt_list.index(Existing_bolt_A):
                        point_to_bolt_dict[node] = bolt - 1

                # Remove exisitng bolt A from list
                ARBolt_list.remove(Existing_bolt_A)

                # Extract existing bolt B
                Existing_bolt_B = ARBolt_list[node_to_bolt_dict.get(GB)]

                # Correction of node_to_bolt_dict to account for the deletion of the instance
                for node, bolt in node_to_bolt_dict.items():
                    if bolt > ARBolt_list.index(Existing_bolt_B):
                        node_to_bolt_dict[node] = bolt - 1

                # Remove exisitng bolt B from list
                ARBolt_list.remove(Existing_bolt_B)

                # Create updated instance
                top_plate_id = [plate.ID for plate in Existing_bolt_A.Plates if platesA[0] in plate.ElementIDs][0]
                bottom_plate_id = [plate.ID for plate in Existing_bolt_B.Plates if platesB[0] in plate.ElementIDs][0]
                element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                element1D.ConnectionPlateA = tuple(GA_coords)
                element1D.ConnectionPlateB = tuple(GB_coords)
                New_bolt = ARBolt.merge_3_bolts(Existing_bolt_A, element1D, Existing_bolt_B)

                ARBolt_list.append(New_bolt)

                if has_connector == True:
                    New_bolt.ContainsConnector = has_connector
                    New_bolt.ConnectorsInBolt.extend(connectors_joined)
                    New_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                node_to_bolt_dict[element1D.GA] = ARBolt_list.index(New_bolt)
                node_to_bolt_dict[element1D.GB] = ARBolt_list.index(New_bolt)

                point_to_bolt_dict[element1D.ConnectionPlateA] = ARBolt_list.index(New_bolt)
                point_to_bolt_dict[element1D.ConnectionPlateB] = ARBolt_list.index(New_bolt)

        # CASE 3. New GA and GB
        elif (GA not in seen_nodes) and (GB not in seen_nodes):

            # CASE 3.1 - GA is not one of the points generated by connector usage.
            if not any(equal_points(GA_coords, point) for point in seen_points):
                # CASE 3.1.1 - GB is not one of the points generated by connector usage.
                if not any(equal_points(GB_coords, point) for point in seen_points):
                    # Create new bolt
                    bolt_id_iterator += 1
                    New_bolt = ARBolt(id=bolt_id_iterator)

                    # Create new top plate
                    plate_id_iterator += 1
                    top_plate_id = plate_id_iterator
                    top_plate_elements = tuple(platesA)
                    Plate_A = _create_plate(model, top_plate_elements, top_plate_id)

                    # Create new bottom plate
                    plate_id_iterator += 1
                    bottom_plate_id = plate_id_iterator
                    bottom_plate_elements = tuple(platesB)
                    Plate_B = _create_plate(model, bottom_plate_elements, bottom_plate_id)

                    # Create new element1D
                    element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                    element1D.ConnectionPlateA = GA_coords
                    element1D.ConnectionPlateB = GB_coords

                    New_bolt.append_element1D(element1D)
                    New_bolt.append_plate(Plate_A)
                    New_bolt.append_plate(Plate_B)

                    ARBolt_list.append(New_bolt)

                    if has_connector == True:
                        New_bolt.ContainsConnector = has_connector
                        New_bolt.ConnectorsInBolt.extend(connectors_joined)
                        New_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                    seen_points.append(GA_coords)
                    seen_points.append(GB_coords)

                    point_to_bolt_dict[tuple(GA_coords)] = ARBolt_list.index(New_bolt)
                    point_to_bolt_dict[tuple(GB_coords)] = ARBolt_list.index(New_bolt)

                    seen_nodes.add(GA)
                    node_to_bolt_dict[GA] = ARBolt_list.index(New_bolt)

                    seen_nodes.add(GB)
                    node_to_bolt_dict[GB] = ARBolt_list.index(New_bolt)

                # CASE 3.1.2 - GB is one of the points generated by connector usage.
                else:
                    # Get existing bolt
                    Existing_bolt = ARBolt_list[point_to_bolt_dict.get(tuple(GB_coords))]

                    # Create new plate
                    plate_id_iterator += 1
                    top_plate_id = plate_id_iterator
                    top_plate_elements = tuple(platesA)
                    Plate_A = _create_plate(model, top_plate_elements, top_plate_id)
                    Existing_bolt.append_plate(Plate_A)

                    # Create new element1D
                    bottom_plate_id = [plate.ID for plate in Existing_bolt.Plates if platesB[0] in plate.ElementIDs][0]
                    element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                    element1D.ConnectionPlateA = tuple(GA_coords)
                    element1D.ConnectionPlateB = tuple(GB_coords)
                    Existing_bolt.append_element1D(element1D)

                    if has_connector == True:
                        Existing_bolt.ContainsConnector = has_connector
                        Existing_bolt.ConnectorsInBolt.extend(connectors_joined)
                        Existing_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                    seen_points.append(GA_coords)
                    seen_nodes.add(GA)
                    node_to_bolt_dict[GA] = ARBolt_list.index(Existing_bolt)
                    point_to_bolt_dict[tuple(GA_coords)] = ARBolt_list.index(Existing_bolt)

            # CASE 3.2 - GA is one of the points generated by connector usage.
            else:
                # CASE 3.2.1 - GB is not one of the points generated by connector usage.
                if not any(equal_points(GB_coords, point) for point in seen_points):
                    # Get existing bolt
                    Existing_bolt = ARBolt_list[point_to_bolt_dict.get(tuple(GA_coords))]

                    # Create new plate
                    plate_id_iterator += 1
                    bottom_plate_id = plate_id_iterator
                    bottom_plate_elements = tuple(platesB)
                    Plate_B = _create_plate(model, bottom_plate_elements, bottom_plate_id)
                    Existing_bolt.append_plate(Plate_B)

                    # Create new element1D
                    top_plate_id = [plate.ID for plate in Existing_bolt.Plates if platesA[0] in plate.ElementIDs][0]
                    element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                    element1D.ConnectionPlateA = tuple(GA_coords)
                    element1D.ConnectionPlateB = tuple(GB_coords)
                    Existing_bolt.append_element1D(element1D)

                    # Update bolt info to know it has connectors in it.
                    if has_connector == True:
                        Existing_bolt.ContainsConnector = has_connector
                        Existing_bolt.ConnectorsInBolt.extend(connectors_joined)
                        Existing_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                    seen_points.append(GB_coords)
                    seen_nodes.add(GB)
                    node_to_bolt_dict[GB] = ARBolt_list.index(Existing_bolt)
                    point_to_bolt_dict[tuple(GB_coords)] = ARBolt_list.index(Existing_bolt)

                # CASE 3.2.2 - GB is one of the points generated by connector usage.
                else:
                    # Extract existing bolt A
                    Existing_bolt_A = ARBolt_list[point_to_bolt_dict.get(tuple(GA_coords))]

                    # Correction of node_to_bolt_dict to account for the deletion of the instance
                    for node, bolt in point_to_bolt_dict.items():
                        if bolt > ARBolt_list.index(Existing_bolt_A):
                            point_to_bolt_dict[node] = bolt - 1

                    # Remove exisitng bolt A from list
                    ARBolt_list.remove(Existing_bolt_A)

                    # Extract existing bolt B
                    Existing_bolt_B = ARBolt_list[point_to_bolt_dict.get(tuple(GB_coords))]

                    # Correction of node_to_bolt_dict to account for the deletion of the instance
                    for node, bolt in point_to_bolt_dict.items():
                        if bolt > ARBolt_list.index(Existing_bolt_B):
                            point_to_bolt_dict[node] = bolt - 1

                    # Remove exisitng bolt B from list
                    ARBolt_list.remove(Existing_bolt_B)

                    # Create updated instance
                    top_plate_id = [plate.ID for plate in Existing_bolt_A.Plates if platesA[0] in plate.ElementIDs][0]
                    bottom_plate_id = [plate.ID for plate in Existing_bolt_B.Plates if platesB[0] in plate.ElementIDs][
                        0]
                    element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
                    element1D.ConnectionPlateA = tuple(GA_coords)
                    element1D.ConnectionPlateB = tuple(GB_coords)
                    New_bolt = ARBolt.merge_3_bolts(Existing_bolt_A, element1D, Existing_bolt_B)

                    ARBolt_list.append(New_bolt)

                    if has_connector == True:
                        New_bolt.ContainsConnector = has_connector
                        New_bolt.ConnectorsInBolt.extend(connectors_joined)
                        New_bolt.ConnectorsIDs.extend(connectors_joined_ids)

                    node_to_bolt_dict[element1D.GA] = ARBolt_list.index(New_bolt)
                    node_to_bolt_dict[element1D.GB] = ARBolt_list.index(New_bolt)

                    point_to_bolt_dict[tuple(GA_coords)] = ARBolt_list.index(New_bolt)
                    point_to_bolt_dict[tuple(GB_coords)] = ARBolt_list.index(New_bolt)

        # CASE 4. Connector connecting to previously different Bolts
        elif (GA in seen_nodes) and (GB in seen_nodes):

            # The approach consists in extracting the information of the previous existing bolts and merge it with the new element1D
            # to create a new instance of the bolt. Then, delete the previous instances.

            # Extract existing bolt A
            Existing_bolt_A = ARBolt_list[node_to_bolt_dict.get(GA)]

            # Correction of node_to_bolt_dict to account for the deletion of the instance
            for node, bolt in node_to_bolt_dict.items():
                if bolt > ARBolt_list.index(Existing_bolt_A):
                    node_to_bolt_dict[node] = bolt - 1

            # Remove exisitng bolt A from list
            ARBolt_list.remove(Existing_bolt_A)

            # Extract existing bolt B
            Existing_bolt_B = ARBolt_list[node_to_bolt_dict.get(GB)]

            # Correction of node_to_bolt_dict to account for the deletion of the instance
            for node, bolt in node_to_bolt_dict.items():
                if bolt > ARBolt_list.index(Existing_bolt_B):
                    node_to_bolt_dict[node] = bolt - 1

            # Remove exisitng bolt B from list
            ARBolt_list.remove(Existing_bolt_B)

            # Create updated instance
            top_plate_id = [plate.ID for plate in Existing_bolt_A.Plates if platesA[0] in plate.ElementIDs][0]
            bottom_plate_id = [plate.ID for plate in Existing_bolt_B.Plates if platesB[0] in plate.ElementIDs][0]
            element1D = AR1DElement(fastener, fastener_card, prop_card, top_plate_id, bottom_plate_id)
            element1D.ConnectionPlateA = tuple(GA_coords)
            element1D.ConnectionPlateB = tuple(GB_coords)
            New_bolt = ARBolt.merge_3_bolts(Existing_bolt_A, element1D, Existing_bolt_B)

            ARBolt_list.append(New_bolt)

            if has_connector == True:
                New_bolt.ContainsConnector = has_connector
                New_bolt.ConnectorsInBolt.extend(connectors_joined)
                New_bolt.ConnectorsIDs.extend(connectors_joined_ids)

            node_to_bolt_dict[element1D.GA] = ARBolt_list.index(New_bolt)
            node_to_bolt_dict[element1D.GB] = ARBolt_list.index(New_bolt)

            point_to_bolt_dict[tuple(GA_coords)] = ARBolt_list.index(New_bolt)
            point_to_bolt_dict[tuple(GB_coords)] = ARBolt_list.index(New_bolt)

    # Check if the bolt has the same type of fasteners in it (either CFAST or CBUSH but not both).
    for bolt in ARBolt_list:
        # Check if all fasteners in the bolt have consistent directions wrt the plates they are connected to.
        plates_normals = [plate.Elements[0].Element.ElemSystemArray[6:9] for plate in bolt.Plates]
        elems1D_axials = [elem1D.Element.ElemSystemArray[0:3] for elem1D in bolt.Elements1D]
        are_same_direction  = [same_direction(fasten,plate)  for fasten, plate in zip(elems1D_axials, plates_normals)]
        if not any(are_same_direction ):
            N2P.N2PLog.Warning.W508(bolt)
            ARBolt_list.remove(bolt)

        # Check if all fasteners in the same Bolt instance are the same type.
        if not all(fast.Card.CardType == bolt.Elements1D[0].Card.CardType for fast in bolt.Elements1D):
            N2P.N2PLog.Warning.W509(bolt)
            ARBolt_list.remove(bolt)
        bolt.TypeFasteners = bolt.Elements1D[0].Card.CardType

    return ARBolt_list

############################### CREATE PLATE FUNCTION ################################
def _create_plate(model: N2PModelContent, element_ids: tuple, plate_id: int) -> ARPlate:
    """
    Create ARPlate object based on the given N2PModelContent, element_ids, and plate_id.
    Args:
        model: N2PModelContent - the N2P model content
        element_ids: tuple - the tuple of element ids
        plate_id: int - the plate id
    return:
        ARPlate - the ARPlate object created
    """
    Elem_list = [model.get_elements((id, 0)) for id in element_ids]
    Plate_elems = []
    complete_plate = True

    for i, elem in enumerate(Elem_list):

        if not isinstance(elem, N2PElement):
            N2P.N2PLog.Error.E500()
            continue

        prop = model.PropertyDict.get(elem.Prop)

        if not prop:
            N2P.N2PLog.Error.E501()
            Plate_elems.append(ARPlateElements(n2pelement=elem,
                                               n2pproperty=None,
                                               n2pmaterial=None))
            complete_plate = False

        else:
            if prop.PropertyType == 'PSHELL':
                material = model.MaterialDict.get(prop.MatMemID)
            elif prop.PropertyType == 'PCOMP':
                material = model.MaterialDict.get(prop.MatID[0])
            else:
                N2P.N2PLog.Error.E501()
                material = 0

            if not material:
                N2P.N2PLog.Error.E502()
                Plate_elems.append(ARPlateElements(n2pelement=elem,
                                                   n2pproperty=prop,
                                                   n2pmaterial=None))

            Plate_elems.append(ARPlateElements(elem, prop, material))

    return ARPlate(Plate_elems, plate_id)

############################### HELPER FUNCTIONS ################################

def get_cards_by_field2(model: N2PModelContent, cards, fields: str, row: int = 0, col: int = 0) -> list[N2PCard, ]:
    if isinstance(fields, str):
        fields = [fields]
    return [cards[idcard] for idcard
            in model.ModelInputData._N2PNastranInputData__inputfiledata.GetCardIDsByField(fields, row, col)]
    
def construct_dict() -> dict: 
    CONSTRUCTDICT = {"CBAR": CBAR, 
                        "CBEAM": CBEAM,
                        "CBUSH": CBUSH,
                        "CELAS1": CELAS1,
                        "CELAS2": CELAS2,
                        "CELAS3": CELAS3,
                        "CELAS4": CELAS4,
                        "CFAST": CFAST,
                        "CHEXA_NASTRAN": CHEXANAS,
                        "CHEXA_OPTISTRUCT": CHEXAOPT,
                        "CONM2": CONM2,
                        "CORD1C": CORD1C,
                        "CORD1R": CORD1R,
                        "CORD1S": CORD1S,
                        "CORD2C": CORD2C,
                        "CORD2R": CORD2R,
                        "CORD2S": CORD2S,
                        "CPENTA_NASTRAN": CPENTANAS,
                        "CPENTA_OPTISTRUCT": CPENTAOPT,
                        "CPYRA": CPYRA,
                        "CQUAD4": CQUAD4,
                        "CQUAD8": CQUAD8,
                        "CROD": CROD,
                        "CSHEAR": CSHEAR,
                        "CTETRA_NASTRAN": CTETRANAS,
                        "CTETRA_OPTISTRUCT": CTETRAOPT,
                        "CTRIA3": CTRIA3,
                        "CTRIA6": CTRIA6,
                        "CWELD": CWELD,
                        "GRID": GRID,
                        "MAT10_NASTRAN": MAT10NAS,
                        "MAT10_OPTISTRUCT": MAT10OPT,
                        "MAT1_NASTRAN": MAT1NAS,
                        "MAT1_OPTISTRUCT": MAT1OPT,
                        "MAT2_NASTRAN": MAT2NAS,
                        "MAT2_OPTISTRUCT": MAT2OPT,
                        "MAT3": MAT3,
                        "MAT4": MAT4,
                        "MAT5": MAT5,
                        "MAT8": MAT8,
                        "MAT9_NASTRAN": MAT9NAS,
                        "MAT9_OPTISTRUCT": MAT9OPT,
                        "MPC": MPC,
                        "PBAR": PBAR,
                        "PBARL": PBARL,
                        "PBEAM": PBEAM,
                        "PBEAML": PBEAML,
                        "PBUSH_NASTRAN": PBUSHNAS,
                        "PBUSH_OPTISTRUCT": PBUSHOPT,
                        "PCOMP_NASTRAN": PCOMPNAS,
                        "PCOMP_OPTISTRUCT": PCOMPOPT,
                        "PELAS": PELAS,
                        "PFAST": PFAST,
                        "PLOTEL": PLOTEL,
                        "PLPLANE": PLPLANE,
                        "PMASS": PMASS,
                        "PROD": PROD,
                        "PSHEAR": PSHEAR,
                        "PSHELL_NASTRAN": PSHELLNAS,
                        "PSHELL_OPTISTRUCT": PSHELLOPT,
                        "PSOLID_NASTRAN": PSOLIDNAS,
                        "PSOLID_OPTISTRUCT": PSOLIDOPT,
                        "PWELD": PWELD,
                        "RBAR": RBAR,
                        "RBAR1": RBAR1,
                        "RBE1": RBE1,
                        "RBE2": RBE2,
                        "RBE3": RBE3,
                        "RSPLINE": RSPLINE,
                        "SPC": SPC,
                        "SPC1": SPC1,
                        "UNSUPPORTED": N2PCard
                    }
    return CONSTRUCTDICT    

def get_intersection(fastener_GA: N2PNode, fastener_GB: N2PNode, plate: N2PElement) -> list:
    """
    Calculate the intersection point between a fastener and a plate.

    Args:
        fastener_GA: N2PNode
        fastener_GB: N2PNode
        plate: N2PElement

    Returns:
        list: The intersection point coordinates as a list.
    """
    origin = np.array([fastener_GA.X, fastener_GA.Y, fastener_GA.Z])
    end = np.array([fastener_GB.X, fastener_GB.Y, fastener_GB.Z])

    # x axis of the element1D
    element1D_vector = end - origin

    # Find the intersection of the bolt axis with the plane of the element
    node1 = np.array([plate.Nodes[0].X, plate.Nodes[0].Y, plate.Nodes[0].Z])
    node2 = np.array([plate.Nodes[1].X, plate.Nodes[1].Y, plate.Nodes[1].Z])
    node3 = np.array([plate.Nodes[2].X, plate.Nodes[2].Y, plate.Nodes[2].Z])
    plane_normal = np.cross(node3 - node1, node2 - node1) / np.linalg.norm(
        np.cross(node3 - node1, node2 - node1))

    t = np.dot(plane_normal, node1 - origin) / np.dot(plane_normal, element1D_vector)

    # intersection point of bolt x axis with plate plane
    intersection = origin + t * element1D_vector
    return intersection

def final_step_intersection(nodes: list, model: N2PModelContent, GA: N2PNode, GB: N2PNode, actual_node: N2PNode):
    """
    Generate a list of results, elements, and an intersection plate based on input nodes, model, GA, GB, and actual_node.

    Args:
        nodes: List of N2PNode
        model: N2pModelContent
        GA: N2PNode
        GB: N2PNode
        actual_node: N2PNode

    Returns:
        results: list
        elements_close_nodes: list
        intersection_plate: list[N2PElement]
    """
    supported_elements = ["CQUAD4", "CTRIA3"]
    # Elements in the face of one of the plates connected to the connector.

    elems_connected_to_node = [elem for node in nodes for elem
                    in node.Connectivity if (isinstance(elem, N2PElement) and elem.TypeElement in supported_elements)]

    if len(elems_connected_to_node) == 0:
        return [None], [None], [None]

    plates_in_face = [plate for plate in model.get_elements_by_face(elems_connected_to_node[0])]

    # Distance from GA to each node in the plates.
    distances_sort = sorted(
        [[np.linalg.norm(np.array([actual_node.X, actual_node.Y, actual_node.Z]) - np.array([node.X, node.Y, node.Z])),
          node]
         for elem in plates_in_face for node in elem.Nodes], key=lambda x: x[0])

    # Obatain the closest node.
    close_node = [x for i, x in enumerate(distances_sort) if x not in distances_sort[:i]][0][1]

    # Get elements that contain the closest node
    elements_close_nodes = [elem for elem in close_node.Connectivity if
                            (isinstance(elem, N2PElement) and elem.TypeElement in supported_elements)]

    # Get intersection of the projection of the 1D element with the plate.
    intersection_plate = np.array(min([get_intersection(GA, GB, plate) for plate in elements_close_nodes],
                                      key=np.linalg.norm))
    # Get vertices of the element where the intersection can be found.
    vertices_element = [[np.array(node.GlobalCoords) for node in elem.Nodes] for elem in elements_close_nodes]
    # Check if the intersection is inside the elements
    results = [point_in_element(intersection_plate, vertex) for vertex in vertices_element]

    return results, elements_close_nodes, intersection_plate
