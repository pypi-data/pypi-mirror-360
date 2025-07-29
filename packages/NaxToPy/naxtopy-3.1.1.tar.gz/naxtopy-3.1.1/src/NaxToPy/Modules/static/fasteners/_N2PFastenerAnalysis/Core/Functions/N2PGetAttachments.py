"""
Script with functions used to identify attachments and create N2PAttachment objects. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

from NaxToPy.Core import N2PModelContent
from NaxToPy.Modules.static.fasteners.joints.N2PAttachment import N2PAttachment
from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint

# New method used to obtain a model's attachments ----------------------------------------------------------------------
def get_attachments(model: N2PModelContent, jointsList: list[N2PJoint]) -> list[N2PAttachment]: 

    """
    Method that obtains a model's N2PAttachments and fills some of their attributes. 

    Two joints are said to be part of the same attachment if they are attached to the same group of N2PElements. The 
    elements they are attached to are defined by calling the NaxTo function get_elements_attached for each plate in the 
    joint. Furthermore, two joints are said to be part of an attachment if one joint's attached elements are a subset 
    of the other joint's attached elements. 
    This can be clarified with the following example: consider three joints, two of them made up by two CFASTs and one 
    made up by one CFAST, so the first two would have three plates and the last one would have only two. Assume that 
    these joints all conect roughly the same region of the model, so they intuitively should be part of the same 
    attachment. In this case, the joints 1 and 2 will have exactly the same attached elements, so they would form an 
    N2PAttachment. However, joint 3 will have less attached elements, as it has one less plate, but all of them 
    will be included in the list of attached elements of the previous joints (joint 3's attached element list is a 
    subset of joints 1 and 2's attached element list). In this case, joint 3 is also said to be part of this 
    attachment. 

    Args: 
        model: N2PModelContent
        jointList: list[N2PJoint] -> list of all N2PJoints to be analyzed.

    Returns: 
        attachmentList: list[N2PAttachment]

    Calling example: 
        >>> myAttachments = get_attachments(model1, JointsList) 
    """

    # Joints are assigned a new attribute, attached_elements, which are the N2PElements obtained from calling the 
    # model.get_elements_attached() function with the joint's plate elements as an input. 
    if jointsList[0].PlateList[0]._attached_elements: 
        hasAttached = True 
    else: 
        hasAttached = False 
    for j in jointsList: 
        if hasAttached: 
            j._attached_elements = j.PlateList[0]._attached_elements
            for p in j.PlateList[1:]: 
                j._attached_elements.update(p._attached_elements)
        else: 
            j._attached_elements = set(model.get_elements_attached(model.get_elements([p.PlateCentralCellSolverID 
                                                                                       for p in j.PlateList])))
    iterator = 0 
    attachmentList = [] 
    # All joints are searched 
    for i1, j in enumerate(jointsList): 
        for l in jointsList[i1+1:]: 
            # If the second joint already has an attachment, it is skipped 
            if not l.Attachment: 
                if isAttached(j,l): 
                    # If the joints are attached, and it is the first time this attachment has been seen, a new 
                    # attachment is created 
                    if not j.Attachment: 
                        j._attachment = N2PAttachment(id = iterator) 
                        j._attachment._joints_list.append(j) 
                        j._attachment._attached_plates_id_list = [] 
                        j._attachment._attached_plates_list = []
                        attachmentList.append(j.Attachment)
                        iterator = iterator + 1 
                    # Regardless of whether or not the attachment is new, the second joint is assigned this attachment, 
                    # and it is appended to the attachment's list of joints 
                    l._attachment = j.Attachment
                    l._attachment._joints_list.append(l) 
    for i in attachmentList: 
        iterator = 0 
        for j in i.JointsList: 
            for p in j.PlateList: 
                # Plates in the attachment are assigned their new attachment ID, and the attachment gets some 
                # attributes filled in 
                p._attachment_id = iterator 
                iterator = iterator + 1 
                i._attached_plates_list.append(p) 
                i._attached_plates_id_list.append(p.PlateCentralCellSolverID)
    return attachmentList
# ----------------------------------------------------------------------------------------------------------------------

# Method used to determine if two joints have the same attached elements -----------------------------------------------
def isAttached(j: N2PJoint, l: N2PJoint) -> bool: 

    """
    Auxiliary method used to determine if two joint's attached elements are approximately the same. 

    Args: 
        j, l: N2PJoint -> joints to be searched 
    Returns: 
        True or False 

    Two joints are said to have approximately the same elements if one of the three conditions are met: 
        - Their attached elements are exactly the same 
        - The attached elements of the first joint are a subset of the attached elements of the second 
        - The attached elements of the second joint are a subset of the attached elements of the first
    If these conditions are not met, or if the joints are identical, the function returns False. 
    """

    if j == l:
        return False
    aj = j._attached_elements
    al = l._attached_elements
    return aj == al or aj.issubset(al) or al.issubset(aj)
# ----------------------------------------------------------------------------------------------------------------------