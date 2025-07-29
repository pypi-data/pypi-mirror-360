import subprocess
import pkgutil
import os
from pkg_resources import resource_filename
from typing import Literal

import NaxToPy.Core.Reference_Finder.__Reference_Finder as RF
from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToPy.Core.Constants.Constants import VIZZER_CLASSES_DLL


# Funcion que busca el path del icono de NaxToPy -----------------------------------------------------------------------
def __ico_path() -> str:
    """ Funcion oculta que busca el icono de NaxToPy

        Returns: 
            icon_path: str
    """
    try:
        ico_path = resource_filename('NaxToPy', 'NaxToPy.ico')
        N2PLog.Info.I200()
        return ico_path

    except:
        search_path = r"C:\GIT_REPOSITORIES\NAXTO\NaxToPy\v.1.0\NaxToPy"
        filename = "NaxToPy.ico"
        for root, directory, files in os.walk(search_path):
            if filename in files:
                N2PLog.Info.I200()
                return str(os.path.join(search_path, filename))

    N2PLog.Error.E304()
    return -1
# ----------------------------------------------------------------------------------------------------------------------


# Funcion que busca si se usa el paquete NaxToPy -----------------------------------------------------------------------
def __busca_n2p(path) -> bool:
    """ Funcion oculta que busca si se usa el modulo NaxToPy en los archivos que se quieren convertir en ejecutables
    """
    with open(path) as f:
        if 'import NaxToPy' in f.read():
            return True
        else:
            return False
# ----------------------------------------------------------------------------------------------------------------------


# Funcion oculta que devuelve la lista de las bibliotecas de las que hace uso NaxToPy ----------------------------------
def __list_ext_libs(libs_path, solver, abq_ver) -> list[str]:
    """ Funcion oculta que devuelve la lista de las bibliotecas de las que hace uso NaxToPy.

        Estan donde NaxToView está instalado. Las devulve con el formato listo para añadirse a la llamada de PyInstaller

        Args:
            libs_path: str

        Returns: 
            dll_list: list
    """
    import NaxToPy.Core.Constants.librerias as lb

    if isinstance(abq_ver, str):
        abq_ver = [abq_ver]

    i = -1
    libs = list()
    directions = list()
    # Bucle que busca todas las versiones de abaqus que hay disponibles para NaxTo y las guarda en directions.
    # También guarda en libs todas las dll de NaxTo para que se guarden en el .exe
    for root, dirnames, filenames in os.walk(libs_path):
        i += 1
        libs += filenames

        if i == 1:
            directions += dirnames
            break

    if abq_ver is None or all(items in directions for items in abq_ver):
        pass
    else:
        N2PLog.Critical.C105(lb.ABAQUS_VERSION)
        # sys.exit(f"C105: THE ARGUMENT ABAQUSVERSION MUST BE ONE OF THE AVAILABLE: {lb.ABAQUS_VERSION}")

    #abq_ver = abq_ver.split(" ")
    abq_libs = list()

    dll_list = list()
    for dll in libs:
        dll_list.append('--add-data')
        dll_list.append(libs_path + "\\" + dll + r";./bin")

    if abq_ver == "" or abq_ver is None or abq_ver == [""] or abq_ver == []:
        abq_ver = []

    elif abq_ver == ["ALL"] or abq_ver == ["all"]:
        for dirs in directions:
            abq_libs.append("ABQS\\" + dirs)

    else:
        for abq in abq_ver:
            abq_libs.append("ABQS\\" + abq)

    dll_abq_list = list()
    for dll in abq_libs:
        dll_abq_list.append('--add-data')
        dll_abq_list.append(libs_path + "\\" + dll + r";./bin" + f"\\{dll}")

    dll_list += dll_abq_list

    return dll_list
# ----------------------------------------------------------------------------------------------------------------------


