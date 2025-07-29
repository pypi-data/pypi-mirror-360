# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info.

"""Module with all the required functions to load the C# dinamic libraries"""

from enum import Enum
import sys
import os
import winreg
import clr

from NaxToPy.Core.Constants.Constants import (
    DEVELOPER_VIZZER, VIZZER_CLASSES_DLL, VERSION, NAXTO_VERSION, COMPILED_VIZZER, NAXTO_ADVANCED_INSTALLER
)
from NaxToPy.Core.Errors.N2PLog import N2PLog

class _RunType(Enum):
    """Enumeration for different runtime environments."""
    RELEASE = 0
    EXE = 1
    DEVELOPE = 2
    COMPILED = 3


def _check_run_type() -> _RunType:
    """Returns a RunType value:
        - RELEASE
        - EXE
        - DEVELOPE
    """
    dev_dll_path = os.path.join(DEVELOPER_VIZZER, VIZZER_CLASSES_DLL)
    compiled_dll_path = os.path.join(COMPILED_VIZZER, VIZZER_CLASSES_DLL)

    if getattr(sys, 'frozen', False):  # PyInstaller EXE
        return _RunType.EXE
    
    elif os.path.exists(dev_dll_path):  # Development environment
        return _RunType.DEVELOPE
    
    elif os.path.exists(compiled_dll_path):
        return _RunType.COMPILED
    
    else:
        return _RunType.RELEASE  # Default to RELEASE
    

def _search_naxtomodel() -> str:
    """Searchs in the register for the installed version of NaxTo and returns the NaxToModel.dll path.    
    """

    # Check first in LOCAL_MACHINE, if fails, check in CURRENT_USER
    naxto_paths = (
        _read_register(winreg.HKEY_LOCAL_MACHINE) or
        _read_register(winreg.HKEY_CURRENT_USER)
    )

    # If fails again, return None
    if naxto_paths is None:
        return None
    
    compatible_path = _check_compatibility(naxto_paths)
    if not compatible_path:
        return None
    else:
        return os.path.join(compatible_path, f"bin\\{VIZZER_CLASSES_DLL}")


def _check_compatibility(naxto_paths: list[tuple[str,str]]) -> str:
    """Finds what of the NaxTo versions that are installed is compatible with this NaxToPy version 
    
    Returns:
        Path: String with the path to a compatible dll
    """
    for version, path in naxto_paths:
        # Version is NAXTOVIEW_202XRY, so only the 202XRY is checked
        if version.split("_")[1] == NAXTO_VERSION:
            return path
        
    # If no compatible, return None
    return None


def _search_license(path: str) -> str:
    """Search for NaxToLicense.dll path"""
    return os.path.join(os.path.dirname(path), "NaxToLicense.dll")


def _read_register(keyType: int) -> list[tuple[str, str]]:
    """Try to read the instalation path of NaxTo. 
    
    - Returns a tuple ordered from newer to older with the version and the path.
    - Returns None if fails.
    
    Returns:
        list[tuple[NAXTOVIEW_VERSION, PATH]]
    """
    try:
        # Open the key for IDAERO sub keys
        with winreg.OpenKey(keyType, "SOFTWARE\\IDAERO") as idaerokey:
            # Save how many subkeys there are in IDAERO
            num_naxto_keys = winreg.QueryInfoKey(idaerokey)[0]

            naxto_versions = []
            for i in range(num_naxto_keys):
                # Searchs only for the NAXTOVIEW subkeys in the IDAERO key
                if winreg.EnumKey(idaerokey, i).split("_")[0] == "NAXTOVIEW":
                    naxto_versions.append(winreg.EnumKey(idaerokey, i))
    except:
        return None
    
    else:
        naxto_versions.sort(reverse=True)  # Ordered from newer to older
        naxto_paths = []  # List of tuples with the version and the path of the version
        for version in naxto_versions:
            with winreg.OpenKey(keyType, f"SOFTWARE\\IDAERO\\{version}") as naxto_key:
                path = winreg.QueryValueEx(naxto_key, "Path")[0]
                naxto_paths.append((version, path))
        
        return naxto_paths


def _write_register() -> None:
    """Opens the Windows Register and generates the IDAERO key in LOCAL_MACHINE or in CURRENT_USER if fails and write the Path value    
    """
    
    try:
        # We search where this file is placed. It will be in a TEMP dicrectory. Then we go up 3 directories
        naxtopy_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        keyType = winreg.HKEY_LOCAL_MACHINE

        # We try to use the LOCAL_MACHINE first
        try:
            naxto_key = winreg.CreateKey(keyType, f"SOFTWARE\\IDAERO\\NAXTOVIEW_{NAXTO_VERSION}")
            
        # We use the CURRENT_USER if fails
        except:
            keyType = winreg.HKEY_CURRENT_USER
            naxto_key = winreg.CreateKey(keyType, f"SOFTWARE\\IDAERO\\NAXTOVIEW_{NAXTO_VERSION}")

        winreg.SetValueEx(naxto_key, "Path", 0, winreg.REG_SZ, naxtopy_path + "\\")

    except Exception as e:
        msg = N2PLog.Error.E112(e)
        raise Exception(msg)
    finally:
        naxto_key.Close()

