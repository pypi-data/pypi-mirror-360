"""Constants of the NaxToPy package"""

# NaxToPy Version
VERSION = "3.1.1"

# Supported for Naxto:
NAXTO_VERSION = '2025R1'
NAXTO_STEP = "1"
NAXTO_ADVANCED_INSTALLER = "2025.1.1"

# Assembly version of NaxToModel.dll
VIZZER_COMPATIBILITY = ("5.1.0.1")
"""Tuple with the compatible versions of NaxToModel.dll"""

# PYTHON EXTERNO ----------------------------------------------------------------------------------
# Versiones de Python soportadas:
SUP_PY_VER = (9, 10, 11, 12, 13)

# Librerias Externas de Python
EXTERNAL_LIBS_PYTHON = ['cffi',
                        'clr_loader',
                        'pycparser',
                        'pythonnet',
                        'numpy',
                        'setuptools',
                        'h5py']
# -------------------------------------------------------------------------------------------------

# Binary extensions supported by NaxToPy ----------------------------------------------------------
BINARY_EXTENSIONS = ["op2", "xdb", "h5", "h3d", "odb", "rst"]

# NAXTO -------------------------------------------------------------------------------------------
# Ruta a las librerias de NaxTo
DEVELOPER_VIZZER = r'C:\GIT_REPOSITORIES\NAXTO\NAXTOVIEW\v.5.0\NaxToView\NaxToModel\bin\x64\Debug'

COMPILED_VIZZER = r"C:\GIT_REPOSITORIES\NAXTO\NAXTOLibsDebug\NAXTOVIEW\v.5.0"

# DLLs de NaxTo
VIZZER_CLASSES_DLL = 'NaxToModel.dll'
# -------------------------------------------------------------------------------------------------

PEDIGREE_FACTOR = 1000  # Para pasar de id pedigree a id solver: id_solver = id_pedigree // _PEDIGREE_FACTOR_
                        # Para obtener el id part: id_pedigree % _PEDIGREE_FACTOR_

WEB_DOC = r"https://www.idaerosolutions.com/NaxToPyDoc/index.html"
