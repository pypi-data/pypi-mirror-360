"""Module that contains the N2PReport class"""

from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToPy.Core.Classes.N2PComponent import _get_axis
from NaxToPy.Core._AuxFunc._NetToPython import _numpytonet
import numpy as np
from typing import Union
from NaxToModel import N2Report, N2ParamInputResults, N2Enums
from System import Object, Array


class N2PReport:
    """Class that contains the data of a report. It includes the input data: load cases, the selection (that could be a
    list of N2PNode or N2PElement), if envelope,... and the output data: results array asked
    
    To create a :class:`N2PReport` use the method :meth:`new_report()` from the :class:`N2PModelContent` class.

    Example:
        >>> # report1 is a N2PReport
        >>> report1 = model.new_report("<LC1:FR1>,<LC2:FR1>", False, "DISPLACEMENTS", "<X:NONE#>,<Y:NONE#>", False, list_n2pnodes, "LC")
        >>> report1.calculate()
        >>> headers = report1.Headers
        >>> body = report1.Body
    """

    _sortbyoptions = {"LC": 0, "IDS": 1}
    __slots__ = (
        "_vz_model",
        "_lc_incr",
        "_allincr",
        "_result",
        "_componentssections",
        "_ifenvelope",
        "_selection",
        "_optionalargs",
        "_sortby",
        "_paraminputresult",
        "_vizzerout",
    )

    def __init__(self, vz_model, lc_incr: str, allincr: bool, result: str, componentssections: str, ifenvelope: bool,
                 selection: list[N2PNode, N2PElement], sortby: str, aveSections=-1, cornerData=False, aveNodes=-1,
                 variation=100, realPolar=0, coordsys: int = -1000, v1: Union[tuple, np.ndarray] = (1, 0, 0),
                 v2: Union[tuple, np.ndarray] = (0, 1, 0)):

        self._vz_model = vz_model
        self._lc_incr = lc_incr
        self._allincr = allincr
        self._result = result
        self._componentssections = componentssections
        self._ifenvelope = ifenvelope
        self._selection = selection
        self._optionalargs = {"aveSections": aveSections, "cornerData": cornerData, "aveNodes": aveNodes,
                 "variation": variation, "realPolar": realPolar, "coordsys": coordsys, "v1": v1, "v2": v2}

        sortby = sortby.upper()
        if sortby in self._sortbyoptions.keys():
            self._sortby = sortby
        else:
            N2PLog.Error.E311()

        self._paraminputresult = N2ParamInputResults.structResults(0)
        self._paraminputresult.Result = result
        self._paraminputresult.aveSection = aveSections
        self._paraminputresult.cornerData = cornerData
        self._paraminputresult.aveIntra = aveNodes
        self._paraminputresult.variation = variation
        self._paraminputresult.real_cartesian_polar = realPolar

        if coordsys > 0:
            self._paraminputresult.coordSys = coordsys

        elif coordsys < 0 and (v1 != (1, 0, 0) or v2 != (0, 1, 0)):
            # Esto es una array de doubles. Si se quiere hacer una transformacion tanto en sistemas ya definidos en
            # el solver como por el usuario hay que pasarlo como argumento de N2ParamInputResult
            new_sys = _get_axis(v1, v2)
            new_sys = _numpytonet(new_sys)

            self._paraminputresult.coordSys = -10
            self._paraminputresult.orientationcoordinatesystem = new_sys

        elif coordsys == -1:
            self._paraminputresult.coordSys = coordsys

        self._vizzerout = None

    def calculate(self) -> None:
        """Method that actually generate the report using the object attributes."""
        ids = _numpytonet(np.array([ele.InternalID for ele in self._selection], dtype=np.int64))
        obj_array = Array.CreateInstance(Object, 0)
        
        selectionType = N2Enums.selectionType(0)
        if isinstance(self._selection[0], N2PNode):
            selectionType = N2Enums.selectionType(1)
            
        error, self._vizzerout = N2Report.GenerateReport(self._vz_model, ids, self._lc_incr, self._allincr, self._componentssections,
                                         self._paraminputresult, N2Report.SortBy(self._sortbyoptions[self._sortby]),
                                         selectionType, self._ifenvelope, obj_array)

        if error < 0:
            N2PLog.Error.E314()

    def to_csv(self, path: str) -> None:
        """ Method that saves the report in a csv text format in the document specified in the argument. It uses the
        current delimiter specified in the Windows Regional Setting.

        Args:
            path (str): path of the text file
        """
        np.savetxt(path, np.vstack((self.Headers, self.Body)), delimiter=N2Report.ConfigRegionalSettings(), fmt='%s')

    @property
    def Headers(self) -> np.ndarray:
        """Returns a ndarray of strings with the headers"""
        if not self._vizzerout:
            self.calculate()
        return np.array(self._vizzerout[0])

    @property
    def Body(self) -> np.ndarray:
        """Returns a ndarray of strings with the results of the report asked"""
        if not self._vizzerout:
            self.calculate()
        cs_array = np.array(self._vizzerout[1])
        d2 = len(self.Headers)
        d1 = len(cs_array)//d2
        return cs_array.reshape(d1, d2)

    @property
    def LC_FR(self) -> str:
        """Formula with the load cases and increments/frames"""
        return self._lc_incr

    @property
    def Result(self) -> str:
        """Result where de components are asked"""
        return self._result

    @property
    def CompSections(self) -> str:
        """Formula with the components and it sections"""
        return self._componentssections

    @property
    def Envelope(self) -> bool:
        """True if the envelope of the elements/nodes is asked"""
        return self._ifenvelope

    @property
    def Selection(self) -> list[Union[N2PNode, N2PElement]]:
        """List of N2PNodes or N2PElement where the results for the report is asked"""
        return self._selection

    @property
    def SortBy(self) -> str:
        """Can be "LC" if is load case shorted or "IDS" if is by id of the element/node. ("LC" means all the elements
        for LC1, then all elements for LC2... While "IDS" is for element1 all LC, then element2 for all LC...)"""
        return self._sortby

    @property
    def OptianlArgs(self) -> dict:
        """Dictionary with the values of the optional arguments:
        "aveSections", "cornerData", "aveNodes", "variation",  "realPolar", "coordsys", "v1", "v2"
        """
        return self._optionalargs
