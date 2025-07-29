import os
import sys
import logging
import time
import atexit
from abc import ABC
from typing import Literal

from NaxToPy.Core.Errors.N2PFileHandler import FileHandler


# Clase que se encarga del registro de NaxToPy -------------------------------------------------------------------------
class N2PLog(ABC):
    """ Class prepared for the control of the program.

    It uses the module logging to register the main instructions and
    data of the NaxToPy Package. It can't be instanced.

    Attributes:
        LevelList
    """

    # Aqui se definen los atributos de la clase, cuyo concepto es ligeramente diferente ald de los de la instancia
    flv = "INFO"
    clv = "WARNING"

    LevelList = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # Nivel de registro del archivo .log
    if flv == "DEBUG":
        __flevel = logging.DEBUG
    elif flv == "WARNING":
        __flevel = logging.WARNING
    elif flv == "ERROR":
        __flevel = logging.ERROR
    elif flv == "CRITICAL":
        __flevel = logging.CRITICAL
    else:
        __flevel = logging.INFO

    # Nivel de registro de lo que sale por consola
    if clv == "DEBUG":
        __clevel = logging.DEBUG
    elif clv == "WARNING":
        __clevel = logging.WARNING
    elif clv == "ERROR":
        __clevel = logging.ERROR
    elif clv == "CRITICAL":
        __clevel = logging.CRITICAL
    else:
        __clevel = logging.INFO

    __directory = os.path.dirname(os.path.abspath(sys.argv[0]))

    if __directory == "C:\\Users":
        __directory = os.path.expanduser("~") + "\\Documents\\"

    __filename = time.strftime("NaxToPy_%Y-%m-%d.log", time.localtime())
    __path = os.path.join(__directory, __filename)

    __logger = logging.getLogger('Logger')
    __logger.setLevel("DEBUG")

    # Formato en el que se presenta los datos del registro en el archivo .log
    __formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)-5s", "%H:%M:%S")

    # File with the loggin data:
    __fh = FileHandler(__path)
    __fh.setLevel(__flevel)
    __fh.setFormatter(__formatter)
    __logger.addHandler(__fh)

    # Formato en el que se presenta los datos del registro en la consola
    __formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)-5s", "%H:%M:%S")

    # Loggin data shown in the console
    __ch = logging.StreamHandler()
    __ch.setLevel(__clevel)
    __ch.setFormatter(__formatter)
    __logger.addHandler(__ch)

    # Primera instruccion en el logger
    __logger.info("############### NaxToPy Started ###############")

    # Ultima instruccion en el logger
    atexit.register(__logger.info, "############### NaxToPy Finished ###############\n")

    # Tras cualquier error critico, contemplado o no, se ejecuta esta funcion. Se comprueba si el ultimo error
    # almacenado era crtico o no, se escribe el archivo .log y se activa el logger. Si el ultimo error almacenado no
    # era critico o no hay errores almacenados es porque el error que ha causado el fallo no estaba contemplado. En
    # ese caso se llama al error C001 y despues se escribe el log 
    def _my_excepthook(excType, excValue, traceback, logger=__logger, fh=__fh):

        if not fh.buffered_records:
            previous_critical = fh.buffered_records[-1].getMessage().startswith('C')
        else:
            previous_critical = False

        if not previous_critical:
            logger.critical("C001: UNCAUGHT CRITICAL EXCEPTION: ", exc_info=(excType, excValue, traceback))

        fh.write_buffered_records()
        fh.immediate_logging()
    # ----------------------------------------------------------------------------------------------------------------

    sys.excepthook = _my_excepthook

    # ATRIBUTOS COMO CLASES DE LA CLASE N2PLog PARA INTRODUCIR DATOS EN EL REGISTRO -----------------------------------

    ############################################  DEBUG  ###############################################################
    class Debug:
        """ Class with all the debug data.

        The DXXX are methods that keep in the register the information in the
        debuggibg procces about the processes that the package is keeping. Use only in the debug stages.
        
        :meta private:
        """

        @staticmethod
        def user(message: str) -> None:
            """Method prepared to be called by the user for adding debugs data to the loggin

            Anyone who is using NaxToPy can write in the register their
            own debug message. Use the following structure as a standard message (D + four digits + Body).

            Args:
                message: str

            Example:
                "DXXXX: Body of the message"
            """
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D100(instruction, timee) -> None:
            """Method for timing the instructions during debug
            """
            message = f"Time (s) {instruction}: {timee}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D101(path) -> None:
            """Method that shows the location of the NaxToModel library found"""
            message = f"NaxToModel found at: {path}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D102() -> None:
            """Method that shows if the property Program_Call of N2ModelContent was changed"""
            message = f"Program_Call of N2ModelContent has been set"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D103(parallel) -> None:
            """Method that shows the parallel option set at low level"""
            message = f"The parallel processing has been set to {parallel}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D104(connectors: bool) -> None:
            """Method that shows the parallel option set at low level"""
            message = f"Load Connectors Option is set to {connectors}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D200(assembly) -> None:
            """Message that shows the assembly version of the core library"""
            message = f"The assembly version is: {assembly}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D201(result_file) -> None:
            """Message that shows that the results from a file were loaded correctly"""
            message = f"The results from {result_file} were loaded correctly"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D499(fastener_ID) -> None:
            """ Information given for the extraction time.
            """
            message = f"D499: Fastener updated: {fastener_ID}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D500(current_time,tinit) -> None:
            """ Information given for the extraction time.
            """
            message = f"D500: Extraction time: {current_time-tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D501(current_time,tinit) -> None:
            """ Information given for computation time of elastic modulus.
            """
            message = f"D501: Elastic modulus calculation time: {current_time-tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D502(current_time,tinit) -> None:
            """ Information given for computation time of set intersection
            """
            message = f"D502: Set intersection computation time: {current_time-tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D503(current_time,tinit) -> None:
            """ Information given for computation time of fastener update
            """
            message = f"D503: Fastener update computation time: {current_time-tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D504(current_time,tinit) -> None:
            """ Information given for loading time of the model
            """
            message = f"D504: Model loading time: {current_time-tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D600(current_time, tinit) -> None:
            """ Information given for result obtention time.
            """
            message = f"D600: Result obtention time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D601(current_time, tinit) -> None:
            """ Information given for fasteners obtention time.
            """
            message = f"D601: Fasteners obtention time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D602(current_time, tinit) -> None:
            """ Information given for fasteners analysis time.
            """
            message = f"D602: Fasteners analysis time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D603(current_time, tinit) -> None:
            """ Information given for fasteners attachments obtention time.
            """
            message = f"D603: Fasteners attachments obtention time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D604(current_time, tinit) -> None:
            """ Information given for fasteners whole calculation time.
            """
            message = f"D604: Fasteners whole calculation time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D605(current_time, tinit) -> None: 
            """ Information given for fasteners distance obtention time. """
            message = f"D605: Fasteners distance obtention time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D606(current_time, tinit) -> None: 
            """ Information given for fasteners force obtention time. """
            message = f"D605: Fasteners forces obtention time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D607(current_time, tinit) -> None: 
            """ Information given for fasteners bypass loads obtention time. """
            message = f"D605: Fasteners bypass loads obtention time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D608(current_time, tinit) -> None: 
            """ Information given for results export time. """
            message = f"D605: Fasteners results export time: {current_time - tinit} s"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D900(time) -> None: 
            """ Information given for time invested in element filtering stage in N2PCalculatorRFJoints"""
            message = f"D900: Elements Filtering time: {time}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D901(time) -> None: 
            """ Information given for time invested in composite elements RF calculation in N2PCompRF"""
            message = f"D901: Composite elements RF calculation time: {time}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D902(time) -> None: 
            """ Information given for time invested in metallic elements RF calculation in N2PMetalRF"""
            message = f"D902: Metallic elements RF calculation time: {time}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod 
        def D903(time) -> None: 
            """ Information given for time invested in rivet elements RF calculation in N2PRivetRF"""
            message = f"D903: Rivet elements RF calculation time: {time}"
            N2PLog._N2PLog__logger.debug(message)
    # ------------------------------------------------------------------------------------------------------------------

    ############################################  INFO  ################################################################
    class Info:
        """ Class with all the information data. The IXXX are methods that keep in the register the information
        about the processes that the package is keeping.
        
        :meta private:
        """

        @staticmethod
        def user(message) -> None:
            """ Method prepared to be used by the user so anyone who is using NaxToPy can write in the register their
own information message. Use the following structure as a standard message (I + four digits + Body).

                "IXXXX: Body of the message"
            """
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I100() -> None:
            """ Information that show that the NaxToPy Runing Code.
            """
            from NaxToLicense import LicenseManager
            from System import DateTime
            from datetime import datetime

            current_date = datetime.now()

            time_date = DateTime(current_date.year, current_date.month, current_date.day, current_date.hour,
                                 current_date.minute, current_date.second)

            licen = LicenseManager()

            if not licen.HasLicense():
                err = LicenseManager.GenerateCommunityLicense()
                licen.HasLicense()

            code = licen.GetRunCode(time_date)
            message = f"I100: NaxToPy Running with the code: {code}"
            N2PLog._set_format2(time_date.ToString().split(" ")[1])
            N2PLog._N2PLog__logger.info(message)
            N2PLog._set_format1()

        @staticmethod
        def I101(vizzer_libs) -> None:
            """ Information that show that the NaxTo libraries were correctly found at vizzer_libs.
            """
            message = f"I101: The NaxTo libraries were found successfully at {vizzer_libs}."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I102(value) -> None:
            message = f"I102: The directory of the .log file has been modified to {value} ."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I103(value) -> None:
            message = f"I103: The name of the .log file has been modified to {value} ."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I104() -> None:
            message = f"I104: Numpy installation has been successfully completed."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I105() -> None:
            """ Information given when the register is modified correctly.
            """
            message = f"I105: The windows register was modified with the path of the NaxTo libraries successfully."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I106(register, key_version) -> None:
            """ Information given when the register is modified correctly.
            """
            message = f"I106: Key for {key_version} created successfully in {register}."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I107(version) -> None:
            """ Information given when the program is called from a .exe file.
            """
            message = f"I107: Working with the executable version libraries of NaxTo. NaxToPy version: {version}"
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I108() -> None:
            """ Information given when the program use the develover version of NaxToModel.
            """
            message = "I108: Working with developer version of NaxToModel."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I109() -> None:
            """ Information given when the NaxToModel library is load correctly.
            """
            message = f"I109: Library NaxToModel.dll loaded successfully."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I110(path) -> None:
            """ Information given when the file .N2P is saved correctly.
            """
            message = f"I110: The file {path} has been successfully saved."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I111(path) -> None:
            """ Information given when the result file is initialize correctly.
            """
            message = f"I111: The file {path} has been successfully opened."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I112() -> None:
            """ Information given when the result the mesh is build correctly.
            """
            message = "I112: The mesh has been successfully created."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I113() -> None:
            """ Information given when the program use the compiled version of NaxToModel.
            """
            message = "I113: Working with compiled version of NaxToModel of NAXTOLibsDebug"
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I114(nversion) -> None:
            """ Print the version of the NaxTo that it is being executed.
            """
            message = f"I114: Working with NaxTo version {nversion}"
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I115() -> None:
            """ Working with the naxto libraries from the exe
            """
            message = "I115: Working with NaxTo libraries embedded in the .exe"
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I116() -> None:
            """ Working with the installed naxto libraries
            """
            message = "I116: Working with NaxTo installed libraries (in Program Files\IDAERO)"
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I200() -> None:
            """ Information given when the NaxToPy.ico is found correctly.
            """
            message = "I200: The NaxToPy icon file has been successfully found."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I201(file) -> None:
            """ Information given when the .exe file built with n2ptoexe() is correctly created.
            """
            message = f"I201: The .exe file has been successfully created at {file}."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I202(id) -> None:
            """ Information given when the .exe file built with n2ptoexe() is correctly created.
            """
            message = f"I202: The Active Increment has been set to the ID: {id}"
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I203() -> None:
            """ Information given when the module N2PEnvelope is executing.
            """
            message = f"I203: Executing N2PEnvelope..."
            N2PLog._N2PLog__logger.info(message)


        @staticmethod
        def I500() -> None:
            """ Information given when the ID list is empty.
            """
            message = f"I500: All load cases will be studied because no ID list was given."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I501() -> None:
            """ Information given when the ID list is empty.
            """
            message = f"I501: All fasteners will be studied because no ID list was given."
            N2PLog._N2PLog__logger.info(message)
    # ------------------------------------------------------------------------------------------------------------------

    ###########################################  WARNING  ##############################################################
    class Warning:
        """ Class with all the warnings. The WXXX are methods that keep in the register the warnings that might be
        revised. They don't affect directly to the correct working of the package.

        :meta private:
        """

        @staticmethod
        def user(message) -> None:
            """ Method prepared to be used by the user so anyone who is using NaxToPy can write in the register their
            own warning message. Use the following structure as a standard message (W + four digits + Body).

                "WXXXX: Body of the message"
            """
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W100() -> None:
            """ Warning raised when numpy is not installed and it will be installed using pip
            """
            message = "W100: numpy package is not installed. In order to execute this method, the package is needed. \n" + \
                      "      The installation will start in 10 seconds ."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W101() -> None:
            """ Warning raised when the register level of the .log file is intended to change, as it could make more difficult to track errors
            """
            message = "W101: Register level of the .log has changed to a higher filter. This can make more difficult to track errors."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W102(path) -> None:
            """ Warning raised when the Windows Register is modified by NaxToPy
            """
            message = f"W102: The Windows Register has been modified: CURRENT_USER/SOFTWARE/IDAERO -> Path = {path}" + \
                "  If NaxTo is installed afterwards, this key must be deleted"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W103() -> None:
            """ Warning raised when the Windows Register is modified by NaxToPy: The Path value is deleted
            """
            message = f"W103: The Path Value in Windows Register has been deleted."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W104(naxver) -> None:
            """ Warning raised when the version NaxTo that this NaxToPy version is prepared for is not found
            """
            message = f"W104: This NaxToPy should work with {naxver}, that is NOT found. Checking compatibility with" \
                      f"other versions installed"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W105() -> None:
            """ Warning raised when the assemblies founded are not saved as compatible
            """
            message = f"W105: No library was found to be compatible with this NaxToPy version. The package may" \
                      f"work but is recommended to find a compatible NaxTo or NaxToPy version."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W106(e) -> None:
            """ Warning raised when the register couldn't be destroyed
            """
            message = f"W106: The NaxTo key couldn't be destroyed. It may cause some errors in the future. Error:{e}"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W107(versions: list) -> None:
            """ The NaxToModel.dll was loaded successfully, but it may not be fully compatible.
            """
            message = (f"W107: The NaxTo library was loaded successfully, but it may not be fully compatible.\n"
                       f"\tConsider to use this NaxToPy versions: {versions}")
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W110(depre_method, new_method) -> None:
            """ Deprecated Warning
            """
            message = f"W110: The {depre_method} is deprecated. Please use {new_method} instead"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W200() -> None:
            """ Warning raised when the executable file is build without the icon
            """
            message = "W200: The .exe file will not have the NaxToPy icon. There should have been an error while loading it"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W201() -> None:
            """ Warning raised when the AbaqusVersion is asked but the solver is not Abaqus
            """
            message = "W201: The Abaqus version is None as the solver is not ABAQUS"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W202() -> None:
            """ Warning raised when the number of elements don't match with the size of the results
            """
            message = "W202: The number of elements don't match with the size of the results"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W203() -> None:
            """ Warning raised when there are two connectors with the same id. So they are saved in the connector dict
            as a list.
            """
            message = f"W203: there are two or more connectors with the same id. They are saved in the connector" + \
                      f"dict as a list with the same key."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W204() -> None:
            """ Warning raised when there is no Model Data from an Input File.
            """
            message = f"W204: There is no data from an input file data supported"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W205() -> None:
            """ Warning raised when there the Deprecated function "Initialize" is called.
            """
            message = f"W205: Initialize is a deprecated function. Please, use load_model instead"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W206() -> None:
            """ Warning raised when there the Deprecated property "ActiveIncrement" is called.
            """
            message = f"W206: ActiveIncrement is a deprecated property. Please, ActiveN2pIncrement to obtain a " \
                      f"N2PIncrement or ActiveN2pIncrement.ID to obtain the ID"
            N2PLog._N2PLog__logger.warning(message)


        @staticmethod
        def W207() -> None:
            """ Warning raised when there the Deprecated class "N2PModelInputData" is called.
            """
            message = f"W207: N2PModelInputData class is a deprecated. Please, use N2PNastranInputData"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W208(coord) -> None:
            """ Asking for results in self defined coordinate system at the same time in antother option.
            """
            message = (f"W208: v1 and v2 where provided when the coordsys marked was {coord}. The coord option {coord} will prevail.\n"
                       "To enforce to use v1 and v2 mark coordsys=-10 or don't mark it at all")
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W209() -> None:
            """ An average variation parameter have been set when aveNodes value is not average (-3)
            """
            message = f"W209: An average variation parameter have been set when aveNodes value is not average (-3)"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W210(comp) -> None:
            """
            Warning raised when the component selected is not transformable.
            """
            message = f"W210: The component selected ({comp}) is not transformable"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W300() -> None:
            """ Warning raised when there are more dimensions than points in n2p.envelope
            """
            message = f"W300: there are more dimensions than points as arguments in n2p.envelope"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W301(name) -> None:
            """ Warning raised when the name for the new derived load case already exist
            """
            message = f"W301: the name for the new load case already exist. It has been rename to '{name}'"
            N2PLog._N2PLog__logger.warning(message)


        @staticmethod
        def W500(listids) -> None:
            """ Warning raised when a CBUSH or CBAR has not a defined Diameter.
            """
            message = f"W500: Fasteners {listids} have not a defined Diameter and are either CBUSH or CBAR. The input diameter needs to be used"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W501(bolt) -> None:
            """ Warning raised when a CBUSH is defined with coincident nodes.
            """
            message = f"W501: CBUSH {bolt.ID} is discarded for the study because it is defined with coincident nodes"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W502(bolt) -> None:
            """ Warning raised when a CFAST is defined as PROP.
            """
            message = f"W502: CFAST {bolt.ID} ignored: defined as PROP."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W503(bolt) -> None:
            """ Warning raised when a Fastener property is not found.
            """
            message = f"W503: Fastener {bolt.ID} ignored: property not found."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W504(bolt) -> None:
            """ Warning raised when a Fastener plates are not found.
            """
            message = f"W504: Fastener {bolt.ID} ignored: plates not found."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W505(bolt) -> None:
            ''' Warning raised when a fastener element is not found.
            '''
            message = f"W505: Fastener {bolt.ID} skipped. Element not found."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W506(bolt) -> None:
            ''' Warning raised when a fastener intersection with the plate is not found.
            '''
            message = f"W506: Fastener {bolt.ID} ignored: intersection with the plate not found."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W507(bolt) -> None:
            ''' Warning raised when different types of properties found in the same joined plate elements.
            '''
            message = f"W507: Different types of properties found in the same joined plate elements: not consistent. Fastener {bolt.ID} ignored."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W508(bolt) -> None:
            ''' Warning raised when direction of elements 1D wrt connected plates not consistent.
            '''
            message = f"W508: Direction of elements 1D wrt connected plates not consistent. Fastener {bolt.ID} ignored."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W509(bolt) -> None:
            ''' Warning raised when different type of elements 1D in the same bolt.
            '''
            message = f"W509: Different type of elements 1D in the same bolt: not consistent. Fastener {bolt.ID} ignored."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W510(listids) -> None:
            ''' Warning raised when a fastener has not a provided head position.
            '''
            message = f"W510: Fasteners {listids} have not a provided head position, so the inner element 1D order is set indistinctly."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W511() -> None:
            ''' Warning raised when calculation using the results in the centroid.
            '''
            message = f"W511: Calculation using the results in the centroid may not be as precise as when Corner Data is used."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W512(plate, bolt) -> None:
            ''' Warning raised when element not found.
            '''
            message = f"W512: Skipping plate {plate.ID} of bolt {bolt.ID}. Element not found."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W513(bolt) -> None:
            ''' Warning raised when intersection point with plate not defined.
            '''
            message = f"W513: Intersection point with plate not defined. Bypass calculation skipped in fastener {bolt.ID}."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W514(bolt) -> None:
            ''' Warning raised when normal to plate not defined.
            '''
            message = f"W514: Normal to plate not defined. Bypass calculation skipped in fastener {bolt.ID}."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W515(bolt) -> None:
            ''' Warning raised when distance to edge not defined.
            '''
            message = f"W515: Distance to edge not defined. Bypass calculation skipped in fastener {bolt.ID}."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W516(bolt) -> None:
            ''' Warning raised when no plate elements found.
            '''
            message = f"W516: No plate elements found. Bypass calculation skipped in fastener {bolt.ID}."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W517() -> None:
            ''' Warning raised when a plate is not an ARPlate.
            '''
            message = f"W517: Plate omitted. Incorrect class: Should be ARPlate."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W518() -> None:
            ''' Warning raised when a fastener is not an AR1DElement.
            '''
            message = f"W518: Fastener omitted. Incorrect class: Should be AR1DElement."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W519(elem) -> None:
            ''' Warning raised when a element is not CQUAD4 nor CTRIA3.
            '''
            message = f"W519: Element {elem.ID} is not CQUAD4 nor CTRIA3."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W520(plate) -> None: 
            '''Warning raised when a plate has no elements adjacent.'''
            message = f"W520: Plate with element ID {plate.PlateCentralCellSolverID} has not enough adjacent elements and the box's points will be projected."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W521(plate) -> None:
            '''Warning raised when the normal direction of a plate has not been calculated.'''
            message = f"W521: Normal direction to plate {plate.PlateCentralCellSolverID} not defined. The bypass calculations are skipped."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W522() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, the get_fasteners attribute is set while the model or list_joints attribute is also set'''
            message = f"W522: The model and/or list_joints attribute is already set. They will be overwritten."
            N2PLog._N2PLog__logger.warning(message)
        
        @staticmethod
        def W523() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, the model attribute is set while the get_fasteners attribute is also set'''
            message = f"W523: The model attribute has already been set by get_fasteners. It will be overwritten."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W524() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, the list_joints attribute is set while the get_fasteners attribute is also set'''
            message = f"W524: The list_joints attribute has already been set by get_fasteners. It will be overwritten."
            N2PLog._N2PLog__logger.warning(message)
        
        @staticmethod
        def W525() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, the type_export attribute is not NAXTOPY, PAG ALTAIR'''
            message = f"W525: Type of export not supported. The results will be exported in NAXTOPY style. Try <<NAXTOPY>>, <<PAGTXT>>, <<<PAGCSV>>> or <<ALTAIR>>."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W526(parameter) -> None: 
            '''Warning raised when the bypass parameters dictionary is not well defined'''
            message = f"W526: Bypass parameter {parameter} is not well defined. The default value will be used."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W527(input, instance) -> None: 
            '''Warning raised when an input is of a wrong instance.'''
            message = f"W527: Attribute {input} is not a {instance} instance. The default value will be used."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W528() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, the export_precison attribute is not 4 or 8'''
            message = f"W528: Precission not supported. The default precission will be used. Try 4 or 8."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W529(jointList) -> None: 
            '''Warning raised when a CFAST has no attached plates'''
            message = f"W529: Fasteners with IDs: {jointList} have been removed due to a problem with their geometry."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W530(plate) -> None:
            '''Warning raised when the intersection point of a plate has not been calculated.'''
            message = f"W530: Intersection point with plate {plate.PlateCentralCellSolverID} not defined. The bypass calculations are skipped."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W531(plate) -> None: 
            '''Warning raised when a plate's intersection point cannot be found.'''
            message = f"W531: The intersection point of plate with solver ID: {plate.CentralElement.ID} cannot be found. A default value is assigned."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W532() -> None: 
            '''Warning raised when, in N2PGetFasteners, the get_distance method is used before the get_joints() one'''
            message = f"W532: No N2PJoints have been created. The get_joints() method is now being called."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W533() -> None: 
            '''Warning raised when, in N2PGetFasteners, the get_attachments method is used before the get_intersection() one'''
            message = f"W533: No intersections have been calculated. The get_intersection() method is now being called."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W534(attribute, instance) -> None: 
            '''Warning raised when an input (as a list) has no valid elements inside.'''
            message = f"W534: Attribute {attribute} has no valid {instance} instances, so it is not set."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W535(listids) -> None:
            '''Warning raised when there are fasteners with an incorrect diameter'''
            message = f"W535: Fasteners {listids} will not be calculated because they have a wrong (zero or negative) or no diameter."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W536() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, get_box() has not been called'''
            message = f"W536: The bypass boxes have not been calculated. The get_box() method is now being called."
            N2PLog._N2PLog__logger.warning(message) 

        @staticmethod
        def W537() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, get_forces() has not been called'''
            message = f"W537: The bearing forces have not been calculated. The get_forces() method is now being called."
            N2PLog._N2PLog__logger.warning(message) 

        @staticmethod
        def W538() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, get_bypass() has not been called'''
            message = f"W538: The bypass loads have not been calculated. The get_bypass() method is now being called."
            N2PLog._N2PLog__logger.warning(message) 

        @staticmethod
        def W539() -> None: 
            '''Warning raised when, in N2PGetLoadFasteners, get_results() has not been called'''
            message = f"W539: The results have not been obtained. The get_results() method is now being called."
            N2PLog._N2PLog__logger.warning(message) 

        @staticmethod
        def W540(plate) -> None:
            '''Warning raised when iterations > maxIterations in get_box()'''
            message = f"W540: Unable to create the bypass box of plate {plate.PlateCentralCellSolverID} because the maximum number of iterations was reached."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W541() -> None:
            '''Warning raised when the number of components of the vector and the reference systems are not multiple of 3 in rotate_vector().'''
            message = f"W541: The number of components of the vector and the reference systems must be multiple of 3. The vector is not rotated."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W542(element = None, vertices = None) -> None: 
            '''Warning raised when one wants to determine if a point is in an element that is not supported.'''
            if element: 
                message = f"W542: Element with ID {element.ID} is not supported, as it is a {element.TypeElement}. Only 'CQUAD' and 'CTRIA3' elements are supported."
            else: 
                message = f"W542: Element with vertices {vertices} is not supported, as it is a {element.TypeElement}. Only 'CQUAD' and 'CTRIA3' elements are supported."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W543(point, quad) -> None:
            '''Warning raised when there is an error in the isoparametric transformation.'''
            message = f"W543: Cannot obtain isoparametric coordinates of the point {point} within the quad with nodes {quad}."
            N2PLog._N2PLog__logger.warning(message)
            
        @staticmethod 
        def W544(path) -> None: 
            '''Warning raised when a loaded file does not exist or is not a file'''
            message = f"W544: Path {path} does not exist or is not a file, so it is not loaded."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W545(lclist) -> None: 
            '''Warning raised when there is a broken load case in get_results()'''
            message = f"W545: Load cases with IDs: {[k.ID for k in lclist]} are broken, so they are removed from the list and their results are ignored."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W546(id) -> None: 
            '''Warning raised when there are many warnings of the same type and they are no longer printed.'''
            message = f"W546: There are many warnings with ID: {id}. Please see the log for all of them."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod 
        def W547() -> None: 
            '''Warning raised when trying to export a file to a path that is not a folder.'''
            message = f"W547: Path does not exist or is not a folder."
            N2PLog._N2PLog__logger.warning(message) 

        @staticmethod
        def W650() -> None:
            ''' Warning raised when specific arguments have been introduce to the plastic class.
            '''
            message = f"W650: For this choosen arguments the Yield Stress must be at zero plastic strain."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W651() -> None:
            ''' Warning raised when a non ISOTROPIC/MAT1 asociated to the element has been chosen.
            '''
            message = f"W651: Some elements have been removed because they are not metallic materials."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W700() -> None:
            ''' Warning raised when a data entry does not have its compulsory information
            '''
            message = f"W700: A DataEntry does not have all of its necessary information. Its data is not written."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W701(elementType) -> None:
            ''' Warning raised when, while writing an HDF5, the element type is not element, corner or node. 
            '''
            message = f"W701: Element type {elementType} not accepted. Try <<ELEMENT>>, <<CORNER>> or <<NODE>>."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W702() -> None:
            ''' Error thrown when attempting to retrieve the material of a Beam General Section.'''
            message = f"W702: The materials of Beam General Section are not supported"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def W800() -> None:
            ''' Warning raised when, given a list of elements, not all the elements have a composite 
            PropertyType associated.
            '''
            message = f"W800: List of elements include non-composite elements. Those elements will be removed, and will not be taken into account for the analysis."
            N2PLog._N2PLog__logger.warning(message)

            return message
        
                
        @staticmethod
        def W801() -> None:
            ''' Warning raised when trying to initialize a Property class with a wrong N2PProperty / N2PMaterial instance / user input'''
            message = f"W801: Trying to initialize a Property class with incorrect N2PProperty or N2PMaterial assignment"
            N2PLog._N2PLog__logger.warning(message)

            return message
        
        

        @staticmethod
        def W801() -> None:
            ''' Warning raised when trying to initialize a Property class with a wrong N2PProperty / N2PMaterial instance / user input'''
            message = f"W801: Trying to initialize a Property class with incorrect N2PProperty or N2PMaterial assignment"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W851() -> None:
            ''' Warning raised when no '''
            message = f"W851: NO INTEGRATION DISTANCE IS SET FOR ELEMENTS. BY DEFAULT IS SET TO THE THICKNESS OF EACH ELEMENT"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W900() -> None:
            ''' Warning raised when no GetLoadFastener object is found while calling method calculate() at N2PCalculatorRFJoints'''
            message = f"W900: GetLoadFastener property is missing, RFs cannot be calculated and only input echo will be exported"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W901(elem2d_id) -> None:
            ''' Warning raised when at N2PCompRF, the edge distance of an 2D element is not within method limits'''
            message = f"W901: SEE METHOD DOCUMENTATION (COMP ; BEARING; KDF EDGE DISTANCE EFFECT): e/d cannot be lower than 1.80, check element id:{elem2d_id}, It is assumed c_ed = (edge/3·d_nom) for this element"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W902(elem_id) -> None:
            ''' Warning raised when 2D element's property is neither PSHELL nor PCOMP'''
            message = f"W902: Element's property must be PSHELL or PCOMP, Element id: {elem_id} will be ignored"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W903(elem_id, e_d, f_bru) -> None:
            '''Warning raised when e/d is lower than 1.5 in N2PMetalRF'''
            message = f"W903: SEE METHOD DOCUMENTATION (MET ; BEARING; F_BRU): For Element id: {elem_id}, e/d = {e_d} < 1.5, f_bru is assumed to be {f_bru}"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W904(joint_id, elem_id) -> None:
            '''Warning raised when C_SRF_NS cannot be calculated and it is assumed to be 1.0 in N2PJointAnalysisParameters'''
            message = f"W904: SEE METHOD DOCUMENTATION (MET ; NET SECTION; C_SRF_NS): For Element id: {elem_id}, Joint id: {joint_id}, C_SRF_NS is assumed to be 1.00, as eta (D/W) is greater than 0.5"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W905() -> None:
            '''Warning raised when W902 has been raised in one or more elements during N2PCalculatorRFJoints execution'''
            message = f"W905: SEE LOG FILE: For one or more elements, Warning W902 has been raised"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W906() -> None:
            '''Warning raised when W905 has been raised in one or more elements during N2PCalculatorRFJoints execution'''
            message = f"W906: SEE LOG FILE: For one or more elements, Warning W905 has been raised"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W907() -> None:
            '''Warning raised when W901 has been raised in one or more elements during N2PCompRF execution'''
            message = f"W907: SEE LOG FILE: For one or more elements, Warning W901 has been raised"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W908() -> None:
            '''Warning raised when W903 has been raised in one or more elements during N2PMetalRF execution'''
            message = f"W908: SEE LOG FILE: For one or more elements, Warning W903 has been raised"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W950() -> None:
            ''' Warning raised when a non-uniaxial compression loading state is used for a uniaxial criteria'''
            message = f"W950: LOAD STATE IN SOME ELEMENTS IS DIFFERENT FROM UNIAXIAL COMPRESSION, BUT CRITERIA SELECTED APPLIES FOR UNIAXIAL COMPRESSION. CHECK VALIDITY OF THE CALCULATION"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W951() -> None:
            ''' Warning raised when tension loading state is used for a compression criteria'''
            message = f"W951: TENSION LOAD STATE USED FOR A COMPRESSION CRITERIA IN SOME ELEMENTS. RF SET TO 999999"
            N2PLog._N2PLog__logger.warning(message)

    # ------------------------------------------------------------------------------------------------------------------
    ############################################  ERROR  ###############################################################
    class Error:
        """ Class with all the errors that can be expected.

        They should be handeled by a try-exception clasule. The errors are method that do not return anything,
        they write in the log file and console the error.

        :meta private:
        """

        @staticmethod
        def user(message: str) -> None:
            """ Method prepared to be called by the user for adding errors to the loggin

            This anyone who is using NaxToPy can write in the register their
            own error message. Use the following structure as a standard message (E + four digits + Body).

            Args:
                message: str

            Example:
                "EXXXX: BODY OF THE MESSAGE"
            """
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E101() -> None:
            """ Error raised when the NaxTo libraries couldn't be found.
            """
            message = "E101: THE NAXTO LIBRARIES COULDN'T BE FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E102() -> None:
            """ Error raised when the value to set the directory where the .log file is not a string.
            """
            message = "E102: THE DIRECTORY OF THE .log MUST BE A STRING."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E103() -> None:
            """ Error raised when the value to set the file name of the .log is not a string.
            """
            message = "E103: THE FILE NAME OF THE .log MUST BE A STRING."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E104() -> None:
            """ Error raised when directory of the .log couldn't be changed.
            """
            message = "E104: THE DIRECTORY OF THE .log COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E105() -> None:
            """ Error raised when the file name of the .log couldn't be changed.
            """
            message = "E105: THE FILE NAME OF THE .log COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E106() -> None:
            """ Error raised when there is an error while closing the windows register after modifing.
            """
            message = "E106: THE WINDOWS REGISTER COULDN'T BE CLOSED PROPERLY."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E107(levellist) -> None:
            """ Error raised when the register level is intended to change and the level is not one of the possible choices.
            """
            message = f"E107: THE REGISTER LEVEL IS NOT OF THE POSSIBLE ONES ({levellist})."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E108() -> None:
            """ Error raised when the change of register level of the .log file fails.
            """
            message = f"E108: THE REGISTER LEVEL OF THE .log FILE COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E109() -> None:
            """ Error raised when the change of register level of the console fails.
            """
            message = f"E109: THE REGISTER LEVEL OF THE CONSOLE COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E110(path) -> None:
            """ Error raised when the n2ptoexe tries to createa exe from a module that dont use NaxToPy.
            """
            message = f"E110: THE MODULE IN {path} DOESN'T USE NaxToPy"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E111() -> str:
            """ Error raised when a file with an extension of a binary result file is intended to be loaded as
            nastran input text file
            """
            message = f"E111: THE FILE THAT IS INTENDED TO LOAD IS BINARY RESULT FILE, NOT A NASTRAN INPUT TEXT FILE"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E112(er) -> str:
            """ Error raised when the Windows Register couldn't be modified
            """
            message = f"E112: THE WINDOWS REGISTER COULDN'T BE MODIFIED. ERROR: {er}"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E113(file) -> str:
            """ Error raised when the Windows Register couldn't be modified
            """
            message = f"E113: THE FILE {file} DOESN'T EXIST OR COULDN'T BE FOUND"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E201(*args) -> None:
            ''' Error raised when the id of the node is not in the node dictionary.
            '''
            message = "E201: NODE " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E202(*args) -> None:
            ''' Error raised when the id of the element is not in the element dictionary.
            '''
            message = "E202: ELEMENT " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E203(*args) -> None:
            ''' Error raised when the id of the coordinate system is not in the coord dictionary.
            '''
            message = "E203: COORDINATE SYSTEM " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E204(*args) -> None:
            ''' Error raised when the id of the connector is not in the coord dictionary.
            '''
            message = "E204: CONNECTOR " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E205(*args) -> None:
            ''' Error raised when the arguments are no recognize by the function.
            '''
            message = "E205: THE INPUT '" + str(*args) + "' IS NOT RECOGNIZE."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E206(arg) -> None:
            ''' Error raised when the component don't have any results.
            '''
            message = "E206: THE COMPONENT " + str(arg) + " DON'T HAVE ANY RESULTS WITH THE SPECIFIED CONFIG."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E207(arg) -> None:
            ''' Error raised when there is not any Increment with the ID specified.
            '''
            message = f"E207: THE INCREMENT WITH THE ID {arg} DOESN'T EXIST."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E208() -> None:
            """
            Error raised when there is not any result. Some arguments may be the problem.
            """
            message = "E208: THERE IS NOT ANY RESULT WITH THE SPECIFICATION GIVEN."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E209(name) -> None:
            """
            Error raised when there is not ID for the property (Abaqus don't use ids for properties).
            """
            message = f"E209: THERE IS NOT ID FOR THE PROPERTY {name}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E210(name) -> None:
            """
            Error raised when there is not PartID for the property (Abaqus don't use ids for properties).
            """
            message = f"E210: THERE IS NOT PartID FOR THE PROPERTY {name}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E211() -> None:
            """
            Error raised when the increment asked is not an id(int) or a name(str).
            """
            message = f"E211: THE ARGUMENT FOR GET INCREMENT MUST BE A NAME(str) or an ID(int)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E212(id) -> None:
            """
            Error raised when the increment asked is found.
            """
            message = f"E212: THE INCREMENT {id} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E213(name) -> None:
            """
            Error raised when the result asked is found.
            """
            message = f"E213: THE RESULT {name} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E214() -> None:
            """
            Error raised when the result asked is not name(str).
            """
            message = f"E214: THE ARGUMENT FOR GET RESULT MUST BE A NAME(str)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E215(name) -> None:
            """
            Error raised when the component asked is not found.
            """
            message = f"E215: THE COMPONENT {name} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E216() -> None:
            """
            Error raised when the component asked is not name(str).
            """
            message = f"E216: THE ARGUMENT FOR GET COMPONENT MUST BE A NAME(str)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E217(name) -> None:
            """
            Error raised when the derived component asked is not found.
            """
            message = f"E215: THE DERIVED COMPONENT {name} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E218() -> str:
            """
            Error raised when the sections asked in the get_array function.
            """
            message = f"E218: THE SECTIONS MUST BE A LIST OF STRINGS IN THE GET ARRAY RESULT"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E219() -> str:
            """
            Error raised when the component selected is not transformable.
            """
            message = f"E219: THE COMPONET SELECTED IS NOT TRANSFORMABLE"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E220() -> str:
            """
            Error raised when there is an error during the processing of the output coord system.
            """
            message = f"E220: ERROR SELECTION THE OUTPUT COORDINATE SYSTEM"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E221(arg) -> None:
            ''' Error raised when the id of the load case is not found.
            '''
            message = F"E221: THE LOAD CASE WITH ID {arg} DOESN'T EXIST IN THE MODEL."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E222(arg) -> None:
            ''' Error raised when the NAME of the load case is not found.
            '''
            message = F"E222: THE LOAD CASE WITH NAME {arg} DOESN'T EXIST IN THE MODEL."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E223() -> None:
            ''' Error raised when the get element need the part and not only the id.
            '''
            message = F"E223: THE PART IS NEEDED AS A INPUT IN get_elements(arg). TRY USING A TUPLE: (id, part)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E224() -> None:
            ''' Error raised when the get nodes need the part and not only the id.
            '''
            message = F"E224: THE PART IS NEEDED AS A INPUT IN get_nodes(arg). TRY USING A TUPLE: (id, part)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E225() -> None:
            ''' Error raised when the get connectors need the part and not only the id.
            '''
            message = F"E225: THE PART IS NEEDED AS A INPUT IN get_connectors(arg). TRY USING A TUPLE: (id, part)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E226() -> None:
            ''' Error raised when ABD matrix is not invertible.
            '''
            message = F"E226: THE ABD MATRIX IS NOT INVERTIBLE"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E227(rep_id) -> None:
            ''' Error raised when there is a repeated ID in the properties
            '''
            message = f"E227: THE PROPERTY ID {-rep_id} IS REPEATED. ONE WILL BE SAVE WITH THE SIGN CHANGE"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E228(formula, vz_msg) -> None:
            ''' Error raised when the formula introduced for a new derived loadcase is wrong
            '''
            message = f"E228: THE FORMULA INTRODUCED TO CREATE A DERIVED LOAD CASE \"{formula}\" IS WRONG: {vz_msg}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E229(formula, vz_msg) -> None:
            ''' Error raised when the formula introduced for a new envelope loadcase is wrong
            '''
            message = f"E229: THE FORMULA INTRODUCED TO CREATE A ENVELOPE LOAD CASE \"{formula}\" IS WRONG: {vz_msg}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E230(formula, vz_msg) -> None:
            ''' Error raised when the formula introduced for a new derived component is wrong
            '''
            message = f"E230: THE FORMULA INTRODUCED TO CREATE DERIVED COMPONENT \"{formula}\" IS WRONG: {vz_msg}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E231() -> str:
            ''' Error raised when the argument "where" of load_user_coord_sys_from_csv is not "NODES" or "ELEMENTS"
            '''
            message = f"E231: THE ARGUMENT 'where' MUST BE 'ELEMENTS' OR 'NODES'"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E232(result_file) -> None:
            """Error raised when the file to import results don't exist """

            message = f"E232: The file {result_file} don't exist"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E233() -> str:
            """The filter list contains elements and the result is in nodes"""

            message = f"E233: THE `filter_list` MUST BE A LIST OF `N2PNode` AS THE RESULT IS NODES AND NOT IN ELEMENTS"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E234() -> str:
            """The filter list contains nodes and the result is in elements"""

            message = f"E234: THE `filter_list` MUST BE A LIST OF `N2PElement` AS THE RESULT IS ELEMENTS AND NOT IN NODES"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E235() -> str:
            """The filter list are not nodes or elements"""

            message = f"E235: THE `filter_list` MUST BE A LIST OF `N2PElement` OR `N2PNode`"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E236(aveNodes, supported) -> str:
            """Error when the aveNodes option is not supported"""

            message = f"E236: THE OPTION aveNodes = {aveNodes} IS NOT SUPPORTED. USE {supported}"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E237(aveSections, supported) -> str:
            """Error when the aveSections option is not supported"""

            message = f"E237: THE OPTION aveSections = {aveSections} IS NOT SUPPORTED. USE {supported}"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E238(section, actualsections) -> str:
            """Error when the sections selected don't exist"""

            message = f"E238: THE SECTION {section} DOESN'T EXIST. SECTIONS ARE {actualsections}"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E239(realPolar, supported) -> str:
            """Error when the realPolar option is not supported"""

            message = f"E239: THE OPTION realPolar = {realPolar} IS NOT SUPPORTED. USE {supported}"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E240() -> str:
            """Error when the N2PLoadCase introduced in get_result_by_LCs_Incr dont belong to the same N2PModelContent"""

            message = f"E240: THE N2PLoadCase INTRODUCED IN get_result_by_LCs_Incr DON'T BELONG TO THE N2PModelContent."
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E241(part: str) -> None:
            """Error when the specified part does not exist or contains no entities of the given type."""

            message = f"E241: THE PART {part} DOESN'T EXIST IN THE ABQUS INPUT DATA OR IT CONTAINS NO ENTITIES OF THE GIVEN TYPE."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E242(part: str, id_: int) -> None:
            """The part exists, but no entity with the given ID was found."""

            message = f"E242: THE PART {part} EXISTS, BUT NO ENTITY WITH ID {id_} WAS FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E300(args) -> None:
            ''' Error raised when the program fail to save the model (as a N2PModelContent object).
            '''
            prueba = list(locals().keys())
            message = "E300: THE MODEL {prueba} COULDN\'T BE SAVE."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E301(args) -> None:
            ''' Error raised when the extension of the file path that is intended to save is wrong.
            '''
            message = "E301: FILE {args} HAS A WRONG EXTENSION."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E302(args) -> None:
            ''' Error raised when the program faile to load the model (as a N2PModelContent object) from a .N2P file.
            '''
            message = "E302: THE MODEL COULDN'T BE LOAD FROM {args}."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E303(args) -> None:
            ''' Error raised when the extension of the file path that is intended to load is wrong.
            '''
            message = "E303: FILE {args} HAS A WRONG EXTENSION."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E304() -> None:
            ''' Error raised when NaxToPy.ico is not found.
            '''
            message = f"E304: NAXTOPYTHON ICON WAS NOT FOUND IN THE PACKAGE (icon.ico)."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E305() -> None:
            ''' Error raised when the length of the columns of the cloud of points don't macht in N2PEnvelope.
            '''
            message = f"E305: THE LENGHT OF THE DATA INCLUDED MUST HAVE THE SAME LENGTH"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E306() -> None:
            ''' Error raised when the arguments of envelope are not valid.
            '''
            message = f"E306: THE ARGUMENTS OF 'envelope' MUST BE A DATAFRAME OR LISTS"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E307() -> None:
            ''' Error raised when the dataframe of envelope has NaN values.
            '''
            message = f"E307: THE DATAFRAME ARGUMENT HAS NAN VALUES IN IT. PLEASE CHECK THE INPUTS"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E308() -> None:
            ''' Error raised when qhull library fails (wrong inputs, coplanar points, etc).
            '''
            message = f"E308: THE INNER LIBRARY FAILED (WRONG INPUTS OR COPLANAR POINTS)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E309() -> None:
            ''' Error raised when qhull library fails (wrong inputs, coplanar points, etc).
            '''
            message = f"E309: THE INNER LIBRARY FAILED (INSUFFICIENT NUMBER OF POINTS)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E310() -> None:
            ''' Error raised when the inputs list(tuple(LC, Incr)) for getting results for LC and Incr are wrong.
            '''
            message = f"E310: THE LIST OF LOAD CASES AND INCREMENTS MUST BE A A LIST OF TUPLES. THE TUPLE MUST BE " + \
                      f"(N2PLOADCASE, N2PINCREMENT) OR (INT[id_lc], INT[id_incr])"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E311() -> None:
            ''' Error raised when the sortby parameter of the N2PReport is not one of the possible ones.
            '''
            message = f"E311: THE SORTBY PARAMETER FOR A N2PREPORT MUST BE 'LC' OR 'IDS' "
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E312(lc, result) -> None:
            ''' Error raised when the components asked for the N2PReport are not found in the result of the loadcase
            '''
            message = f"E312: THE COMPONENTS ASKED FOR THE N2PREPORT ARE NOT IN THE RESULT {result} OF THE " \
                      f"LOAD CASE {lc}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E313() -> None:
            ''' Error raised when there is an error in the arguments, probably in the formulas.
            '''
            message = f"E313: THERE IS AN ERROR IN THE ARGUMENTS OF THE METHOD new_report()"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E314() -> None:
            ''' Error raised when there is an error generating the report in VizzerClasses.
            '''
            message = f"E314: INTERNAL ERROR WHILE CALCULATING THE REPORT. PLEASE, CHECK THE ARGUMENTS"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E315() -> str:
            ''' Error raised when the matrix couldn't be inverted.
            '''
            message = f"E315: THE ROTATION MATRIZ COULDN'T BE INVERTED"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def E316() -> str:
            """Error raised when the string used in N2PAbaqusInputData.get_keywords_by_type is not a valid one"""
            message = f"E316: THE STRING USED IN N2PAbaqusInputData.get_keywords_by_type() DOESN'T MATCH WITH ANY OF" \
                      f"POSSIBLES"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def E317(card: str, i: int, e: str) -> str:
            """Theres being an error modifing a card"""
            message = f"E317: AN ERROR WITH CODE {i} MODIFYING A {card} CARD OCCURED: {e}"
            N2PLog._N2PLog__logger.error(message)
            return message


        @staticmethod
        def E318() -> None:
            """ Error raised when the inputs components in get_result_by_LCs_Incr is not a string or a list of strings.
            """
            message = f"E318: THE COMPONENTS IN get_result_by_LCs_Incr MUST BE A STRING"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E319() -> None:
            """ Error raised when not all the inputs components are in N2PResult.Components
            """
            message = f"E319: A COMPONENT INTRODUCED IS NOT IN THE RESULT'S COMPONENT LIST"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E400() -> None:
            ''' Error raised when the atttribute of a N2PCard is intended to change and the new value lenght don't match
            with the previous.
            '''
            message = f"E400: THE LENGTH OF THE LIST DONT MATCH WITH THE PREVIOUS LENGTH LIST ATTRIBUTE OF A N2PCARD"
            N2PLog._N2PLog__logger.error(message)
    # ------------------------------------------------------------------------------------------------------------------

        @staticmethod
        def E311(propID) -> None:
            ''' Error raised when young modulus is not found.
            '''
            message = f"E311: YOUNG MODULUS COULD NOT BE FOUND FOR PROPERTY {propID}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E498(key) -> None:
            """ The dictionary must have the keys "D" and "E"
            """
            message = f"E498: THE DICTIONARY FOR THE FASTENERS PROPERTIES MUST HAVE THE KEY {key}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E499(method, allowed) -> None:
            """ The stifness method introduced is no allowed.
            """
            message = f"E499: THE METHOD {method} IS NOT ALLOWED. ALLOWED ARE: {allowed}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E500() -> None:
            ''' Error raised when an element not found correctly when trying to create plates.
            '''
            message = f"E500: Element not found correctly or not supported."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E501() -> None:
            ''' Error raised when a prop not found correctly or it is not supported.
            '''
            message = f"E501: Property not found correctly or not supported."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E502() -> None:
            ''' Error raised when a mat not found correctly or it is not supported.
            '''
            message = f"E502: Material not found correctly or not supported."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E503(bolt) -> None:
            ''' Error raised when fastener is said to have the Head in a middle element1D.
            '''
            message = f"E503: Bad definition of fastener {bolt.ID}: said to have the Head in a middle element1D."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E504() -> None:
            ''' Error raised when load cases/s are not found.'''
            message = f"E504: Load cases/s not found."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E505(bolt) -> None:
            ''' Error raised when a fastener is not connected to 2 plates.
            '''
            message = f"E505: Fastener {bolt.ID} was not computed because it is not connected to 2 plates."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E506(bolt) -> None:
            ''' Error raised when a fastener diameter is not defined.
            '''
            message = f"E506: Diameter not defined. Bypass calculation skipped for fastener {bolt.ID}."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E507(plate) -> None:
            ''' Error raised when iterations > max_iter.
            '''
            message = f"E507: Unable to calculate bypass loads in plate {plate.SolverID} because iterations >  Max Iterations."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E508(plate) -> None:
            ''' Error raised when there is a problem with the geometry of the plate.
            '''
            message = f"E508: Plate {plate.SolverID} was not computed because there is a problem with its geometry."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E509(bolt) -> None:
            ''' Error raised when no forces were correctly retrieved.
            '''
            message = f"E509: Fastener {bolt.ID} discarded because no forces were correctly retrieved."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E510() -> None:
            ''' Error raised when there is an error in the isoparametric transformation.
            '''
            message = f"E510: Cannot obtain u and v in isoparametric transformation."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E511() -> None:
            ''' Error raised when elements are not supported in interpolation.
            '''
            message = f"E511: Interpolation only supported for triangular and quadrilateral elements."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E512() -> None:
            ''' Error raised when the number of components of the vector and the reference systems are not multiple of 3
             in the rotation.'''
            message = f"E512: The number of components of the vector and the reference systems must be multiple of 3."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E513() -> None:
            ''' Error raised when the type is not supported.'''
            message = f"E513: Not supported type. Not serializing."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E514() -> None:
            ''' Error raised when trying to serialize something that is not a list.'''
            message = f"E514: Can only serialize lists. Not serializing."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E515() -> None:
            ''' Error raised when trying to deserialize something that is not a list.'''
            message = f"E515: Not supported type. Not deserializing."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E516() -> None:
            ''' Error raised when trying to deserialize something that is not a list.'''
            message = f"E516: Can only deserialize lists. Not deserializing."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E517(listids) -> None:
            ''' Error raised when having fasteners with wrong diameter.'''
            message = f"E517: Fasteners {listids} will not be calculated because they have a wrong or no diameter definition."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E518(solver) -> None:
            """Error raised when the solver is not supported"""
            message = f"E518: Solver {solver} is not supported."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod 
        def E519() -> None: 
            '''Error raised when all load cases are broken.'''
            message = f"E519: All load cases have missing results."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E520(attribute, instance) -> None: 
            '''Error raised when an input (as a list) has no valid elements inside.'''
            message = f"E520: Attribute {attribute} has no valid {instance} instances."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod 
        def E521() -> None: 
            '''Error raised when no model has been imported'''
            message = f"E521: No N2PModelContent has been imported."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E522() -> None: 
            '''Error raised when, in N2PGetLoadFasteners, no result files have been imported'''
            message = f"E522: No result files have been imported."
            N2PLog._N2PLog__logger.error(message) 
        
        @staticmethod
        def E523() -> None: 
            '''Error raised when, in N2PGetLoadFasteners, no N2PJoints have been imported'''
            message = f"E523: No N2PJoints have been imported."
            N2PLog._N2PLog__logger.error(message) 

        @staticmethod 
        def E524(path) -> None: 
            '''Error raised when a loaded file does not exist or is not a file'''
            message = f"E524: Path {path} does not exist or is not a file."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod 
        def E525() -> None: 
            '''Error raised when all joints are broken.'''
            message = f"E525: Every joint has problems with their geometry."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod 
        def E527() -> None: 
            '''Error raised when the used solver is not Nastran'''
            message = f"E527: Solver not supported. Try using a model with Nastran or the new N2PGetFasteners module."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod 
        def E535(input, instance) -> None: 
            '''Error raised when an input is of a wrong instance.'''
            message = f"E535: Attribute {input} is not a {instance} instance."
            N2PLog._N2PLog__logger.error(message) 
        
        @staticmethod 
        def E537() -> None: 
            '''Error raised when the first column of the dataset (ID Entity column) is not composed of integers. '''
            message = f"E537: Error raised when the first column of the dataset (ID Entity column) is not composed of integers"
            N2PLog._N2PLog__logger.error(message) 

        @staticmethod
        def E650() -> None:
            ''' Error raised when trying to assign a non isotropic material to a isotropic one'''
            message = f"E650: Action not allowed because an attempt is being made to assign a non isotropic material to an isotropic one."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E651() -> None:
            ''' Error raised when trying to assign a non orthotropic material to a orthotropic one'''
            message = f"E651: Action not allowed because an attempt is being made to assign a non orthotropic material to an orthotropic one."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E652() -> None:
            ''' Error raised when trying to assign a wrong hardening to a plastic class'''
            message = f"E652: Action not allowed because an attempt is being made to assign wrong hardening to a plastic class."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E654() -> None:
            ''' Error raised when trying to assign wrong arguments to a plastic class'''
            message = f"E654: Action not allowed because an attempt is being made to assign wrong configuration to the plastic class."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E655() -> None:
            ''' Error raised when trying to assign wrong plastic class'''
            message = f"E655: Action not allowed because an attempt is being made to assign wrong plastic class."
            N2PLog._N2PLog__logger.error(message)
        
        @staticmethod
        def E656() -> None:
            ''' Error raised when trying to assign a wrong N2PMaterial instance to a material subclass'''
            message = f"E656: Action not allowed because an attempt is being made to a wrong N2PMaterial instance to a material subclass."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E657() -> None:
            ''' Error raised when trying to get a Plastic instance which is not assigned'''
            message = f"E657: Action not allowed because an attempt is being made to get a Plastic instance which is not assigned."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E658() -> None:
            ''' Error raised when trying to set a non Plastic instance'''
            message = f"E658: Action not allowed because an attempt is being made to set a non Plastic instance."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E659() -> None:
            ''' Error raised when trying to get an Allowable instance which is not assigned'''
            message = f"E659: Action not allowed because an attempt is being made to get an Allowables instance which is not assigned."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E660() -> None:
            ''' Error raised when trying to set a non Plastic instance'''
            message = f"E660: Action not allowed because an attempt is being made to set a non Allowables instance."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E661(materialid) -> None:
            """ Error raised when trying to use the N2PNeuber module without assign a YieldStress to a material"""
            message = (f"E661: Action not allowed because an attempt is being made to use the neuber module without assign a Yield Stress to the material ID:{materialid}")
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E662(materialid) -> None:
            """ Error raised when trying to use the N2PNeuber module without assign a RO_exponent to a material"""
            message = (f"E662: Action not allowed because an attempt is being made to use the neuber module without assign a RO exponent to the material ID:{materialid}")
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E663() -> None:
            """ Error raised when trying to assign a non N2PElement list"""
            message = (f"E663: Action not allowed because an attempt is being made to assign a non N2PElement list")
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E664() -> None:
            """ Error raised when trying to assign a non N2PLoadCase list"""
            message = (f"E664: Action not allowed because an attempt is being made to assign a non N2PLoadCase list")
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E665(ele) -> None:
            """ Error raised when is not possible to find a Neuber solution"""
            message = (f"E665: Action not allowed is not possible to find a Neuber solution for the stress of the element{ele}")
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E670() -> None:
            ''' Error raised when trying to get an Allowable  instance which is not assigned'''
            message = (f"E670: Action not allowed because an attempt is being made to get an Allowables instance which"
            " is not assigned.")
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E671() -> None:
            ''' Error raised when no valid results are available'''
            message = (f"E671: Error raised when no valid results are available")
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E672(*args) -> None:
            ''' Error raised when the id of the material is not in the material dictionary.
            '''
            message = "E672: MATERIAL " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)


        @staticmethod
        def E673(*args) -> None:
            ''' Error raised when the id of the property is not in the property dictionary.
            '''
            message = "E673: PROPERTY " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)
        
        @staticmethod
        def E674(ele) -> None:
            ''' Error raised when Neuber method can not be applicated in an element.
            '''
            message = "E674: Error raised when a Neuber method can not be applicated to the ele" + str(ele)
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E675() -> None:
            ''' Error raised when a Neuber method can not be applicated in an element.
            '''
            message = "E674: Error raised when a Neuber method can not be applicated to the ele"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E700() -> None:
            ''' Error raised when trying to write in a dataset that has different data types than the one in the data entry'''
            message = f"E700: The DataEntry has different data types than the ones in the data set."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E701() -> None:
            ''' Error raised when an entity ID is not of integer type'''
            message = f"E701: The entity ID is not an integer."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E702(entityID) -> None:
            ''' Error raised when, in a dataset, one tries to write a row whose entity ID is already in the dataset'''
            message = f"E702: The entity ID {entityID} is already in the dataset."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E703() -> None:
            ''' Error raised when dataset introduced in HDF5 is not an nparray or a string'''
            message = f"E703: DATASET MUST BE A NUMPY ARRAY OR A STRING"
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E800() -> None:
            ''' Error raised when a module (Failure Aanlysis) is initialized with a wrong model assignment. '''
            message = f"E800: Assigned model input must be a N2PModelContent instance."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E801() -> None:
            ''' Error raised when a module (Failure Analysis) is initialized with a wrong Element list assignment. '''
            message = f"E801: Invalid Element assignmet to Elements attribute."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E802() -> None:
            ''' Error raised when a module (Failure Analysis) is initialized with a wrong LoadCase list assignment. '''
            message = f"E802: Invalid Load Case assignment to LoadCases attribute."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E803(criteria, criteria_dict:dict) -> None:
            ''' Error raised when a Failure Criterion assigned by user is not supported by module computations. '''
            message = f"E803: {criteria} is not a Criterion supported by N2PFailureComposites. Available Criteria are {criteria_dict.keys()}. "
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E804() -> None:
            ''' Error raised when a Failure Criterion analysis is trying to be launched and Material Instances have not their
            Allowable values assigned yet.'''
            message = f"E804: Trying to perform Failure Analysis without assigning Failure Threshold"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E805() -> None:
            ''' Error raised when trying to initialize a Property class with a wrong N2PProperty / N2PMaterial instance / user input'''
            message = f"E805: Trying to initialize a Property class with incorrect N2PProperty or N2PMaterial assignment"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E806() -> None:
            ''' Error raised when trying to initialize a CompositeShell subclass with non-composite N2PProperty instance'''
            message = f"E806: Trying to initialize a CompositeShell instance with non-composite N2PProperty"
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E900(joint_id) -> None:
            ''' Error raised when no FastenerSystem is found while trying to create and N2PJointAnalysisParameters object'''
            message = f"E900: Joint id:{joint_id} has no FastenerSystem assigned, its property JointAnalysisParameters is not created."
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E901(parameter,correct_value,default) -> None:
            ''' Error raised when the user does not introduce a valid parameter when 
            running the elements_manager_filter method at N2PCalculatorRFJoints'''
            message = f"E901: elements_manager_filter {parameter} must be {correct_value}, {parameter}={default} is used instead (default)."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E902(parameter,correct_value) -> None:
            ''' Error raised when the user does not introduce the appropiate data type to a 
            N2PJointAnalysisParameter property'''
            message = f"E902: JointAnalysisParameter {parameter} must be {correct_value}, no changes are applied."
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E903(parameter,text) -> None:
            ''' Error raised when the user does not introduce the appropiate data size to a 
            JointAnalysisParameter property'''
            message = f"E903: JointAnalysisParameter {parameter} {text}, no changes are applied."
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E904(joint_id) -> None:
            ''' Error raised when N2PCompRF finds a not valid TShim for the INDUSTRIAL method'''
            message = f"E904: SEE METHOD DOCUMENTATION (COMP_Bearing): for Joint Id: {joint_id} " + \
                        "tshim must be lower or equal to 2.5mm for INDUSTRIAL METHOD, tshim=2.5 is set"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E905() -> None:
            ''' Error raised when N2PCalculatorRFJoints does not find Pandas to write the requested element filter print excel file'''
            message = f"E905: Pandas library is not installed, please install it or set Table_Print = 'CSV', Analysis elements are" + \
                        " printed in CSV format as EXCEL option cannot be used"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def E906() -> None:
            ''' Error raised when N2PCalculatorRFJoints does not find Pandas to write the requested RF excel file'''
            message = f"E906: Pandas library is not installed, please install it or do not use 'RF_min_and_LC_to_EXCEL()'"
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E907(joint_id, element_id) -> None:
            ''' Error raised when net-section allowable calculation has failed in N2PMetalRF class'''
            message = f"E907: SEE METHOD DOCUMENTATION (METAL_Net Section): for Joint Id: {joint_id}, element Id: {element_id}, Anet/Agross is negative"
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E908() -> None:
            ''' Error raised when Error E900 has been raised for one or more elements during N2PCalculatorRFJoints execution'''
            message = f"E908: SEE LOG FILE: For one or more elements, Error E900 has been raised"
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E909() -> None:
            ''' Error raised when Error E904 has been raised for one or more elements during N2PCompRF execution'''
            message = f"E909: SEE LOG FILE: For one or more elements, Error E904 has been raised"
            N2PLog._N2PLog__logger.error(message)

            return message
        
        @staticmethod
        def E910() -> None:
            ''' Error raised when Error E907 has been raised for one or more elements during N2PMetalRF execution'''
            message = f"E910: SEE LOG FILE: For one or more elements, Error E907 has been raised"
            N2PLog._N2PLog__logger.error(message)

            return message
        
    ###########################################  CRITICAL  #############################################################
    class Critical:
        """Class with all the critical errors.

        The critical are methods that do not return anything, they write in the log file and console the error.
        Optionally a raise Exception could be added. Always a sys.exit() should be executed at the end.

        :meta private:
        """

        @staticmethod
        def user(message: str) -> None:
            """
            Method prepared to be called by the user for adding CRITICAL errors to the loggin.
            
            Method prepared to be called by the user for adding CRITICAL errors to the loggin.
            

            Anyone who is using NaxToPy can write in the register their own CRITICAL error message.
            Use the following structure as a standard message (C + four digits + Body).

            Args:
                message: str

            Example:
                "CXXXX: BODY OF THE MESSAGE"
            """
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C001(message):
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C100(path, error) -> str:
            """ Critical error raised when the model couldn't be initialized.
            """
            message = f"C100: THE MODEL IN THE FILE {path} COULDN'T BE INITIALIZED. (Vizzer Error: {error})"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C101(error) -> str:
            """ Critical error raised when the mesh couldn't be generated.
            """
            message = f"C101: THE MESH COULDN'T BE GENERATED. (Vizzer Error: {error})"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C102(py_version) -> str:
            """ Critical Error raised when the current python version is not supported.
            """
            message = f"C102: THE CURRENT PYTHON VERSION ({py_version}) IS NOT SUPPORTED."
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C103() -> str:
            """ Critical Error raised when VizzerClasses.dll is not properly load.
            """
            message = f"C103: THE LIBRARY 'NaxToModel.dll' COULDN'T BE LOADED CORRECTLY"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C104() -> str:
            """ Critical Error raised when the console argument in n2ptoexe is not a bool type.
            """
            message = f"C104: THE ARGUMENT CONSOLE MUST BE A BOOLEAN: True | False"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C105(directions) -> None:
            """ Critical Error raised when the argument abaqus version in n2ptoexe is wrong or not supported.
            """
            message = f"C105: THE ARGUMENT ABAQUSVERSION MUST BE ONE OF THE AVIABLE: {directions}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C106() -> str:
            """ Critical Error raised when the pyinstaller is not installed and it couldn´t be downloaded.
            """
            message = f"C106: THE PACKAGE PyInstaller COULDN'T BE LOADED. PLEASE INSTALL IT MANUALLY"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C107() -> str:
            """ Error raised when the NaxTo libraries couldn't be found.
            """
            message = "C107: THE NAXTO LIBRARIES COULDN'T BE FOUND. PLEASE, INSTALL NAXTO"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C108(path) -> str:
            """ Error raised when the file couldn't be found.
            """
            message = f"C108: THE FILE {path} DOESN'T EXIST"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C109(ver, comp_ver) -> None:
            """ Error raised when NaxTo is not compatible with NaxToPy.
            """
            message = f"C109: THIS VERSION OF NAXTOPY ({ver}) IS NOT COMPATIBLE WITH THIS ASSEMBLY VERSION: {comp_ver}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C110(ver, naxver) -> str:
            """ Error raised when there aren't installed a compatible version of  with minor changes.
            """
            message = (f"C110: THIS VERSION OF NAXTOPY({ver}) IS NOT COMPATIBLE WITH THE NAXTO VERSIONS THAT ARE INSTALLED.\n"
                       f"\tUPDATE TO A COMPATIBLE NAXTO VERSION ({naxver}) OR DOWNLOAD FROM https://pypi.org/project/NaxToPy/ A COMPATIBLE NAXTOPY VERSION")
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C111(ver) -> None:
            """ Error raised when there version of NaxTo is not found.
            """
            message = f"C111: NAXTO VERSION WAS NOT FOUND. PLEASE, CHECK IF NAXTO{ver} IS INSTALLED"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C112() -> str:
            """ Error raised when there is an Elements safearray error in VizzerClasses (Vizzer Error: -1003). This
            error could happen when the memory of the processor tthat call the low level libraries has a leak (is not
            correctly erased). A solution may be change the initialize method to parallel.
            """
            message = f"C112: ERROR RAISED WHEN THERE IS AN ERROR IN THE SA OF ELEMENTS. THIS MAY BE CAUSED BY A MEMORY" \
                      f"LEAK IN THE LOW LEVEL LIBRERIES. A SOLUTION MAY BE CHANGE THE \"initilaize\" method to parallel:" \
                      f"model = NaxToPy.load_model(path, parallelprocessing=True)"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C113(lib, ver, listver) -> str:
            """ Error raised when the NaxToPy versions the dll is compatible with is not this one
            """
            message = f"C113: THE LIBRARY {lib} IS NOT COMPATIBLE WITH NAXTOPY {ver}. INSTALL ANY OF THESE VERSION OF" \
                      f"NAXTOPY {listver} OR UPDATE NAXTO"
            N2PLog._N2PLog__logger.critical(message)
            return message
        
        @staticmethod
        def C114(path) -> str:
            """ Register gave a path to a file that doen't exist
            """
            message = f"C114: THE FILE THE IN THE PATH THE REGISTER GAVE DOESN'T EXIST: {path}"
            N2PLog._N2PLog__logger.critical(message)
            return message

        @staticmethod
        def C200() -> None:
            """ Critical error raised when numpy couldn't be installed.
            """
            message = "C200: NUMPY PACKAGE COULDN\'T BE INSTALLED. PLEASE, INSATALL IT MANUALY."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C201() -> None:
            """ Critical error raised when the type of the argument of N2PAbaqusInputData.get_keywords_by_type is not a
            string.
            """
            message = "C201: THE ARGUMENT FOR N2PAbaqusInputData.get_keywords_by_type() MUST BE A STRING"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C500() -> None:
            """ Critical error raised when numpy couldn't be installed.
            """
            message = "C500: SOLVER NOT SUPPORTED."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod 
        def C520() -> None: 
            '''Critical error raised when all load cases are broken.'''
            message = f"C520: ALL LOAD CASES HAVE MISSING RESULTS."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C661() -> None:
            """Critical Error raised when trying to use the N2PNeuber module without assign a YieldStress to a material"""
            message = (f"C661: Action not allowed because an attempt is being made to use the neuber module without assign a Yield Stress to a material")
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C662() -> None:
            """Critical Error raised when trying to use the N2PNeuber module without assign a RO_exponent to a material"""
            message = (f"C662: Action not allowed because an attempt is being made to use the neuber module without assign a RO exponent to a material")
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C663() -> None:
            """Critical Error raised when trying to assign a non N2PElement list"""
            message = (f"C663: Action not allowed because an attempt is being made to assign a non N2PElement list")
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C664() -> None:
            """Critical Error raised when trying to assign a non N2PLoadCase list"""
            message = (f"C664: Action not allowed because an attempt is being made to assign a non N2PLoadCase list")
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C800() -> None:
            ''' Critical Error raised when a module (Failure Analysis) is initialized with a wrong model assignment. '''
            message = f"C800: Assigned model input must be a N2PModelContent instance."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C801() -> None:
            ''' Critical Error raised when a module (Failure Analysis) is initialized with a wrong Element list assignment. '''
            message = f"C801: Invalid Element assignmet to Elements attribute."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C802() -> None:
            ''' Critical Error raised when a module (Failure Analysis) is initialized with a wrong LoadCase list assignment. '''
            message = f"C802: Invalid Load Case assignment to LoadCases attribute."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C850() -> None:
            '''Critical Error raised when the IntegrationDistance is not a dictionary'''
            message = f"C850: INTEGRATION DISTANCE MUST BE A DICT MAPPING EACH N2PELEMENT WITH ITS CORRESPONDING INTEGRATION DISTANCE"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C851(key) -> None:
            '''Critical Error raised when key of IntegrationDistance is not a N2PElement instance'''
            message = f"C851: KEY '{key}' IS NOT A N2PELEMENT INSTANCE"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C852(value, key) -> None:
            '''Critical Error raised when key of IntegrationDistance is not a float'''
            message = f"C852: INTEGRATION DISTANCE '{value}' FOR ELEMENT {key} IS NOT A FLOAT"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C853() -> None:
            '''Critical Error raised when the FailureCriteria is not a valid criteria'''
            message = f"C853: FAILURE CRITERIA MUST BE 'MI','TI' OR 'CI'"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C854(material) -> None:
            '''Critical Error raised when Material is not a Orthotropic instance'''
            message = f"C854: MATERIAL {material} IS NOT AN ORTHOTROPIC INSTANCE"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C855() -> None:
            '''Critical Error raised when Ez, PoissonXZ or PoissonYZ are not defined'''
            message = f"C855: YOUNGZ, POISSONXZ AND POISSONYZ MUST BE DEFINED"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C856() -> None:
            '''Critical Error raised when convergence is not reached in optimization process'''
            message = f"C856: OPTIMIZATION DID NOT CONVERGE WITHIN THE MAXIMUM NUMBER OF ITERATIONS."
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C857(material) -> None:
            ''' Critical Error raised when allowables are not defined'''
            message = f"C857: ALLOWABLES FOR MATERIAL {material} MUST BE DEFINED"
            N2PLog._N2PLog__logger.error(message)

            return message
        @staticmethod
        def C858() -> None:
            '''Critical Error raised when load case list is not defined'''
            message = f"C858: LOAD CASES LIST MUST BE DEFINED"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C859() -> None:
            '''Critical Error raised when element list is not defined'''
            message = f"C859: ELEMENT LIST MUST BE DEFINED"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C860(solver) -> None:
            ''' Critical Error raised when module is not available for a given solver'''
            message = f"C860: MODULE NOT AVAILABLE FOR SOLVER {solver}"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C861() -> None:
            '''Critical Error raised when solver is not one of the availables for the module'''
            message = f"C861: PROPERTIES OF THE ELEMENTS MUST BE COMPOSITESHELL"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C900(property,correct_type) -> None:
            """ Critical error raised when the user does not introduce the appropiate data to a 
            FastenerSystem property.
            """
            message = f"C900:{property} must be {correct_type}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C901(property,correct_type) -> None:
            """ Critical error raised when the user does not introduce the appropiate data to a 
            CalculatorRFJoints property.
            """
            message = f"C901:{property} must be {correct_type}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C902() -> None:
            """ Critical error raised when the user does not introduce a N2PGetFasteners object
            before calling the elements_manager_filter method in N2PCalculatorRFJoints class.
            """
            message = f"C902: GetFastener property is empty, elements_manager_filter cannot start"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C903(parameter,joint_id) -> None:
            """ Critical error raised when a specific N2PFastenerSystem parameter is missing for RF calculation.
            """
            message = f"C903: {parameter} is missing for FastenerSystem of N2PJoint id: {joint_id}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C904() -> None:
            """ Critical error raised when the user asks for outputs but does not define the ExportLocation property at N2PCalculatorRFJoints.
            """
            message = f"C904: ExportLocation property is not defined, N2PCalculatorRFJoints cannot print outputs."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C905(parameter, prop_id) -> None:
            """ Critical error raised when any metallic material parameter is not defined and class N2PMetalRF fails.
            """
            message = f"C905: Metallic Material {parameter} is not defined por Prop id: {prop_id}."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C906(prop_id) -> None:
            """ Critical error raised when PTAllowable cannot be obtained in N2PCompRF class due to an user input missing parameter.
            """
            message = f"C906: Composite Property id: {prop_id} has no PTAllowable defined. (See documentation)"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C907(parameter, prop_id) -> None:
            """ Critical error raised when any composite laminate property parameter is not defined and class N2PCompRF fails.
            """
            message = f"C907: Composite Property {parameter} is not defined por Prop id: {prop_id}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C908() -> None:
            """ Critical error raised when RF output is requested but no N2PGetLoadFasteners has been provided.
            """
            message = f"C908: RF output cannot be created if N2PGetLoadFasteners has not been provided."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C950() -> None:
            ''' Critical Error raised when YoungZ is not defined'''
            message = f"C950: YOUNG MODULUS IN Z-DIRECTION MUST BE FILLED"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C951(failure_mode) -> None:
            ''' Critical Error raised when failure mode is not one of the allowed'''
            if failure_mode is None:
                message = f"C951: FAILURE MODE IS A MANDATORY INPUT"
            else:
                message = f"C951: FAILURE MODE {failure_mode} NOT ACCEPTED"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C952(failure_theory) -> None:
            ''' Critical Error raised when failure theory is not one of the allowed'''
            if failure_theory is None:
                message = f"C952: FAILURE THEORY IS A MANDATORY INPUT"
            else:
                message = f"C952: FAILURE THEORY {failure_theory} NOT ACCEPTED"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C953(core_type) -> None:
            ''' Critical Error raised when failure theory is not one of the allowed'''
            message = f"C953: CORE TYPE {core_type} NOT ACCEPTED"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C954(failure_mode, failure_theory) -> None:
            ''' Critical Error raised when failure mode is not one of the allowed for a given failure theory'''
            message = f"C954: FAILURE MODE {failure_mode} NOT COMPATIBLE WITH FAILURE THEORY {failure_theory}"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C955() -> None:
            ''' Critical Error raised when cell size is not set'''
            message = f"C955: CELL SIZE MUST BE DEFINED FOR DIMPLING FAILURE MODE"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C956() -> None:
            ''' Critical Error raised when ZCompressive allowable is not defined'''
            message = f"C956: Z-COMPRESSIVE ALLOWABLE MUST BE DEFINED FOR CORE STRENGTH CALCULATIONS"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C957() -> None:
            ''' Critical Error raised when ShearXZ allowable is not defined'''
            message = f"C957: SHEAR XZ ALLOWABLE MUST BE DEFINED FOR CORE STRENGTH CALCULATIONS"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C958() -> None:
            ''' Critical Error raised when ShearYZ allowable is not defined'''
            message = f"C958: SHEAR YZ ALLOWABLE MUST BE DEFINED FOR CORE STRENGTH CALCULATIONS"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C959() -> None:
            ''' Critical Error raised when CellSize is defined for a core which is not HoneyComb'''
            message = f"C959: CELL SIZE MUST BE ASSIGNED TO A HONEYCOMB TYPE CORE"
            N2PLog._N2PLog__logger.error(message)

            return message

        @staticmethod
        def C960() -> None:
            ''' Critical Error raised when Core is not alligned with 0º material orientation'''
            message = f"C960: CORE MUST BE ALLIGNED WITH X-AXIS OF MATERIAL SYSTEM"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C961() -> None:
            ''' Critical Error raised when thin face assumption is not satisfied'''
            message = f"C961: RATIO CORE-TO-FACE THICKNESS MUST BE GREATER THAN 5.77 (THIN FACE ASSUMPTION). CHECK DOCUMENTATION"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C962() -> None:
            ''' Critical Error raised when Core Type is not honeycomb for dimpling mode'''
            message = f"C962: CORE TYPE FOR DIMPLING FAILURE MODE MUST BE HONEYCOMB"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C963(laminate_criteria) -> None:
            ''' Critical Error raised when laminate failure criteria is not one of the allowed'''
            message = f"C963: LAMINATE FAILURE CRITERIA {laminate_criteria} NOT ACCEPTED"
            N2PLog._N2PLog__logger.error(message)

            if laminate_criteria is None:
                message = f"C953: LAMINATE FAILURE CRITERIA IS MANDATORY FOR FACESHEET FAILURE WITH ORTHOTROPIC MATERIALS"
            else:
                message = f"C953: LAMINATE FAILURE CRITERIA {laminate_criteria} NOT ACCEPTED"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C964() -> None:
            ''' Critical Error raised when cell size is not coarse enough to supress local buckling modes'''
            message = f"C964: GLOBAL BUCKLING ANALYSIS CANNOT BE PERFORMED SINCE THE CELL SIZE IS NOT COARSE ENOUGH TO SUPRESS LOCAL BUCKLING MODES"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C965() -> None:
            ''' Critical Error raised when a load case has results different from static in a static-request failure mode'''
            message = f"C965: LOAD CASES MUST REQUEST STATIC RESULTS "
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C966() -> None:
            ''' Critical Error raised when a load case does not request FORCES'''
            message = f"C966: FORCES MUST BE REQUESTED FOR THE SELECTED FAILURE MODE"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C967() -> None:
            ''' Critical Error raised when buckling results are not requested'''
            message = f"C967: BUCKLING RESULTS MUST BE REQUESTED FOR THE SELECTED FAILURE MODE"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C968() -> None:
            ''' Critical Error raised when ramp radius is not positive'''
            message = f"C968: RAMP RADIUS MUST BE POSITIVE"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C969() -> None:
            ''' Critical Error raised when bag angle is not between 0 and 360'''
            message = f"C969: LOCAL ANGLE BETWEEN BAG AND TOOL MUST BE BETWEEN 0 AND 360"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def C970() -> None:
            ''' Critical Error raised when ramp radius is not defined'''
            message = f"C970: RAMP RADIUS MUST BE DEFINED FOR FLATWISE TENSION FAILURE MODE"
            N2PLog._N2PLog__logger.error(message)
            return message
        
        @staticmethod
        def C971() -> None:
            ''' Critical Error raised when bag angle is not defined'''
            message = f"C971: LOCAL ANGLE BETWEEN BAG SIDE AND TOOL SIDE MUST BE DEFINED FOR FLATWISE TENSION FAILURE MODE"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C972() -> None:
            ''' Critical Error raised when weak core assumption is not satisfied'''
            message = f"C972: WEAK CORE ASSUMPTION IS NOT SATISFIED. CHECK DOCUMENTATION"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C973() -> None:
            ''' Critical Error raised when allowable displacement is negative'''
            message = f"C973: ALLOWABLE DISPLACEMENT MUST BE POSITIVE"
            N2PLog._N2PLog__logger.error(message)
            return message

        @staticmethod
        def C974() -> None:
            ''' Critical Error raised when allowable displacement is not defined'''
            message = f"C974: ALLOWABLE DISPLACEMENT MUST BE DEFINED FOR PANEL STIFFNESS CRITERIA"
            N2PLog._N2PLog__logger.error(message)
            return message
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##################  METODOS GETTER Y SETTER PARA USAR LOS ATRIBUTOS COMO PROPIEDADES  ##############################
    ####################################################################################################################

    # Nota: Estos metodos cambian los atributos del objeto que se ha instanciado como clase N2PLog y que se
    #       ha guardado dentro del atributo _ De ahí que estos metodos no vayan como propiedades.

    # Metodo para obtener directorio donde se guarda el archivo.log ----------------------------------------------------
    @classmethod
    def get_directory(cls) -> str:
        """Method that returns the folder where the .log file is being saved"""
        return cls.__directory

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para declarar directorio donde se guarda el archivo.log ---------------------------------------------------
    @classmethod
    def set_directory(cls, value: str) -> None:
        """Method that sets the folder where the .log file must be saved

        Args:
            value: str -> Path to the folder where the .log must be saved.

        """
        if isinstance(value, str):
            cls.__directory = value
            cls.__path = os.path.join(cls.__directory, cls.__filename)
            cls.__fh.path = cls.__path
        else:
            cls.Error.E102()

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar el nivel de registro del fichero .log---------------------------------------------------------
    @classmethod
    def set_file_level(cls, flv: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]) -> None:
        """ Method to set a different level for the file .log of the register. The default level is "INFO". Only The level
register and higher will be printed in the .log file. Higher levels could make more difficult to track errors.
The possible levels are:

    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        """
        if flv in cls.LevelList:
            if flv == "DEBUG":
                flevel = logging.DEBUG
            elif flv == "WARNING":
                flevel = logging.WARNING
            elif flv == "ERROR":
                flevel = logging.ERROR
            elif flv == "CRITICAL":
                flevel = logging.CRITICAL
            else:
                flevel = logging.INFO

            try:
                if flv in ["WARNING", "ERROR", "CRITICAL"]:
                    cls.Warning.W101()
                cls.__flevel = flevel
                cls.__fh.setLevel(cls.__flevel)
                #cls._N2PLog__logger.addHandler(cls.__fh)
            except:
                cls.Error.E108()

        else:
            cls.Error.E107(cls.LevelList)

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar el nivel de registro por consola -------------------------------------------------------------
    @classmethod
    def set_console_level(cls, clv: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]) -> None:
        """ Method to set a different level for console register. The default level is "WARNING". Only The level
register and higher will be printed in the console.
The possible levels are:

    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        """
        if clv in cls.LevelList:
            if clv == "DEBUG":
                clevel = logging.DEBUG
            elif clv == "WARNING":
                clevel = logging.WARNING
            elif clv == "ERROR":
                clevel = logging.ERROR
            elif clv == "CRITICAL":
                clevel = logging.CRITICAL
            else:
                clevel = logging.INFO

            try:
                cls.__clevel = clevel
                cls.__ch.setLevel(cls.__clevel)
                cls._N2PLog__logger.addHandler(cls.__ch)
            except:
                cls.Error.E109()

        else:
            cls.Error.E107(cls.LevelList)

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del archivo.log --------------------------------------------------------------------
    @classmethod
    def get_file_name(cls) -> str:
        """Method that returns the name of the file of the .log"""
        return cls.__filename

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar el nombre del archivo.log --------------------------------------------------------------------
    @classmethod
    def set_file_name(cls, value: str) -> None:
        """Method that sets the name of the file of the .log
        
        Args:
            value: str -> Name of the .log file

        """
        if isinstance(value, str):
            try:
                cls.__filename = value
                cls.__path = os.path.join(cls.__directory, cls.__filename)
                cls.__fh.path = cls.__path
            except:
                cls.Error.E105()

        else:
            cls.Error.E103()

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar desactivar la generación del archivo .log-----------------------------------------------------
    @classmethod
    def deactivate_log(cls) -> None:
        """Method that deactivates the .log"""
        cls.__fh.active = False

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar activar la generación del archivo .log-----------------------------------------------------
    @classmethod
    def activate_log(cls) -> None:
        """Method that activates the .log"""
        cls.__fh.active = True
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def _set_format1(cls) -> None:
        cls.__formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)-5s", "%H:%M:%S")
        cls.__fh.setFormatter(cls.__formatter)
        cls.__logger.addHandler(cls.__fh)

    @classmethod
    def _set_format2(cls, time) -> None:
        if len(time) < 8:
            time = "0" + time
        cls.__formatter = logging.Formatter(f"{time} %(levelname)-8s %(message)-5s")
        cls.__fh.setFormatter(cls.__formatter)
        cls.__logger.addHandler(cls.__fh)
# ----------------------------------------------------------------------------------------------------------------------