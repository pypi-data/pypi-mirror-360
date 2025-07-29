from NaxToPy.Core.Classes.N2PIncrement import N2PIncrement
from NaxToPy.Core.Classes.N2PResult import N2PResult
from NaxToPy.Core.Errors.N2PLog import N2PLog
from typing import Union


# Clase Load Case de Python --------------------------------------------------------------------------------------------
class N2PLoadCase:
    """
    Class which contains the information associated to a load case instance of N2PLoadCase object.
    """

    __slots__ = (
        "__id",
        "__idoriginal",
        "__increments",
        "__incrementsnumberlist",
        "__lctype",
        "__namelc",
        "__results",
        "__solutiontype",
        "_activeIncrement",
        "__solver",
        "_modelFather",
        "__n2loadcase",
        "__increments_by_name",
        "__increments_by_id",
        "__ref_temp"
    )


    # Constructor de N2PLoadCase ---------------------------------------------------------------------------------------
    def __init__(self, id_lc, id_original, increments, increments_number_list, lc_type, name, results,
                 solution_type, solver, model_father, n2loadcase):
        """
        Python Load Case Constructor.

        Input:
            ID: int -> Identification Number of the Load Case
            IDOriginal: int -> Original Identification Number of the Load Case
            Increments: list[N2Increment] -> list with instances of N2Increment
            IncrementsNumberList: list[int] -> list with the number associated to each increment
            LCType: str -> Type of solution applied in the load case
            Name : str -> Name of the load case
            Solver : str -> Solver of the load case
            Results: list[N2Results] -> list with instances of N2Results
        ----------
        Returns:
            N2PLoadCase: object
        """
        self.__id = id_lc
        self.__idoriginal = id_original

        self.__increments = [N2PIncrement(increments[i]) for i in range(0, len(increments))]

        self.__incrementsnumberlist = increments_number_list
        self.__lctype = lc_type
        self.__namelc = name
        self.__results = {results[i].Name: N2PResult(
            results[i].Components,
            results[i].Position,
            results[i].derivedComps,
            results[i].Description,
            results[i].elemTypes,
            results[i].Name,
            self) for i in range(0, len(results))}

        self.__solutiontype = solution_type
        self._activeIncrement = list(increments)[-1].ID
        self.__solver = solver
        self._modelFather = model_father
        self.__n2loadcase = n2loadcase

        self.__increments_by_name = dict()
        self.__increments_by_id = dict()
        self.__ref_temp: float = None
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero de identificacion interno del caso de carga ----------------------------------------
    @property
    def ID(self) -> int:
        """
        Load Case ID.
        """
        return int(self.__id)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo oara obtener el numero de identificacion original del caso de carga ---------------------------------------
    @property
    def OriginalID(self) -> int:
        """
        Original Load Case ID.
        """
        return int(self.__idoriginal)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero de incrementos dentro del caso de carga --------------------------------------------
    @property
    def NumIncrements(self) -> int:
        """
        Number of increments of the Load Case.
        """
        if self.__increments is not None:
            return len(self.__increments)
        else:
            return 0
    # ------------------------------------------------------------------------------------------------------------------
    
    # Metodo para obtener los incrementos de un caso de carga ----------------------------------------------------------
    @property
    def Increments(self) -> list[N2PIncrement]:
        """
        Increments of the Load Case.
        """
        return self.__increments
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el tipo de caso de Carga ---------------------------------------------------------------------
    @property
    def TypeLC(self) -> str:
        """
        Returns the type of Load Case. RAW -> the load case is extracted from the original file. IMPORTED -> the
        load case has been imported.
        """
        return str(self.__lctype)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del caso de carga ------------------------------------------------------------------
    @property
    def Name(self) -> str:
        """
        Name of the Load Case.
        """
        return str(self.__namelc)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el incremento activo. Influye en la funcion de llamada a get_result_array
    @property
    def ActiveIncrement(self) -> int:
        """
        DEPRECATED PROPERTY. Use ActiveN2PIncrement.ID instead. Returns the active increment of the load case. By
        default, is the last one.
        """
        N2PLog.Warning.W206()
        return self._activeIncrement
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para establecer el incremento activo. Influye en la funcion de llamada a get_result_array
    @ActiveIncrement.setter
    def ActiveIncrement(self, id: Union[int, str]) -> None:
        """
        DEPRECATED PROPERTY. Use ActiveN2PIncrement instead. Sets the active increment of the load case. By defult is the last one.

        Args:
            id: int | str -> ID or Name of the N2PIncrement
        """
        activincrement = self.get_increments(id).ID

        if activincrement is not None:
            self._activeIncrement = activincrement
            N2PLog.Info.I202(id)
        else:
            N2PLog.Error.E207(id)
        N2PLog.Warning.W206()
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el incremento activo. Influye en la funcion de llamada a get_result_array --------------------
    @property
    def ActiveN2PIncrement(self) -> N2PIncrement:
        """
        Returns the active increment of the load case. By default, is the last one.
        """
        return self.get_increments(self._activeIncrement)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para establecer el incremento activo. Influye en la funcion de llamada a get_result_array -----------------
    @ActiveN2PIncrement.setter
    def ActiveN2PIncrement(self, incr: N2PIncrement) -> None:
        """
        Sets the active increment of the load case. By defult is the last one.

        Args:
            incr: N2PIncrement -> ID or Name of the N2PIncrement
        """
        self._activeIncrement = incr.ID
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo como propiedad que devuelve todos los N2PResult. Es igual que llamar a get_results sin parametros ---------
    @property
    def Results(self) -> dict[str, N2PResult]:
        """
        Returns all the :class:`N2PResult`.
        """
        return self.__results

    # Metodo para obtener el tipo de solucion del modelo ---------------------------------------------------------------
    @property
    def TypeSolution(self) -> str:
        """
        Solution type of the model.
        """
        return str(self.__solutiontype)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el solver del caso de carga ------------------------------------------------------------------
    @property
    def Solver(self) -> str:
        """
        Solver of the LoadCase.
        """
        return str(self.__solver)
    # ------------------------------------------------------------------------------------------------------------------

    # Propiedad que devuelve la ruta del fichero desde donde se importo el caso de carga -------------------------------
    @property
    def PathFile(self) -> str:
        """
        Returns the path of the file where the load cases were imported from.
        """
        return str(self.__n2loadcase.PathFile)
    # ------------------------------------------------------------------------------------------------------------------

    # Propiedad que devulve la temperatura de referencia ---------------------------------------------------------------
    @property
    def RefTemp(self) -> float:
        """
        Returns the reference temperature of the load case.
        """
        return self.__ref_temp
    # ------------------------------------------------------------------------------------------------------------------
    
    # Método para establecer la temperatura de referencia --------------------------------------------------------------
    @RefTemp.setter
    def RefTemp(self, value) -> None:
        self.__ref_temp = value
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los incrementos disponibles en el caso de carga ----------------------------------------------
    def get_increments(self, id: Union[int, str]) -> N2PIncrement:
        ''' Returns the N2PIncrement object with the id=ID or the id=Name of the Increment

        Args:
            id: str|int -> It can be the ID(int) of the increment or the Name(srt) of the increment

        Returns:
            increment: N2PIncrement
        '''

        # Chequear valor de Name
        if isinstance(id, str):
            # Si el diccionario está vacío se llena
            #if len(self.__increments_by_name__) == 0:
            if not self.__increments_by_name:
                self.__increments_by_name = {str(incr.Name).lower(): incr for incr in self.Increments}
            # Devuelvo N2PResult
            increment = self.__increments_by_name.get(id.lower(), None)
            if increment is not None:
                return increment
            else:
                N2PLog.Error.E212(id)
                return increment

        elif isinstance(id, int):
            # Si el diccionario está vacío se llena
            if not self.__increments_by_id:
                self.__increments_by_id = {incr.ID: incr for incr in self.Increments}
            # Devuelvo N2PResult
            increment = self.__increments_by_id.get(id, None)
            if increment is not None:
                return increment
            else:
                N2PLog.Error.E212(id)
                return increment

        # Devolver todos los resultados
        else:
            N2PLog.Error.E211()
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los incrementos disponibles en el caso de carga ----------------------------------------------
    def get_result(self, name: str) -> N2PResult:
        """
        Returns the N2PResult object with the Name of the Result. The name of the results is different depoending on
        the solver.

        Args:
            name: str

        Returns:
            result: N2PResult

        Examples:
            >>> displ = N2PLoadCase.get_result("DISPLACEMENT")  # If nastran
            >>> displ = N2PLoadCase.get_result("U")  # If Abaqus
        """

        # Chequear valor de Name
        if isinstance(name, str):
            result = self.Results.get(name, None)
            if result is None:
                N2PLog.Error.E213(name)
            return result

        # Devolver todos los resultados
        else:
            N2PLog.Error.E214()
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los incrementos disponibles en el caso de carga ----------------------------------------------
    def set_increment(self, id: Union[int, str]) -> 'N2PLoadCase':
        """
        Method that sets the active increment using an ID where the results will be obtained.
         If id=-1 the last increment is used as active.

        Args:
            id: int|str -> Number id or name of the increment is intended to set as active increment
        Returns:
            loadcase: 'N2PLoadCase'
        """
        if id == -1:
            self.ActiveN2PIncrement = self.__increments[-1]
        elif isinstance(id, int):
            n2pincrements = [i for i in self.__increments if i.ID == id]
            if n2pincrements:
                self.ActiveN2PIncrement = n2pincrements[0]
            else:
                N2PLog.Error.E207(id)
        else:
            n2pincrements = [i for i in self.__increments if i.Name == id]
            if n2pincrements:
                self.ActiveN2PIncrement = n2pincrements[0]
            else:
                N2PLog.Error.E207(id)

        return self
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PLoadCase({self.ID}: \'{self.Name}\')"
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
