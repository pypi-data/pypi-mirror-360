from NaxToPy.Core import N2PModelContent
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARAttachment import ARAttachment
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARBolt import ARBolt
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Functions.ARGetBolts import get_bolts
from NaxToPy import N2PLog

def get_attachments(model: N2PModelContent, bolt_list: list[ARBolt] = None):
    """ This functions takes as input NaxToPy model read from a mesh file, and (optionally) a list of ARBolts to work 
    with. If no bolt list is provided, the list will be extracted from the NaxToPy model. The function processes the
    list and the model and groups the bolts in the list into ARAttachement instances. The function returns a list of 
    ARAttachement instances. An attachement is understood as the set of bolts that join the exact same plates.


    Args:
        model: N2PModelContent
        bolt_list: list[ARBolt]

    Returns:
        attachment_list: list[ARAttachement]

    Calling example:

            attachments = get_attachments(model=model1, bolt_list=bolts)

    Additional information:

    •	As already mentioned, the bolt list input is not compulsory. The default value is None for it. If the default
        value is left or the input list of bolts is empty, the function will take the bolts from the model using the already
        explained function “get_bolts”. However, this will only serve to get all the attachments, because the function
        "bolt_reader” will not be called.

    """
    
    # STEP 0. If no bolt_list is provided, the list is extracted from the model
    if not bolt_list:
        bolt_list = get_bolts(model)

    # STEP 0.1. Get domain of CQUAD and CTRIA elementes of the whole model

    domain = [element for element in model.get_elements() if element.TypeElement == 'CQUAD4' or element.TypeElement == 'CTRIA3']

    # Auxiliar variables definitions
    seen_plates = []
    seen_plates_dict = {}
    plate_id_iterator = 0
    old_to_new_plate_id_dict = {}

    # STEP 1. Loop over bolt_list

    for i, bolt in enumerate(bolt_list):
        # STEP 1.1. Loop over each plate inside the bolt
        for plate in bolt.Plates:

            if len(plate.Elements) == 0:
                N2PLog.Warning.W505(bolt)
                continue

            # In order to assess whether two bolts connect the same plate or not, the only method found is to label 
            # the plate with the set of all 2D element IDS that conform that plate. This is done using the NaxToPy 
            # function get_attached (this may be slow for big models
            plate_element = plate.Elements[0].Element
            all_elements_in_plate_ids = set([e.ID for e in model.get_elements_attached(cells=plate_element,
                                                                                       domain=domain)])

            if all_elements_in_plate_ids not in seen_plates:
                # If this is the first time the plate is seen, it is given a new ID
                plate_id_iterator += 1
                seen_plates.append(all_elements_in_plate_ids)
                new_plate_id = plate_id_iterator
                seen_plates_dict[new_plate_id] = all_elements_in_plate_ids

                old_to_new_plate_id_dict[plate.ID] = new_plate_id
                plate.ID = new_plate_id
            else:
                # If the plate has already been seen, it is given its corresponding ID
                new_plate_id = [k for k, v in seen_plates_dict.items() if v == all_elements_in_plate_ids][0]

                old_to_new_plate_id_dict[plate.ID] = new_plate_id
                plate.ID = new_plate_id
            
            #The bolt is given the set of plates it attches to
            bolt.AttachingPlates.add(new_plate_id)

                

        # STEP 1.2. It is also necessary to update the reference to plate IDs inside each Element1D. This is done 
        # using the previous dictionary.
        for element1d in bolt.Elements1D:
            element1d.BottomPlateID = old_to_new_plate_id_dict.get(element1d.BottomPlateID)
            element1d.TopPlateID = old_to_new_plate_id_dict.get(element1d.TopPlateID)

    # STEP 2 At this stage all the information needed to classify the bolts into attachments is already stored inside
    # each of them. Another loop over the list creates the ARAttachment instances.
    
    seen_attachments = []
    attachment_list = []
    attachment_to_list_index_dict = {}
    attachment_id_iterator = 0
    for bolt in bolt_list:
        attachment = tuple(bolt.AttachingPlates)

        if attachment not in seen_attachments:

            ###CASE 1. NEW ATTACHEMENT
            attachment_id_iterator += 1

            new_attachment = ARAttachment(id = attachment_id_iterator)
            new_attachment.AttachedPlatesIDs = attachment
            new_attachment.AttachedPlates = bolt.Plates
            new_attachment.Bolts.append(bolt)

            attachment_list.append(new_attachment)
            attachment_to_list_index_dict[attachment] = attachment_list.index(new_attachment)

            seen_attachments.append(attachment)
        else:
            ###CASE 2. EXISITNG ATTACHEMENT
            exisitng_attachment_list_index = attachment_to_list_index_dict.get(attachment)
            exisitng_attachment = attachment_list[exisitng_attachment_list_index]

            exisitng_attachment.Bolts.append(bolt)

    return attachment_list