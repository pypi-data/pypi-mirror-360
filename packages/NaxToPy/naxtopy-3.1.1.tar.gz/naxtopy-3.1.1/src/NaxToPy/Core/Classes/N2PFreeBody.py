""" Module with all the FreeBody related classes.
"""
from NaxToModel import N2FBDSection, N2FBD, N2FBDResult
from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PCoord import N2PCoord
from NaxToPy.Core.Classes.N2PIncrement import N2PIncrement
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from array import array

# Esta chapuza es para poder crear variables de C#, que son las que necesita el las propiedades de N2FBDSection
import System

class N2PFreeBody(object):
    """
    Main class for free bodies analysis.
    """

    __slots__ = (
        "__name",
        "__loadcase",
        "__increment",
        "__nodelist",
        "__elementlist",
        "__coordsys",
        "__model",
        "__outpoint",
        "__fbdresult",
        "__centroid"
    )
    

    def __init__(self, name: str, loadcase: N2PLoadCase, increment: N2PIncrement, nodelist: list[N2PNode], elementlist: list[N2PElement],
                 modelfather, coordsys: N2PCoord = None, outpoint: tuple[float] = None):
        """
        Constructor of the N2PFreeBody class. It generates a free body in the section defined with the node and
        element list passed as arguments. If no outpoint is given, resultant will be calculated in the centroid.
        
        Args:
            name: str -> Must be unique. If a new FreeBody is name as an old one, the old FreeBody will be deleted.
            loadcase: N2PLoadCase
            increment: N2PIncrement
            nodelist: list[N2PNode]
            elementlist: list[N2PElement]
            coordsys: N2PCoord = None
            outpoint: tuple[float] = None
        """
        self.__name = name
        self.__loadcase = loadcase
        self.__increment = increment
        self.__nodelist = nodelist
        self.__elementlist = elementlist
        self.__coordsys = coordsys
        self.__model = modelfather
        self.__outpoint = outpoint
        self.__fbdresult = None


        if outpoint is not None:
            self.__centroid = False
        else:
            self.__centroid = True

        # Llamada al constructor de NaxToModel
        n2fbdsection = N2FBDSection(self.__name)
        n2fbdsection.OpenFile = self.__model._N2PModelContent__vzmodel

        # Se incluye la parte:
        n2fbdsection.NodesPartID = self.__model._N2PModelContent__StrPartToID.get(self.__nodelist[0].PartID, 0)

        # Si se define un sistema de coordenadas se evalua la propiedad, si no, no se evalua y se usara el global
        if coordsys is not None:
            n2fbdsection.CoordSystem = self.__coordsys._N2PCoord__info

        # Si se define un punto donde calcular los freebodies se añade a la propiedad Point. Si no no se hace nada y
        # se usara el centroide
        if not self.__centroid:
            pointcoords = array("d", self.__outpoint)
            point = N2FBDSection.N2FBDPointCoordinates(n2fbdsection)
            point.Coordinates = pointcoords
            n2fbdsection.Point = point
        else:
            n2fbdsection.OpenFile = self.__model._N2PModelContent__vzmodel

        # Se añaden los nodos usando su id de solver. La parte es la misma para todo_ y se define antes
        for node in self.__nodelist:
            n2fbdsection.NodesId.Add(node.ID)

        # Se añaden los elementos usando su id de solver. La parte es la misma para todo_ y se define antes
        for element in self.__elementlist:
            n2fbdsection.ElementsId.Add(element.ID)

        # Instancio un objeto de la clase N2FBD
        n2fbd = N2FBD(n2fbdsection)

        # Le añado los casos de carga y los incrementos:
        listacasos = System.Collections.Generic.List[System.Int32]()
        listaframes = System.Collections.Generic.List[System.Int32]()
        listacasos.Add(self.__loadcase.ID)
        listaframes.Add(self.__increment.ID)
        n2fbd.GetGpforcesLcInc(listacasos, listaframes)

        # Ejecuto el métedo que calcula las resultantes (por fin)
        # tuple_lc_inc = System.Tuple[System.Int32](self.__loadcase.ID, self.__increment.ID)
        # tuple_lc_inc = System.Tuple[int, int](self.__loadcase.ID, self.__increment.ID)
        tuple_lc_inc = System.Tuple.Create(self.__loadcase.ID, self.__increment.ID)
        self.__fbdresult = n2fbd.FBDCalculate(tuple_lc_inc)

    # Metodo para obtener el Nombre del Free Body ----------------------------------------------------------------------
    @property
    def Name(self) -> str:
        """
        Nombre del Free Body.
        """
        return self.__name
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el Módulo de la Fuerza Resultante ------------------------------------------------------------
    @property
    def FTotal(self) -> float:
        """
        Module of the resultant Force.
        """
        return float(self.__fbdresult.FTotal)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el Módulo del Momento Resultante -------------------------------------------------------------
    @property
    def MTotal(self) -> float:
        """
        Module of the resultant Moment.
        """
        return float(self.__fbdresult.MTotal)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el Vector de Fuerza Resultante ---------------------------------------------------------------
    @property
    def Force(self) -> tuple[float, float, float]:
        """
        Vector of the resultant Force.
        """
        return (float(self.__fbdresult.Section_Forces_FX),
                float(self.__fbdresult.Section_Forces_FY),
                float(self.__fbdresult.Section_Forces_FZ),)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el Vector de Momento Resultante --------------------------------------------------------------
    @property
    def Moment(self) -> tuple[float, float, float]:
        """
        Vector of the resultant Moment.
        """
        return (float(self.__fbdresult.Section_Forces_MX),
                float(self.__fbdresult.Section_Forces_MY),
                float(self.__fbdresult.Section_Forces_MZ),)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el caso de carga del free body ---------------------------------------------------------------
    @property
    def LoadCase(self):
        """
        Load Case of the Free Body.
        """
        return self.__loadcase
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el incremeneto del free body -----------------------------------------------------------------
    @property
    def Increment(self):
        """
        Increment of the Free Body.
        """
        return self.__increment
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener la lista de nodos ----------------------------------------------------------------------------
    @property
    def NodeList(self):
        """
        List of nodes of the Free Body.
        """
        return self.__nodelist
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener la lista de elementos ------------------------------------------------------------------------
    @property
    def ElementList(self):
        """
        Lista de elementos of the Free Body.
        """
        return self.__elementlist
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el punto donde los resultados han sido calculados --------------------------------------------
    @property
    def OutPoint(self):
        """
        Returns the point where the resultants were calculated. Centroid by default.
        """
        return tuple(self.__fbdresult.NodeCoords)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el Sistema de Coordenadas donde los resultados han sido calculados ---------------------------
    @property
    def OutSys(self):
        """
        Returns de Coordinate System where the resultants were calculated.
        """
        return self.__coordsys
    # ------------------------------------------------------------------------------------------------------------------