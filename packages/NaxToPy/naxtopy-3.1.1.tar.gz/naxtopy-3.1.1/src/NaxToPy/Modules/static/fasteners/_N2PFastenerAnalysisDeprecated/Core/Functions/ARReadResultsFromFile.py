import os
from NaxToPy import N2PLog

def results_in_folder(folder: str) -> list:
    """
    Reads and stores all the files stored in a folder. It takes as input the directory path of the folder and reads and
    stores in a list the paths of each of the file that are inside of it.

    Args:
        folder: str

    Returns:
        paths: list

    """
    paths = []
    # Complete path to the folder.
    path_folder = os.path.join(os.path.expanduser('~'), 'Desktop', folder)

    # Verify if folder exists.
    if os.path.exists(path_folder) and os.path.isdir(path_folder):
        # List paths in the folder.
        for name_file in os.listdir(path_folder):
            path_file = os.path.join(path_folder, name_file)
            paths.append(path_file)

    # If it does not exist.
    else:
        N2PLog.Critical.user("[results_in_folder] The folder {} was not found.".format(folder))

    return paths