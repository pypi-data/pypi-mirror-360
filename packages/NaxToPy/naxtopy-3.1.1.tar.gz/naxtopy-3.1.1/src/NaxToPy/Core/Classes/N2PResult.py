from NaxToPy.Core.Classes.N2PComponent import N2PComponent
from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToModel import N2Component
from NaxToModel import N2ArithmeticSolver
from NaxToModel import N2Enums
from System.Collections.Generic import List


# Clase Result de Python --------------------------------------------------------------------------
class N2PResult:
    """Class which contains the information associated to a result of a :class:`N2PLoadCase`"""

    __slots__ = (
        "__components",
        "__position",
        "__derived_comps",
        "__description",
        "__elem_types",
        "__name",
        "_loadCase_father",
    )
    
    # Constructor de N2PResult --------------------------------------------------------------------
    def __init__(self, components, position, derivedComps, description, elemTypes, name, loadCase_father):
        """Python Result Constructor.

        Args:
            components: list[N2Component] -> list with instances of N2Components.
            position: str -> postion of the results.
            derivedComps: list[N2Component] -> list with instances of N2Components (derived).
            description: str -> description of the result.
            elemTypes: list[str] -> list with the types of elements where results have been obtained.
            name: str -> name of the result.
        """

        self.__components = {components[i].Name: N2PComponent(components[i].Name, components[i].Sections, self)
                               for i in range(0, len(components))}
        self.__position = position
        self.__derived_comps = {derivedComps[i].Name: N2PComponent(derivedComps[i].Name, derivedComps[i].Sections, self)
                                  for i in range(0,len(derivedComps))}
        self.__description = description
        self.__elem_types = elemTypes
        self.__name = name
        self._loadCase_father = loadCase_father
    # ---------------------------------------------------------------------------------------------

    # Metodo como propiedad para obtener todas las componentes. Es igual al metodo get_components.
    @property
    def Components(self) -> dict[str, N2PComponent]:
        """Dictionary with the name of the components as keys and :class:`N2PComponent` as values"""
        return self.__components
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la posicion donde se han obtenido resultados ----------------------------
    @property
    def Position(self) -> str:
        """Returns the position where the results have been obtained within the load case"""
        return str(self.__position)
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la componentes derivadas disponibles en el resultado --------------------
    @property
    def DerivedComponents(self) -> dict[str, N2PComponent]:
        """Returns a list of :class:`N2Component` with all the derived components available within the result"""
        return self.__derived_comps
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la descripcion del resultado --------------------------------------------
    @property
    def Description(self) -> str:
        """Descriprion of the result"""
        return self.__description
    # ----------------------------------------------------------------------------------------------

    # Metodo para obtener los tipos de elemento en los cuales se han obtenido resultados -----------
    @property
    def TypesElements(self) -> list[str]:
        """Returns a list with the element types where results are available.
        """
        return list(self.__elem_types)
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del resultado -------------------------------------------------
    @property
    def Name(self) -> str:
        return str(self.__name)
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener las componentes disponibles en el resultado -----------------------------
    def get_component(self, name: str) -> N2PComponent:
        """Returns a :class:`N2Component` as component with name specified. It can be a Raw Component or a derived component

        Args:
            name: str

        Returns:
            N2PComponent: component
        """

        if isinstance(name, str):
            component = self.Components.get(name, None)
            if not component:
                component = self.DerivedComponents.get(name, None)
            if component is None:
                N2PLog.Error.E215(name)
            return component

        # Devolver todos los resultados
        else:
            N2PLog.Error.E216()
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener las componentes originales disponibles en el resultado -----------------------------
    def get_raw_component(self, name: str) -> N2PComponent:
        """Returns a :class:`N2Component` as component with name specified. It checks only in the original list of components

        Args:
            name: str

        Returns:
            N2PComponent: component
        """

        if isinstance(name, str):
            component = self.Components.get(name, None)
            if component is None:
                N2PLog.Error.E215(name)
            return component

        # Devolver todos los resultados
        else:
            N2PLog.Error.E216()
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener las componentes disponibles en el resultado -----------------------------
    def get_derived_component(self, name: str) -> N2PComponent:
        """Returns a N2Component as derived component with name specified,

        Args:
            name: :class:`str`

        Returns:
            N2PComponent: derived component
        """

        if isinstance(name, str):
            result = self.DerivedComponents.get(name, None)
            if result is None:
                N2PLog.Error.E217(name)
            return result

        # Devolver todos los resultados
        else:
            N2PLog.Error.E216()
    # ---------------------------------------------------------------------------------------------

    def new_derived_component(self, name: str, formula: str) -> N2PComponent:
        """Generate a new N2PComponent combination of n components from N2PResult.

        These combinations can be obtained later with the method :meth:`get_derived_component()`.

        To define the combination, pass a string with the result and component names, along with the arithmetic commands as strings.
        The name of the new derived component must be set. To add a component to the formula, it must start with `CMPT_`
        followed by the Result name (the result must be the same) if it is an original component, and with `CMPTD` (only that),
        then `:` and finally the Component name.

        The `Result|Component` must have this structure: `<CMPT_Result:Component>` or `<CMPTD:Component>`.

        Args:
            name (:class:`str`): The name of the component.
            formula (:class:`str`): String containing the Result:Component intended to be used and the arithmetic operations.

        Returns:
            N2PComponent: Derived load case.

        Examples:
            >>> N2PResult.new_derived_component("dev_comp1", formula="<0.5*CMPT_DISPLACEMENTS:MAGNITUDE_D>+2*<CMPT_DISPLACEMENTS:MAGNITUDE_R>")
            >>> N2PResult.new_derived_component("dev_comp2", formula="(<CMPTD:Example>-2*<CMPT_DISPLACEMENTS:MAGNITUDE_R>)^2"
            >>> N2PResult.new_derived_component("dev_comp3", formula="sqrt(<CMPT_STRESSES:XX>^2+<CMPT_STRESSES:YY>^2-<CMPT_STRESSES:XX>*<CMPT_STRESSES:YY>+3*<CMPT_STRESSES:XY>^2)")
        """

        # Recuperamos la instancia N2ModelModelContent
        mc = self._loadCase_father._modelFather._N2PModelContent__vzmodel

        # Llamada al constructor de N2Component de NaxToModel
        new_d_comp = N2Component(mc, name, formula)

        # Se incluye en la lista de compornentes derivadas de NaxToModel. Para ello tengo que comprobar que existe
        # dicha lista. Si no existe la tengo que crear como lista de C#
        if not mc.DerivedComponents:
            mc.DerivedComponents = List[N2Component]()

        # Now I add the new derived component to the list
        mc.DerivedComponents.Add(new_d_comp)

        # Call the method that recalculate the data.
        new_d_comp.RecalculateCMPTInfo2Formule()

        # Este metodo de N2ArithmeticSolver en NaxToModel comprueba que la formula introducida es correcta.
        # Devuelve False si está mal y True si está bien.
        err = N2ArithmeticSolver.CheckExpression(new_d_comp.Formula, mc, N2ArithmeticSolver.ExpressionType.COMPONENT)
        if int(err) == 0:
            pass
        else:
            N2PLog.Error.E230(formula, (formula, str(N2Enums.GetDescription(err).upper())) )  # error
            return "ERROR"

        # The N2PComponent is instanced and added to the dictionary of derived loadcases:
        self.__derived_comps[new_d_comp.Name] = N2PComponent(new_d_comp.Name, new_d_comp.Sections, self)

        return self.__derived_comps[new_d_comp.Name]



    # # Metodo para obtener los resultados de todas las componentes del resultado como DataFrame ----
    # def get_results_dataframe(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1,
    #                           variation=100, realPolar=0) -> DataFrame:
    #     """
    #     Returns a DataFrame of pandas with the results array of echa component of a LoadCase for
    #     the active increment.
    #     Input (Parameters)
    #
    #     + sections: list of sections (string) which operations are done
    #         · None (Default) = All Sections
    #
    #     + aveSections: Operation Among Sections
    #         · -1 : Maximum (Default)
    #         · -2 : Minimum
    #         · -3 : Average
    #         · -4 : Extreme
    #         · -6 : Difference
    #
    #     + cornerData : flag to get results in element nodal
    #         · True : Results in Element-Nodal
    #         · False : Results in centroid (Default)
    #
    #     + aveNodes: Operation among nodes when cornerData is selected
    #         ·  0 : None
    #         · -1 : Maximum (Default)
    #         · -2 : Minimum
    #         · -3 : Average
    #         · -5 : Average with variation parameter
    #         · -6 : Difference
    #
    #     + variation: Integer between 0 & 100 to select
    #         · 0 : No average between nodes
    #         · 100 : Total average between nodes (Default)
    #
    #     + realPolar: data type when complex result
    #         · 1 : Real / Imaginary
    #         · 2 : Magnitude / Phase
    #
    #     ----------
    #     Returns:
    #         DataFrame:
    #             - data: float64 -> results array
    #             - index: int | tuple -> id of the element/node or tuple (id, part)
    #                                     it could be a tuple (nodo_id, element_id, part) for cornerData
    #             - column: str -> component.Name
    #     ----------
    #     """
    #     first = True
    #     for component in self.Components.values():
    #         data = component.get_result_dataframe(sections, aveSections, cornerData, aveNodes,
    #                                               variation, realPolar)
    #         if first:
    #             resultdataframe = data
    #             first = False
    #         else:
    #             resultdataframe = resultdataframe.join(data)
    #
    #     return resultdataframe
    # # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        loadcasestr = f"N2PResult(\'{self.Name}\')"
        return loadcasestr
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
