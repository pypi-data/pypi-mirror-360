from NaxToPy.Core.Constants import Constants
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry
from NaxToPy import N2PLog
import h5py 
import time
import numpy as np
import io
from numpy import ndarray
import ast
class HDF5_NaxTo: 

    # H5F5 constructor ------------------------------------------------------------------------------------------------- 
    def __init__(self): 

        """
        Class that represents one .HDF5 file. 

        Attributes: 
            file: HDF5 file created, either in disk or in memory. 
            memory_file_boolean: bool = True -> boolean that shows if the file is created in disk or in memory. 
            file_path: str -> path in which the file will be created in disk. 
            file_description: str -> file description. 

        The file is structured in the following way: 
            File -> NaxTo -> Results -> Load Case -> Increment -> Results Name -> Section -> Data dataset (a different
        dataset is created for each part). 
        """
        self._file = None
        self._memory_file_boolean: bool = True
        self._file_path: str = None 
        self._file_description: str = None
        self._part_name: str = None
    # ------------------------------------------------------------------------------------------------------------------
    
    # Getters ----------------------------------------------------------------------------------------------------------
    @property
    def FilePath(self) -> str: 
        return self._file_path 
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def FileDescription(self) -> str: 
        return self._file_description
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def File(self):
        return self._file
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def MemoryFile(self) -> bool:
        return self._memory_file_boolean
    # ------------------------------------------------------------------------------------------------------------------


    
    # Setters ----------------------------------------------------------------------------------------------------------
    @FilePath.setter 
    def FilePath(self, value: str) -> None: 
        if type(value) == str: 
            self._file_path = value
            self._memory_file_boolean = False
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @FileDescription.setter 
    def FileDescription(self, value: str) -> None: 
        if type(value) == str: 
            self._file_description = value 
        else: 
            N2PLog.Warning.W527(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @MemoryFile.setter
    def MemoryFile (self, value: bool) -> None:
        self._memory_file_boolean = value
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to create an HDF5 file -------------------------------------------------------------------------------
    def create_hdf5(self) -> None:

        """
        Method used to create an HDF5 file, either in disk (if the FilePath attribute has been filled in), or in memory 
        (if the FilePath boolean attribute has not been filled in). This file will have the following default attributes: 
            - "SOFTWARE", which will always be "NAXTO". 
            - "DESCRIPTION", which will be the FileDescription attribute (if it has been set). 
            - "CREATION_DATE", which will be the exact date when this function is called. Its structure will be 
                HH:MM:SS, DD-MM-YYYY    <==>    hour:minutes:seconds, day-month-year

        Then, a first group will be created, called "NAXTO", with the following attributes: 
            - "VERSION", which will be the NaxTo version used. 
            - "ASSEMBLY", which will be the NaxToPy version used.
            
        Finally, a second group will be created inside the "NAXTO" group, called "RESULTS", which will be empty and 
        should be filled with data written in the "write_dataset()" function. 
        """

        if self._memory_file_boolean == True:
            self._file = io.BytesIO()
        else:
            self._file = self.FilePath
        with h5py.File(self._file, "w") as hdf:
            hdf.attrs["SOFTWARE"] = "NAXTO"
            if self.FileDescription:
                hdf.attrs["DESCRIPTION"] = self.FileDescription
            t = time.asctime()
            hdf.attrs["CREATION_DATE"] = t[11:19] + ", " + str(time.gmtime()[2]) + "-" + t[4:7] + "-" + t[20:24]
    
            naxto = hdf.create_group("NAXTO")
            naxto.attrs["VERSION"] = Constants.NAXTO_VERSION
            naxto.attrs["ASSEMBLY"] = Constants.VERSION

            inputs = naxto.create_group("INPUTS")
            results = naxto.create_group("RESULTS") 
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to write a dataset -----------------------------------------------------------------------------------
    def write_dataset(self, dataEntryList: list[DataEntry]) -> None: 
        hierarchy = {} 
        for dataEntry in dataEntryList: 
            if not all({dataEntry.ResultsName, dataEntry.LoadCase is not None, dataEntry.Increment is not None, 
                        dataEntry.Section, dataEntry.Part, dataEntry.Data is not None}): 
                N2PLog.Warning.W700()
                dataEntryList.remove(dataEntry)
                continue
            part_name = str(ast.literal_eval(dataEntry.Part)[0])
            pathKey = (str(dataEntry.LoadCase), str(dataEntry.Increment), dataEntry.ResultsName, dataEntry.Section, 
                       part_name)
            if pathKey not in hierarchy: 
                hierarchy[pathKey] = [] 
            hierarchy[pathKey].append(dataEntry)
        with h5py.File(self._file, "a") as hdf: 
            naxto = hdf["NAXTO"]
            results = naxto["RESULTS"]
            for pathKey, dataEntry in hierarchy.items(): 
                loadCaseName, incrementName, resultsNameName, sectionName, partName = pathKey 
                loadCase = results.require_group(loadCaseName)
                increment = loadCase.require_group(incrementName) 
                resultsName = increment.require_group(resultsNameName)
                section = resultsName.require_group(sectionName)
                firstEntry = dataEntry[0]
                loadCase.attrs.update({"DESCRIPTION": firstEntry.LoadCaseDescription, "ID": firstEntry.LoadCase, 
                                       "SUBTITLE": firstEntry.LoadCaseName, "SOLUTION_TYPE": np.int32(1)})
                increment.attrs.update({"DESCRIPTION": firstEntry.IncrementDescription, 
                                        "VALUE": firstEntry.IncrementValue, "ID": firstEntry.Increment})
                resultsName.attrs.update({"DESCRIPTION": firstEntry.ResultsNameDescription, 
                                          "TYPE": firstEntry.ResultsNameType})
                section.attrs.update({"DESCRIPTION": firstEntry.SectionDescription})
                combinedData = np.concatenate([entry.Data for entry in dataEntry])
                l = len(combinedData)
                dtype = combinedData.dtype 
                if partName in section: 
                    data = section[partName]
                    if data.dtype == dtype: 
                        s = data.shape[0]
                        data.resize(s + l, axis = 0)
                        data[s:] = combinedData
                    else: 
                        N2PLog.Error.E700()
                        continue
                else: 
                    data = section.create_dataset(partName, shape = (l,), maxshape = (None,), chunks = (min(l, 1024),), 
                                                  compression = "gzip", compression_opts = 4, dtype = dtype, 
                                                  shuffle = True)
                    data.attrs["DESCRIPTION"] = firstEntry.DataDescription 
                    data.attrs["PART"] = firstEntry.Part 
                    data[:] = combinedData
    # ------------------------------------------------------------------------------------------------------------------


    # # Method used to write a dataset -----------------------------------------------------------------------------------
    # def write_dataset(self, dataEntryList: list[DataEntry]) -> None:
    #     """
    #     Método optimizado para escribir en un archivo HDF5 con mayor eficiencia.
    #     """
    #     with h5py.File(self._file, "a") as hdf:
    #         naxto = hdf["NAXTO"]
    #         results = naxto["RESULTS"]

    #         for dataEntry in dataEntryList:
    #             if not all([
    #                 dataEntry.ResultsName, dataEntry.LoadCase is not None,
    #                 dataEntry.Increment is not None, dataEntry.Section,
    #                 dataEntry.Part, dataEntry.Data is not None
    #             ]):
    #                 N2PLog.Warning.W700()
    #                 continue
                
    #             l = len(dataEntry.Data)
    #             aux = ast.literal_eval(dataEntry.Part)  # Evitar eval
    #             self._part_name = aux[1]
    #             dtype = dataEntry.Data.dtype  # Evitar accesos repetidos
                
    #             lc_name = str(dataEntry.LoadCase)
    #             if lc_name in results:
    #                 lc = results[lc_name]
    #             else:
    #                 lc = results.create_group(lc_name)

    #             lc.attrs.setdefault("DESCRIPTION", dataEntry.LoadCaseDescription)
    #             lc.attrs.setdefault("ID", dataEntry.LoadCase)
    #             lc.attrs.setdefault("SUBTITLE", dataEntry.LoadCaseName)
    #             lc.attrs.setdefault("SOLUTION_TYPE", np.int32(1))

    #             # Mismo procedimiento para 'increment'
    #             increment_name = str(dataEntry.Increment)
    #             if increment_name in lc:
    #                 increment = lc[increment_name]
    #             else:
    #                 increment = lc.create_group(increment_name)

    #             increment.attrs.setdefault("DESCRIPTION", dataEntry.IncrementDescription)
    #             increment.attrs.setdefault("VALUE", dataEntry.IncrementValue)
    #             increment.attrs.setdefault("ID", dataEntry.Increment)

    #             # Mismo procedimiento para 'resultsName'
    #             results_name = dataEntry.ResultsName
    #             if results_name in increment:
    #                 resultsName = increment[results_name]
    #             else:
    #                 resultsName = increment.create_group(results_name)

    #             resultsName.attrs.setdefault("DESCRIPTION", dataEntry.ResultsNameDescription)
    #             resultsName.attrs.setdefault("TYPE", dataEntry.ResultsNameType)

    #             # Mismo procedimiento para 'section'
    #             section_name = dataEntry.Section
    #             if section_name in resultsName:
    #                 section = resultsName[section_name]
    #             else:
    #                 section = resultsName.create_group(section_name)

    #             section.attrs.setdefault("DESCRIPTION", dataEntry.SectionDescription)
                
    #             # Dataset optimizado con chunking y escritura en bloque
    #             if self._part_name in section:
    #                 data = section[self._part_name]
    #                 if data.dtype == dtype:
    #                     s = data.shape[0]
    #                     data.resize(s + l, axis=0)
    #                     data[s:] = dataEntry.Data  # Escritura en bloque
    #                 else:
    #                     N2PLog.Error.E700()
    #                     continue
    #             else:
    #                 data = section.create_dataset(
    #                     self._part_name, shape=(l,), maxshape=(None,),
    #                     chunks=(True), compression="gzip", dtype=dtype
    #                 )
    #                 data.attrs["DESCRIPTION"] = dataEntry.DataDescription
    #                 data.attrs["PART"] = dataEntry.Part
    #                 data[:] = dataEntry.Data  # Escritura en bloque
    # # ------------------------------------------------------------------------------------------------------------------

    # Method used to write an hdf5 file in memory instead of in a path -------------------------------------------------
    def export_to_HDF5(self) -> None:

        """
        Method used to convert an HDF5 file that has been created in memory to an HDF5 file in disk, which will be 
        located in the FilePath attribute. 
        """

        if isinstance(self._file, io.BytesIO):
            # Regresa el puntero al inicio del archivo
            self._file.seek(0)
            
            # Escribe el contenido del archivo en memoria al disco
            with open(self._file_path, 'wb') as disk_file:
                disk_file.write(self._file.read())
            # print(f"Archivo HDF5 guardado en {self._file_path}")
        else:
            raise ValueError("No se está usando un archivo en memoria para este caso.")
        
    
    def _modules_input_data(self, inputList: list[DataEntry]) -> None:
        """
        """
        with h5py.File(self._file,"a") as hdf:
            naxto = hdf["NAXTO"]
            inputs = naxto["INPUTS"]
            for inp in inputList:
                if inp.DataInput is None: 
                    N2PLog.Warning.W700()
                    continue 
                l = len(inp.DataInput)
                if inp.DataInputName in inputs: 
                    # dataset ya creado 
                    data = inputs[inp.DataInputName]
                    if data == inp.DataInput.dtype: 
                        s = data.shape[0]
                        data.resize(s + l, axis = 0)
                        for i,j in enumerate(inp.DataInput): 
                            data[s + i] = j 
                    else: 
                        N2PLog.Error.E700()
                        continue 
                else: 
                    # dataset sin crear, se crea ahora 

                    if type(inp.DataInput) == ndarray:
                        data = inputs.create_dataset(inp.DataInputName, chunks = (True),shape = (l), maxshape = (None,), compression = "gzip", compression_opts = 9, dtype = inp.DataInput.dtype)
                        for i,j in enumerate(inp.DataInput):
                            data[i] = j

                    elif type(inp.DataInput) == str:
                        data = inputs.create_dataset(inp.DataInputName, data = np.bytes_(inp.DataInput))
                    else:
                        msg = N2PLog.Error.E703()
                        raise Exception(msg)


