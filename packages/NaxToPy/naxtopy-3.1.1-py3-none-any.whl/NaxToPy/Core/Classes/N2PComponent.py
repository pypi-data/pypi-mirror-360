from __future__ import annotations

import gc
from array import array
import numpy as np
from typing import Union
import ctypes

from NaxToModel import N2ParamInputResults
from NaxToModel import N2TensorTransformation

from NaxToPy.Core.Classes.N2PSection import N2PSection
from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToPy.Core._AuxFunc._NetToPython import _numpytonet
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PNode import N2PNode




# Clase Component de Python
# -----------------------------------------------------------------------
class N2PComponent:
    """
    Class which contains the information associated to a component of a  :class:`N2PResult` instance.
    """

    __slots__ = (
        "_name",
        "_sections",
        "_result_father",
    )

    # Constructor de N2PComponent --------------------------------------------------------------------------------------
    def __init__(self, name, sections, result_father):
        """ 
        Python Component Constructor.

            Args:
                name: str -> name of the component
                sections: list[N2Sections] -> list with instances of N2Sections
                result_father: N2PResult
        """
        self._name = name
        self._sections = [N2PSection(sections[i].Name,
                                        sections[i].Number) for i in range(0, len(sections))]
        self._result_father = result_father
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el Nombre de la Componente -------------------------------------------------------------------
    @property
    def Name(self) -> str:
        """
        Name of the component.
        """
        return(str(self._name))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener una lista con las secciones de la componente -------------------------------------------------
    @property
    def Sections(self) -> list[N2PSection, ...]:
        """ 
        Returns a list of N2PSection objects with all the sections contained in the component.
        """
        return(self._sections)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para comprobar si el resultado es transformable en otro sistema de coordenadas ----------------------------
    @property
    def IsTransformable(self) -> bool:
        """
        Property that keeps if the component of a result is transformable in other coordinate system.
        """
        # No se guarda como atributo privado durante la instanciacion de un objeto porque algunas variables
        # aun no se han construido. Por eso el metodo de la propiedad es la que busca los argumentos y llama
        # al metodo dentro de Vizzer classes.
        solver = self._result_father._loadCase_father._N2PLoadCase__solver
        result = self._result_father.Name
        component = self.Name
        return bool(N2TensorTransformation.IsResultSupported(solver, result, component))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para llamar a la funcion de NaxToModel que devueleve el array de resultados--------------------------------
    def get_result_array(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                         realPolar=0, coordsys: int = -1000,
                         v1: tuple = (1, 0, 0), v2: tuple = (0, 1, 0)) -> tuple[list, str]:
        """
        Deprecated method. Please, use get_result_list instead for asking the results as a list. If a numpy array is
        preferred, use get_result_ndarray.
        """
        return self.get_result_list(sections, aveSections, cornerData, aveNodes, variation,
                                    realPolar, coordsys, v1, v2)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para llamar a la funcion de NaxToModel que devueleve el array de resultados como lista --------------------
    def get_result_list(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                         realPolar=0, coordsys: int = -1000,
                         v1: Union[tuple, np.ndarray] = (1,0,0), v2: Union[tuple, np.ndarray] = (0,1,0)) -> tuple[list, str]:
        """ 
        Returns a tuple with the list of floats with the result array asked and a str with the position of the
        results.

        Args:
        
            sections: list[str] | list[N2PSection] -> Optional. Sections which operations are done.
                None (Default) = All Sections

            aveSections: int -> Optional. Operation Among Sections.

                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -4 : Extreme,
                -6 : Difference.

            cornerData: bool -> Optional. Flag to get results in element nodal.

                True : Results in Element-Nodal,
                False : Results in centroid (Default).

            aveNodes: int -> Optional. Operation among nodes when cornerData is selected.

                 0 : None,
                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -6 : Difference.

            variation: int -> Optional. Integer between 0 & 100 to select.

                0 : No average between nodes,
                100 : Total average between nodes (Default).

            realPolar: int -> Optional. Data type when complex result.

                1 : Real / Imaginary,
                2 : Magnitude / Phase.

            coordsys: int -> Optional. Coordinate System where the result_array will be represented. By default,
                the output is in element system:

                0   : Global,
                -1  : Material Coordinate System,
                -10 : User defined,
                -20 : Element/Node User Defined,
                >0  : Solver ID of the Predefined Coordinate System.

            v1: tuple -> Optional.

            v2: tuple -> Optional. Directions vectors that generate the coordinate system axis:

                x=v1,
                z=v1^v2,
                y=z^x.

        Returns: 
            results: tuple(list[float], str)

        """
        # Aquí se prepara la llamada a la funcion de NaxToModel.N2PModelContent.getArraytoPlot(). Esta usa como
        # argumento un objeto de la clase N2ParamImputResults. Por se instancia y se modifican sus propiedades antes
        # de hacer la llamada a la funcion.

        # Aqui se mete el sistema de coordenadas en el que queremos que nos saque la informacion.
        # Para ello primero comprobamos que es viable hacer la tansformacion (puede que aun no este implementada o que
        # la componente simplemente no la admita al ser un escalar a secas)

        #resultsParameters.coordSys = -10
        #orientationcoordinatesystem = algo

        resultsParameters = self._create_n2paraminputresult(None, sections, aveSections, cornerData, aveNodes, variation,
                                                            realPolar, coordsys, v1, v2)
        results = list(
            self._result_father._loadCase_father._modelFather._N2PModelContent__vzmodel.CalculateArrayLastResult(
                resultsParameters, 0))

        if results[1] == 1:
            return(list(results[0]),'NODES')
        elif results[1] == 2:
            return(list(results[0]), 'ELEMENTS')
        elif results[1] == 3:
            return(list(results[0]), 'ELEMENT NODAL')
        else:
            N2PLog.Error.E206(self.Name)
            return(-1, 'NO RESULTS')
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para llamar a la funcion de NaxToModel que devuelve el array de resultados como array de numpy ------------
    def get_result_ndarray(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                         realPolar=0, coordsys: int = -1000,
                         v1: Union[tuple, np.ndarray ] = (1,0,0), v2: Union[tuple, np.ndarray ] = (0,1,0),
                         filter_list: list = None) -> tuple[np.array, str]:
        """ 
        Returns a tuple with the numpy array of floats with the result array asked and a str with the position of
        the results.

        Args:

            sections: list[str] | list[N2PSection] -> Optional. Sections which operations are done.
                None (Default) = All Sections

            aveSections: int -> Optional. Operation Among Sections.

                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -4 : Extreme,
                -6 : Difference.

            cornerData: bool -> Optional. Flag to get results in element nodal.

                True : Results in Element-Nodal,
                False : Results in centroid (Default).

            aveNodes: int -> Optional. Operation among nodes when cornerData is selected.

                 0 : None,
                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -6 : Difference.

            variation: int -> Optional. Integer between 0 & 100 to select.

                0 : No average between nodes,
                100 : Total average between nodes (Default).

            realPolar: int -> Optional. Data type when complex result.

                1 : Real / Imaginary,
                2 : Magnitude / Phase.

            coordsys: int -> Optional. Coordinate System where the result_array will be represented. By default,
                the output is in element system:

                0   : Global,
                -1  : Material Coordinate System,
                -10 : User defined,
                -20 : Element/Node User Defined,
                >0  : Solver ID of the Predefined Coordinate System.

            v1: tuple -> Optional.

            v2: tuple -> Optional. Directions vectors that generate the coordinate system axis:

                x=v1,
                z=v1^v2,
                y=z^x.

            filter_n2p: list[N2PElement|N2PNode] (optional)
                List with the N2PElement or N2PNode where the results are asked. Filtering the results slows
                the result extraction. If the results are needed in two separate list of itmes (nodes or elements)
                ask first for both and filter them later.

        Returns:
            results: tuple(np.array, str)

        Examples
            >>> # N2PComponent is a N2PLoadCase.get_results("DISPLACEMENTS").get_component("X")
            >>> displ_X_array, where = N2PComponent.get_result_ndarray(aveSections=-3, coordsys=-1)
            >>> # N2PComponent is a N2PLoadCase.get_results("STRESSES").get_component("XX")
            >>> stress_array, where = N2PComponent.get_result_ndarray(v1=(-1, 0, 0), v2=(0, -1, 0))
        """
        resultsParameters = self._create_n2paraminputresult(None, sections, aveSections, cornerData, aveNodes, variation,
                                                            realPolar, coordsys, v1, v2)

        results = \
            self._result_father._loadCase_father._modelFather._N2PModelContent__vzmodel.CalculateArrayLastResult(
            resultsParameters, 0)

        if results[1] == 1:
            where = "NODES"
        elif results[1] == 2:
            where = "ELEMENTS"
        elif results[1] == 3:
            where = "ELEMENT NODAL"
        else:
            N2PLog.Error.E206(self.Name)
            return (-1, 'NO RESULTS')

        return (self._filter_array(np.array(results[0], np.float64), filter_list, where, None, cornerData), where)
    # ------------------------------------------------------------------------------------------------------------------

    # # Metodo que devulve un dataframe con los resulados tras llamar a la funcion de NaxToModel------------------------
    # def get_result_dataframe(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1,
    #                          variation=100, realPolar=0, coordsys: int = -1000,
    #                          v1: tuple = (1,0,0), v2: tuple = (0,1,0)) -> DataFrame:
    #     """Returns a DataFrame of pandas with the results array of a component as data for the active increment.
    #
    #     Args:
    #
    #         sections: list[str] | list[N2PSection] -> Sections which operations are done.
    #             None (Default) = All Sections
    #
    #         aveSections: int -> Operation Among Sections.
    #             -1 : Maximum (Default),
    #             -2 : Minimum,
    #             -3 : Average,
    #             -4 : Extreme,
    #             -6 : Difference.
    #
    #         cornerData: bool -> flag to get results in element nodal.
    #             True : Results in Element-Nodal,
    #             False : Results in centroid (Default).
    #
    #         aveNodes: int -> Operation among nodes when cornerData is selected.
    #             0 : None,
    #             -1 : Maximum (Default),
    #             -2 : Minimum,
    #             -3 : Average,
    #             -5 : Average with variation parameter,
    #             -6 : Difference.
    #
    #         variation: int -> Integer between 0 & 100 to select.
    #             0 : No average between nodes,
    #             100 : Total average between nodes (Default).
    #
    #         realPolar: int -> data type when complex result.
    #             1 : Real / Imaginary,
    #             2 : Magnitude / Phase.
    #
    #         coordsys: int -> Coordinate System where the result_array will be represented.
    #             0   : Global,
    #             -1  : Material Coordinate System,
    #             -10 : User defined,
    #             -20 : Element/Node User Defined,
    #             >0  : Solver ID of the Predefined Coordinate System.
    #
    #         v1: tuple
    #
    #         v2: tuple -> Directions vectors that generate the coordinate system axis:
    #             x=v1,
    #             z=v1^v2,
    #             y=z^x.
    #
    #     Returns:
    #         DataFrame:
    #             data: float64: results array
    #             index: int | tuple: id of the element/node or tuple (id, part)
    #                                     it could be a tuple (nodo_id, element_id, part) for cornerData
    #             column: str: component.Name
    #     ----------
    #     """
    #     ids = list()
    #     indexname = list()
    #
    #     resultlist = self.get_result_array(sections, aveSections, cornerData, aveNodes, variation, realPolar, coordsys,
    #                                        v1, v2)
    #
    #     if resultlist[0] == -1:
    #         N2PLog.Error.E208()
    #         return DataFrame()
    #     if len(self.__result_father__._loadCase_father._modelFather._N2PModelContent__StrPartToID) == 1:
    #         noparts = True
    #     else:
    #         noparts = False
    #
    #     if resultlist[1] == "NODES":
    #         nodos = self.__result_father__._loadCase_father._modelFather.get_nodes()
    #         if noparts:
    #             ids = [nodo.ID for nodo in nodos]
    #             indexname = ["Grid"]
    #         else:
    #             ids = [(nodo.PartID, nodo.ID) for nodo in nodos]
    #             indexname = ["Part", "Grid"]
    #         del nodos
    #     elif resultlist[1] == "ELEMENTS":
    #         elements = self.__result_father__._loadCase_father._modelFather.get_elements()
    #         connectors = self.__result_father__._loadCase_father._modelFather.get_connectors()
    #         if noparts:
    #             # La lista de connectores puede contener N2PConnector o lista de N2PConector. Esto es porque
    #             # los MPC puden tener ids iguales en Nastran. Por eso en la comprension de la lista de conectores
    #             # itero sobre la lista de conetores con igual id dentro de la lista de conectores general y si no
    #             # resulta ser una lista lo transformo en lista e itero.
    #             ids = [element.ID for element in elements] + \
    #                   [c.ID for con in connectors for c in (con if isinstance(con, list) else [con])]
    #             indexname = ["Element"]
    #         else:
    #             ids = [(element.PartID, element.ID) for element in elements] +\
    #                   [(c.PartID, c.ID) for con in connectors for c in (con if isinstance(con, list) else [con])]
    #             indexname = ["Part", "Element"]
    #         del elements, connectors
    #     elif resultlist[1] == "ELEMENT NODAL":
    #         ids = list(self.__result_father__._loadCase_father._modelFather._elementnodal().values())
    #         indexname = ["Part", "Grid", "Element"]
    #
    #     # Se revisa que la lista de malla y la lista de resultados sean del mismo tamaño
    #     if not len(ids) == len(resultlist[0]):
    #         N2PLog.Warning.W202()
    #         length = min(len(ids), len(resultlist[0]))
    #         ids = ids[:length]
    #         resultlist = (resultlist[0][:length], resultlist[1])
    #
    #     data = {self.Name: resultlist[0]}
    #     if isinstance(ids[0], tuple):
    #         index = MultiIndex.from_tuples(ids, names=indexname)
    #     else:
    #         index = ids
    #
    #     df = DataFrame(data=data, index=index, columns=[self.Name])
    #
    #     if not isinstance(ids[0], tuple):
    #         df = df.rename_axis(indexname, axis='index')
    #
    #     return df
    # # ----------------------------------------------------------------------------------------------------------------

    # Método que devuelve un diccionario con la tupla (LC, Incr) como clave y una lista de resultados como valor -------
    def _get_result_by_LCs_Incr(self, list_lc_incr: list[tuple["N2PLoadCase", "N2PIncrement"],...], components = None,
                               sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                               realPolar=0, coordsys: int = -1000,
                               v1: tuple = (1,0,0), v2: tuple = (0,1,0),
                               filter_list: list = None) -> dict[tuple: list[float]]:

        py_dict = {}  # Dictionary that is going to be returned.
        first_shoot = True
        i = 0
        n_opt = 0
        n_lcs = len(list_lc_incr)
        
        # A first shoot with a block of 5 load cases is made. The memory used in the process wil be measured
        # using the function _get_memory_usage(). Acording to de memory used, the optimum number of load cases
        # per block will be claculated and the remain load cases will be launched in blocks.
        while i < n_lcs:
            
            if first_shoot:
                formula = self._create_formula(list_lc_incr[0:5])
            else:
                formula = self._create_formula(list_lc_incr[i : i + n_opt])

            if not formula:
                return None
            
            if components is None: components = [None] 
            for component in components:
                resultsParameters = self._create_n2paraminputresult(component, sections, aveSections, cornerData, aveNodes, variation,
                                                                    realPolar, coordsys, v1, v2)

                if first_shoot:
                    _, available_memory, initial_memory = _get_memory_usage()

                cs_dict = self._result_father._loadCase_father._modelFather._N2PModelContent__vzmodel.CalculateArrayLastResult(
                        formula, resultsParameters, 0)
                
                if filter_list and not cornerData:
                    ii_map = [item.InternalID for item in filter_list]
                elif filter_list and cornerData:
                    if isinstance(filter_list[0], N2PElement):
                        ii_map = list(self._result_father._loadCase_father._modelFather.elementnodal(filter_list).keys())
                    else:
                        N2PLog.Error.E234()
                else:
                    ii_map = None

                if not components[0]:
                    py_dict.update({
                        (int(key.split(":")[0].replace("DoF_LCD", "-").replace("DoF_LC", "")), int(key.split(":")[1][2:])) :
                        self._filter_array(np.array(value, np.float64), filter_list, None, ii_map, cornerData)
                        for key, value in dict(cs_dict[0]).items()
                    })
                else:
                    py_dict.update({
                        (int(key.split(":")[0].replace("DoF_LCD", "-").replace("DoF_LC", "")), int(key.split(":")[1][2:]), component) :
                        self._filter_array(np.array(value, np.float64), filter_list, None, ii_map, cornerData)
                        for key, value in dict(cs_dict[0]).items()
                    })
                
                del cs_dict
                # endfor

            if first_shoot:
                _, _, final_memory = _get_memory_usage()
                used_memory = final_memory - initial_memory
                # Minimum number is fixed to 100
                used_memory = used_memory if used_memory > 100 else 100
                n_opt = int(available_memory*0.9/used_memory*5)
                i = 5
                first_shoot = False
            else:
                i += n_opt

            # Limpiamos memoria antes de pasar al siguiente bloque de casos de carga
            self._result_father._loadCase_father._modelFather.clear_results_memory()
            # endwhile
        
        return py_dict
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo que crea la formula que necesita la funcion de NaxToModel -------------------------------------------------
    def _create_formula(self, list_lc_incr: list[tuple["N2PLoadCase", "N2PIncrement"],...]) -> str:

        if isinstance(list_lc_incr, tuple):
            list_lc_incr = [list_lc_incr]

        N2PLoadCase = type(self._result_father._loadCase_father)
        N2PIncrement = type(self._result_father._loadCase_father.Increments[0])

        if isinstance(list_lc_incr[0][0], N2PLoadCase) and isinstance(list_lc_incr[0][1], N2PIncrement):
            return ",".join(f"<LC{lc[0].ID}:FR{lc[1].ID}>" for lc in list_lc_incr)

        elif isinstance(list_lc_incr[0][0], int) and isinstance(list_lc_incr[0][1], int):
            return ",".join(f"<LC{lc[0]}:FR{lc[1]}>" for lc in list_lc_incr)

        else:
            N2PLog.Error.E310()
            return None
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo que crea el N2ParamInputResult ----------------------------------------------------------------------------
    def _create_n2paraminputresult(self, component, sections, aveSections, cornerData, aveNodes, variation,
                                   realPolar, coordsys, v1, v2) -> N2ParamInputResults:

        # Aqui comprobamos que si queremos hacer una transformacion y si esta es posible:
        if self.IsTransformable and (coordsys != -1000 or (v1 != (1, 0, 0) or v2 != (0, 1, 0))):
            # si es un sistema definido por el usuarios es -10 y se busca el GlobalID. Si es positivo es de solver.
            # si es material es -1.
            if (v1 != (1, 0, 0) or v2 != (0, 1, 0)) and (coordsys != -10 and coordsys != -1000):
                N2PLog.Warning.W208(coordsys)

            if (coordsys == -10 or coordsys == -1000) and (v1 != (1, 0, 0) or v2 != (0, 1, 0)):
                # Esto es una array de doubles. Si se quiere hacer una transformacion tanto en sistemas ya definidos en
                # el solver como por el usuario hay que pasarlo como argumento de N2ParamInputResult
                new_sys = _get_axis(v1, v2)
                new_sys = _numpytonet(new_sys)

                resultsParameters = N2ParamInputResults.structResults(0)
                resultsParameters.coordSys = -10
                resultsParameters.orientationcoordinatesystem = new_sys

            elif coordsys in {-1, 0, -20} or coordsys > 0:
                resultsParameters = N2ParamInputResults.structResults(0)  # , x_array, y_array, z_array)
                resultsParameters.coordSys = coordsys

            else:
                # If coordsys doesn't match any known case, log an error and return failure
                msg = N2PLog.Error.E220()
                raise Exception(msg)

        elif not self.IsTransformable and (coordsys != -1000 or (v1 != (1, 0, 0) or v2 != (0, 1, 0))):
            if component:
                comp = component
            else:
                comp = str(self.Name)
            N2PLog.Warning.W210(comp)
            resultsParameters = N2ParamInputResults.structResults(0)

        else:
            # Initializer if it is no transformable
            resultsParameters = N2ParamInputResults.structResults(0)

        # Component Selected
        if component:
            resultsParameters.Component = component
        else:
            resultsParameters.Component = str(self.Name)

        # Entity Selection (So Far 'ALL')
        resultsParameters.IdsEntities = ''

        # Active Increment
        resultsParameters.IncrementID = str(self._result_father._loadCase_father._activeIncrement)

        # Load Case Selected
        resultsParameters.LoadCaseID = str(self._result_father._loadCase_father.ID)

        # Parts Selected (So Far 'ALL')
        resultsParameters.Part = 'all'

        # Results Selected
        resultsParameters.Result = str(self._result_father.Name)

        resultsParameters.Sets = ''
        resultsParameters.TypeElement = ''

        # Sections Selected (By Default 'ALL') & Section Average
        sectionParam = ''

        if sections is None:
            for section in self._sections:
                sectionParam += str(section.Name) + '#'
        else:
            if not isinstance(sections, list):
                msg = N2PLog.Error.E218()
                raise TypeError(msg)
            actual_sections = {s.Name for s in self.Sections}
            for section in sections:
                if type(section) is N2PSection:
                    sectionParam += str(section.Name) + '#'
                else:
                    if section in actual_sections:
                        sectionParam += str(section) + '#'
                    else:
                        msg = N2PLog.Error.E238(section, actual_sections)
                        raise Exception(msg)

        resultsParameters.sectPoint = sectionParam

        avasectionsupported = (-1, -2, -3, -4, -6)
        if aveSections not in avasectionsupported:
            msg = N2PLog.Error.E237(aveSections, avasectionsupported)
            raise Exception(msg)
        resultsParameters.aveSection = aveSections

        # CornerData Selection, Average & Variation
        resultsParameters.cornerData = cornerData

        _aveIntraSupported = (0, -1, -2, -3, -6)
        if (aveNodes not in _aveIntraSupported):
            msg = N2PLog.Error.E236(aveNodes, _aveIntraSupported)
            raise Exception(msg)
        else:
            resultsParameters.aveIntra = aveNodes

        if variation != 100 and aveNodes != -3:
            N2PLog.Warning.W209()
        if variation > 100:
            variation = 100
        elif variation < 0:
            variation = 0

        resultsParameters.variation = variation

        # Real/Imaginary or Magnitude/Phase
        __complexSupported = (0, 1, 2)
        if (realPolar not in __complexSupported):
            msg = N2PLog.Error.E239(realPolar, __complexSupported)
            raise Exception(msg)
        else:
            resultsParameters.real_cartesian_polar = realPolar

        return resultsParameters
    # ------------------------------------------------------------------------------------------------------------------

    def _filter_array(self, array: np.ndarray, filter_list: list[Union[N2PElement, N2PNode]], 
                      where=None, ii_map=None, cornerData=False) -> np.ndarray:

        if not filter_list:
            return array
        
        if where == "ELEMENTS" and not isinstance(filter_list[0], N2PElement):
            msg = N2PLog.Error.E234()
            raise Exception(msg)
        elif where == "NODE" and not isinstance(filter_list[0], N2PNode):
            msg = N2PLog.Error.E233()
            raise Exception(msg)
        elif not isinstance(filter_list[0], (N2PNode, N2PElement)):
            msg = N2PLog.Error.E235()
            raise Exception(msg)
        
        if not ii_map and not cornerData:
            ii_map = [item.InternalID for item in filter_list]
        elif not ii_map and cornerData:
            ii_map = list(self._result_father._loadCase_father._modelFather.elementnodal(filter_list).keys())
        
        return array[ii_map]


    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        loadcasestr = f"N2PComponent(\'{self.Name}\')"
        return loadcasestr
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------


def _get_axis(v1: Union[tuple, np.ndarray], v2: Union[tuple, np.ndarray]) -> np.ndarray:
    """
    Function that returns the components of the three vectors of a rectangular coordinate system.

    Args:
        v1: tuple|ndarray
        v2: tuple|ndarray

    Returns:
        ndarray
    """
    v1 = np.array(v1)
    v1 = v1/np.linalg.norm(v1)

    v2 = np.array(v2)
    v2 = v2/np.linalg.norm(v2)

    z = np.cross(v1, v2)
    y = np.cross(z, v1)

    return np.vstack((v1, y, z))

def _get_memory_usage() -> tuple[float, float, float]:
    """
    Returns total_memory, available_memory, used_memory in MB.
    """

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))

    total_memory = memory_status.ullTotalPhys / (1024 ** 2)  # Convert to MB
    available_memory = memory_status.ullAvailPhys / (1024 ** 2)  # Convert to MB
    used_memory = total_memory - available_memory

    return total_memory, available_memory, used_memory