def _check_naxto_version() -> bool:
    """Returns true if the NaxTo version is compible with NaxToPy checking the windows register"""
    try:
        naxto_paths = _read_register(winreg.HKEY_LOCAL_MACHINE) or _read_register(winreg.HKEY_CURRENT_USER)
        if naxto_paths is None:
            return False
        
        compatible_path = _check_compatibility(naxto_paths)
        if compatible_path is None:
            return False
        
        return True

    except Exception as e:
        return False

def _clean_register() -> None:
    """Removes temporary registry entries created during EXE runtimes."""

    def delete_register(keyType: int):
        try:
            # Key is open with access equal to KEY_READ (default) to be read
            with winreg.OpenKey(keyType, f"SOFTWARE\\IDAERO\\NAXTOVIEW_{NAXTO_VERSION}") as naxto_key:
                path = winreg.QueryValueEx(naxto_key, "Path")[0]
            if "TEMP" in path:
                # Key is open with access equal to KEY_SET_VALUE to be deleted
                with winreg.OpenKey(keyType, f"SOFTWARE\\IDAERO\\NAXTOVIEW_{NAXTO_VERSION}", 0, winreg.KEY_SET_VALUE) as naxto_key:
                    winreg.DeleteValue(naxto_key, "Path")
        except (FileNotFoundError, PermissionError):
            pass
    
    for key_type in {winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER}:
        delete_register(key_type)


def __reference_finder() -> None:
    """Main function that loads the required dlls based on the runtime type.
    
    In order to load the dlls, some checks must be done:
        1. NaxToPy Version
        2. NaxTo Compatibility
        3. Type of running: .exe, develope, release
        4. Where the libraries are placed
        5. If EXE but it has same version as the installed (RELEASE) use the installed
        6. Load the libraries
    """

    # Check the type of run. Depending of the ruing type the libraries will be search in a place.
    run_type = _check_run_type()

    if run_type == _RunType.RELEASE:
        naxtomodel_path = _search_naxtomodel()
        if naxtomodel_path is None:
            msg = N2PLog.Critical.C110(VERSION, NAXTO_VERSION)
            raise ImportError(msg)
        
        # The register has given a path, but perhaps it doesn't exist.
        if not os.path.exists(naxtomodel_path):
            msg = N2PLog.Critical.C114(naxtomodel_path)
            raise ImportError(msg)
        seconddll_path = _search_license(naxtomodel_path)

    elif run_type == _RunType.DEVELOPE:
        naxtomodel_path = os.path.join(DEVELOPER_VIZZER, VIZZER_CLASSES_DLL)
        seconddll_path = os.path.join(r"C:\GIT_REPOSITORIES\NAXTO\NAXTOLibsDebug\NAXLicense\v.4.0", "NaxToLicense.dll")
        N2PLog.Info.I108()

    elif run_type == _RunType.COMPILED:
        naxtomodel_path = os.path.join(COMPILED_VIZZER, VIZZER_CLASSES_DLL)
        seconddll_path = os.path.join(r"C:\GIT_REPOSITORIES\NAXTO\NAXTOLibsDebug\NAXLicense\v.4.0", "NaxToLicense.dll")
        N2PLog.Info.I113()

    elif run_type == _RunType.EXE:
        naxtomodel_path = _search_naxtomodel()
        N2PLog.Info.I107(VERSION)

        if naxtomodel_path is None or "IDAERO" not in naxtomodel_path:
            _clean_register()
            naxtomodel_path = sys._MEIPASS + "\\bin\\NaxToModel.dll"
            _write_register()
            N2PLog.Info.I115()
        elif not _check_naxto_version():
            _clean_register()
            naxtomodel_path = sys._MEIPASS + "\\bin\\NaxToModel.dll"
            _write_register()
            N2PLog.Info.I115()
        else:
            N2PLog.Info.I116()

        seconddll_path = _search_license(naxtomodel_path)

    try:
        clr.AddReference(naxtomodel_path)
        clr.AddReference(seconddll_path)

        from NaxToModel import Global
        # Compatible NaxToPy versions acording to N2ModelContent.dll
        compatible_versions = list(Global.NAXTOPY_COMPATIBILITY)
        if VERSION in compatible_versions or Global.VERSION_ADVANCED_INSTALLER == NAXTO_ADVANCED_INSTALLER:
            pass
        else:
            N2PLog.Warning.W107(compatible_versions)
        N2PLog.Info.I114(Global.RELEASE_VERSION)

    except Exception:
        msg = N2PLog.Critical.C103()
        raise ImportError(msg)
    
    else:
        N2PLog.Info.I109()
        N2PLog.Debug.D101(naxtomodel_path)
    
    N2PLog.Info.I100()