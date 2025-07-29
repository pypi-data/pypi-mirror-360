import NaxToPy as N2P
import pickle as pkl
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARBolt import ARBolt
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARAttachment import ARAttachment
from NaxToPy.Core import N2PModelContent

def serialize(list_to_serialize: list, file: str) -> None:
    '''
    Serializes a list of “ARBolt” or “ARAttachment” and dumps the data into a file. This file will be a .pkl with all
    the stored data. It is important to recognize that serialize must only be used at the end of the script. Objects in
    memory may change when serialize is called, even if they are not directly passed to the function. Thus, when using
    this function, only the most important data of each of the objects is stored, and leaving everything as a function
    of the elements, properties and materials IDs.

    Args:
        list_to_serialize: list
        file: str

    Returns:
        pkl file

    Calling example:

            serialize(list_to_serialize =bolts, file = serial_location)

    '''

    # We have not been able to make a deepcopy of list_to_serialize, therefore all AR objects may change and get
    # serialized. To make a deep copy, objects need to be pickleable, N2P objects are not. We have not found a simple
    # alternative to solve this issue.

    supported_types = (ARBolt, ARAttachment)

    if isinstance(list_to_serialize, list):

        if not all(isinstance(elem, supported_types) for elem in list_to_serialize):
            N2P.N2PLog.Error.E513()
            return None
    else:
        N2P.N2PLog.Error.E514()
        return None

    serialized_list = [elem.serialize() for elem in list_to_serialize]
    with open(file, 'wb') as f:
        pkl.dump(serialized_list, f)


def deserialize(file: str, model: N2PModelContent, frac = 1.0) -> list:
    '''
    Deserializes a list of ARBols or ARAttachments loading a pickle file.

    Args:
        file: str
        model: N2PModelContent
        frac: int. Fraction of the list that will be deserialized. The default value is 1.0. (recommended to maintain t
        he default value in order to deserialize everything as you could use the “bolt_reader” function to select the
        wanted bolts)

    Returns:
        serialized_list: list[ARBolt or ARAttachment]

    Calling example:

            deserialize(file = serial_location, model = model)

    '''
    supported_types = (ARBolt, ARAttachment)

    with open(file, 'rb') as f:
        serialized_list = pkl.load(f)

    num_elems = len(serialized_list)
    elems_to_process = int(frac*num_elems)

    if isinstance(serialized_list, list):
        if all(isinstance(elem, supported_types) for elem in serialized_list):
            for elem in serialized_list[:elems_to_process]:
                elem.deserialize(model)
            return serialized_list

        else:
            N2P.N2PLog.Error.E515()
            return 0
    else:
        N2P.N2PLog.Error.E516()
        return 0