_solver_type = Literal["ALL", "NASTRAN", "ABAQUS", "ANSYS", "OPTISTRUCT"]
_abqver_type = list[Literal["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "6.11", "6.12", "6.13", "6.14"]]


# Funcion principal que usa PyInstaller para generar el .exe -----------------------------------------------------------
def n2ptoexe(path: str, console: bool = True, solver: _solver_type = "ALL", abaqusversion: _abqver_type = None,
             splash: str = "", extra_packages: list[str] = None, extra_files: list[str] = None,
             hidden_imports: list[str] = None) -> None:
    """Function that creates .exe files of programs that use NaxToPy

    Args:
        path: str -> path of the module that will be used to create the .exe file

        console: bool -> If True (Default), the .exe will opne a console of python.
                         If False, the .exe will not open any python console.

        solver: srt | list[str] -> Default="ALL" Solver or list of solvers that the module will work with.
                                   Posible solvers are:  "NASTRAN", "ABAQUS", "ANSYS", "OPTISTRUCT"

        abaqusversion: str | list[srt] -> Default='2022'. Only when "ABAQUS" is selected a str or a list of
                                          ABAQUS version are aviable. Posible abaqus versions:
                                          ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '6.11', '6.12',
                                          '6.13', '6.14']
        splash: str -> Optional. Path to the splash image. If used, the user must introduce pyi_splash.close() at the
            beginning of the execution of the module. Import pyi_splash first. The splash image will appear during  the
            .exe unpacking. Image should be png and smaller than 500x500 pixels.
        extra_packages: list[str] -> If some packages are not imported correctly by the function, they can be added
                                     manually. An example of a package that usually fails is 'sv_ttk'.
        extra_files: list[str] -> Lis of path of extra dll, images or other files the user want to add the exe. The
                                  files will be saved in the ./bin directory inside the exe. To acces to the files
                                  use: path_file = os.path.join(sys._MEIPASS, r"bin\mylib.dll")

    Examples:
        >>> n2ptoexe(r"C:\Scripts\myscript1.py")
        >>> n2ptoexe(r"C:\Scripts\myscript2.py", console=False, solver="NASTRAN")
        >>> n2ptoexe(r"C:\Scripts\myscript3.py", console=True, solver="OPTISTRUCT", splash=r"C:\Scripts\mysplash.jpg")
        >>> n2ptoexe(r"C:\Scripts\myscript4.py", extra_packages=["sv_ttk"], extra_files=[r"C:\Scripts\icon.png"])
        >>> n2ptoexe(r"C:\Scripts\myscript5.py", hidden_imports=["plyer.platforms.win.notification"])
    """

    # 0 ) Genera el archivo .log y añade los logs de la importación ------------------------------------------------
    # Configura el logger para que escriba automaticamente los logs ------------------------------------------------
    N2PLog._N2PLog__fh.write_buffered_records()
    N2PLog._N2PLog__fh.immediate_logging()

    # Paso todoo a mayusculas para que no haya errores
    solver.upper()

    icon = __ico_path()

    try:
        if pkgutil.find_loader("PyInstaller") is None:
            subprocess.call(['pip', 'install', "PyInstaller"])

        import PyInstaller.__main__ as PyIns
    except RuntimeError:
        msg = N2PLog.Critical.C106()
        raise RuntimeError(msg)

    # Si queremos que el ejecutable saque una consola de python. Si se piden cosas mediante la funcion input(), o
    # queremos sacar cosas por consola con un print() habrá que marcar console. Si funciona todo por interfaz grafica,
    # usando por ejemplo tkinter o no es necesario interactuar en absoluto es mejor marcar windowed (sin consola).

    if console == True:
        consl = "-c"
    elif console == False:
        consl = "-w"
    else:
        msg = N2PLog.Critical.C104()
        raise Exception(msg)

    if __busca_n2p(path):

        # We want something like 'C:\\Program Files\\IDAERO\\NaxTo\\NaxTo_202XRY\\NAXTOVIEW\\bin'
        libs_path = os.path.dirname(RF._search_naxtomodel())
        dll_list = __list_ext_libs(libs_path, solver, abaqusversion)
        

        # Aqui se cargan las propiedades de la llamada a PyInstaler
        pyinstaller_cmd = [path] + [consl]
        pyinstaller_cmd += dll_list
        if icon == -1:
            pyinstaller_cmd += ["--onefile", "--collect-all", "NaxToPy"]
            # pyinstaller_cmd += ["--collect-all", "NaxToPy"]  # "--onefile",
            N2PLog.Warning.W200()
        else:
            pyinstaller_cmd += ["--onefile", "--collect-all", "NaxToPy", '--icon', icon]

        if splash:
            pyinstaller_cmd += ['--splash', splash]

        if extra_files:
            for file in extra_files:
                if os.path.isfile(file):
                    pass
                else:
                    msg = N2PLog.Error.E113(file)
                    raise Exception(msg)
                pyinstaller_cmd += ["--add-data", f"{file};./bin"]

        if extra_packages:
            for package in extra_packages:
                pyinstaller_cmd += ["--collect-data", package]

        if hidden_imports:
            for h_import in hidden_imports:
                pyinstaller_cmd += ["--hidden-import", h_import]

        PyIns.run(pyinstaller_cmd)
        N2PLog.Info.I201(os.getcwd())
    else:
        msg = N2PLog.Error.E110(path)
        raise Exception(msg)

# ----------------------------------------------------------------------------------------------------------------------
