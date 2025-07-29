#
from NaxToPy.Core.Errors.N2PLog import N2PLog

class N2PFastenerSystem:

    """
    Class that represents a specific fastener designation whose values need to be defined in order to 
    obtain RF values for one or more failure modes

    Attributes:
        Designation: fastener system name (str)
        Fastener_pin_single_SH_allow: fastener pin single shear strength allowable [Force] (float)
        Fastener_collar_single_SH_allow: fastener collar single shear strength allowable [Force] (float)
        Fastener_pin_tensile_allow: fastener pin tensile strength allowable [Force] (float)
        Fastener_collar_tensile_allow: fastener collar tensile strength allowable [Force] (float)
        D_head: head diameter (float)
        D_tail: tail diameter (float)
        D_nom: nominal diameter (float)
        Configuration: BOLT or RIVET or SOLID (str) (Default: BOLT)
        FastenerType: LOCK or BLIND (str) (Default: LOCK)
        FastenerInstallation: PERMANENT or REMOVABLE or QUICK RELEASE (str) (Default: PERMANENT)
        FastenerHead: PAN or CSK (str) (Default: PAN)
        FloatingNut: True or False (bool) (Default: False)
        AluminumNut: True or False (bool) (Default: False)
    """

    # N2PFastenerSystem ----------------------------------------------------------------------------------------
    def __init__(self): 

        """
        The constructor creates an empty N2PGetFasteners instance. Its attributes must be added as properties.

        Calling example:
            >>> Fastener_HWGT315 = N2PFastenerSystem()
            >>> Fastener_HWGT315.Designation = "HWGT315-LEADING-EDGE"
            >>> Fastener_HWGT315.Fastener_pin_single_SH_allow = 5000.0
            >>> Fastener_HWGT315.Fastener_collar_single_SH_allow = 6000.0
            >>> Fastener_HWGT315.Fastener_pin_tensile_allow = 7000.0
            >>> Fastener_HWGT315.Fastener_collar_tensile_allow = 8000.0
            >>> Fastener_HWGT315.D_head = 10.0
            >>> Fastener_HWGT315.D_tail = 9.0
            >>> Fastener_HWGT315.D_nom = 5.0
            >>> Fastener_HWGT315.Configuration = "RIVET" (optional)
            >>> Fastener_HWGT315.FastenerType = "LOCK" (optional)
            >>> Fastener_HWGT315.FastenerInstallation = "REMOVABLE" (optional)
            >>> Fastener_HWGT315.FastenerHead = "PAN" (optional)
            >>> Fastener_HWGT315.FloatingNut = False (optional)
            >>> Fastener_HWGT315.AluminumNut = False (optional)
        """

        self._designation: str = None
        self._fastener_pin_single_SH_allow: float = None
        self._fastener_collar_single_SH_allow: float = None
        self._fastener_pin_tensile_allow: float = None
        self._fastener_collar_tensile_allow: float = None
        self._d_head: float = None
        self._d_tail: float = None
        self._d_nom: float = None
        self._configuration: str = "BOLT"
        self._fastenertype: str = "LOCK"
        self._fastenerinstallation: str = "PERMANENT"
        self._fastenerhead: str = "PAN"
        self._floatingnut: bool = False
        self._aluminumnut: bool = False

    # -----------------------------------------------------------------------------------------------------------
    
    # Getters ---------------------------------------------------------------------------------------------------
    @property
    def Designation(self) -> str:
        """
        Property that returns the designation of the fastener.
        """

        return self._designation
    #------------------------------------------------------------------------------------------------------------

    @property
    def Fastener_pin_single_SH_allow(self) -> float:
        """
        Property that returns the fastener pin single shear strength allowable.
        """

        return self._fastener_pin_single_SH_allow
    #------------------------------------------------------------------------------------------------------------

    @property
    def Fastener_collar_single_SH_allow(self) -> float:
        """
        Property that returns the fastener collar single shear strength allowable.
        """

        return self._fastener_collar_single_SH_allow
    #------------------------------------------------------------------------------------------------------------

    @property
    def Fastener_pin_tensile_allow(self) -> float:
        """
        Property that returns the of the fastener pin tensile strength allowable.
        """

        return self._fastener_pin_tensile_allow
    #------------------------------------------------------------------------------------------------------------

    @property
    def Fastener_collar_tensile_allow(self) -> float:
        """
        Property that returns the of the fastener collar tensile strength allowable.
        """

        return self._fastener_collar_tensile_allow
    #------------------------------------------------------------------------------------------------------------

    @property
    def D_head(self) -> float:
        """
        Property that returns the head diameter of the fastener.
        """

        return self._d_head
    #------------------------------------------------------------------------------------------------------------

    @property
    def D_tail(self) -> float:
        """
        Property that returns the tail diameter of the fastener.
        """

        return self._d_tail
    #------------------------------------------------------------------------------------------------------------

    @property
    def D_nom(self) -> float:
        """
        Property that returns the nominal diameter of the fastener.
        """

        return self._d_nom
    #------------------------------------------------------------------------------------------------------------

    @property
    def Configuration(self) -> str:
        """
        Property that returns the fastener configuration (RIVET/BOLT/SOLID) (Default: BOLT).
        """

        return self._configuration
    #------------------------------------------------------------------------------------------------------------

    @property
    def FastenerType(self) -> str:
        """
        Property that returns the fastener configuration (LOCK/BLIND) (Default: LOCK).
        """

        return self._fastenertype
    #------------------------------------------------------------------------------------------------------------

    @property
    def FastenerInstallation(self) -> str:
        """
        Property that returns the fastener installation (PERMANENT/REMOVABLE/QUICK RELEASE) (Default: PERMANENT).
        """

        return self._fastenerinstallation
    #------------------------------------------------------------------------------------------------------------

    @property
    def FastenerHead(self) -> float:
        """
        Property that returns the fastener head geometry (PAN/CSK) (Default: PAN).
        """

        return self._fastenerhead
    #------------------------------------------------------------------------------------------------------------

    @property
    def FloatingNut(self) -> bool:
        """
        Property that returns if the fastener has a floating nut (True) or not (False).
        """

        return self._floatingnut
    #------------------------------------------------------------------------------------------------------------

    @property
    def AluminumNut(self) -> bool:
        """
        Property that returns if the nut is made out of aluminum (True) or not (False).
        """

        return self._aluminumnut
    #------------------------------------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------------------------------

    # Setters ---------------------------------------------------------------------------------------------------
    @Designation.setter
    def Designation(self, value: str):

        # "value"must be a string to be accepted and its length is checked.
        if not isinstance(value, str):
            msg = N2PLog.Critical.C900('Fastener Designation', 'a string')
            raise Exception(msg)
        else:
            # Only if the length limits is respected, the value is stored
            if len(value) <= 30:
                self._designation = value
            else:
                msg = N2PLog.Critical.C900('Fastener Designation', 'have 30 (or less) characters')
                raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @Fastener_pin_single_SH_allow.setter
    def Fastener_pin_single_SH_allow(self, value: float):

        # "value" must be a positive float or integer to be accepted 
        if type(value) == float and value > 0:
            self._fastener_pin_single_SH_allow = value
        elif type(value) == int and value > 0:
            self._fastener_pin_single_SH_allow = float(value)
        else:
            msg = N2PLog.Critical.C900('Fastener_pin_single_SH_allow', 'a positive float/integer')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @Fastener_collar_single_SH_allow.setter
    def Fastener_collar_single_SH_allow(self, value: float):

        # "value" must be a positive float or integer to be accepted
        if type(value) == float and value > 0:
            self._fastener_collar_single_SH_allow = value
        elif type(value) == int and value > 0:
            self._fastener_collar_single_SH_allow = float(value)
        else:
            msg = N2PLog.Critical.C900('Fastener_collar_single_SH_allow', 'a positive float/integer')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @Fastener_pin_tensile_allow.setter
    def Fastener_pin_tensile_allow(self, value: float):

        # "value" must be a positive float or integer to be accepted
        if type(value) == float and value > 0:
            self._fastener_pin_tensile_allow = value
        elif type(value) == int and value > 0:
            self._fastener_pin_tensile_allow = float(value)
        else:
            msg = N2PLog.Critical.C900('Fastener_pin_tensile_allow','a positive float/integer')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @Fastener_collar_tensile_allow.setter
    def Fastener_collar_tensile_allow(self, value: float):

        # "value" must be a positive float or integer to be accepted
        if type(value) == float and value > 0:
            self._fastener_collar_tensile_allow = value
        elif type(value) == int and value > 0:
            self._fastener_collar_tensile_allow = float(value)
        else:
            msg = N2PLog.Critical.C900('Fastener_collar_tensile_allow','a positive float/integer')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @D_head.setter
    def D_head(self, value: float):

        # "value" must be a positive float or integer to be accepted
        if type(value) == float and value > 0:
            self._d_head = value
        elif type(value) == int and value > 0:
            self._d_head = float(value)
        else:
            msg = N2PLog.Critical.C900('D_head','a positive float/integer')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------
    
    @D_tail.setter
    def D_tail(self, value: float):

        # "value" must be a positive float or integer to be accepted
        if type(value) == float and value > 0:
            self._d_tail = value
        elif type(value) == int and value > 0:
            self._d_tail = float(value)
        else:
            msg = N2PLog.Critical.C900('D_tail','a positive float/integer')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @D_nom.setter
    def D_nom(self, value: float):

        # "value" must be a positive float or integer to be accepted
        if type(value) == float and value > 0:
            self._d_nom = value
        elif type(value) == int and value > 0:
            self._d_nom = float(value)
        else:
            msg = N2PLog.Critical.C900('D_tail','a positive float/integer')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @Configuration.setter
    def Configuration(self, value: str):

        # "value" must be a str ("RIVET", "BOLT" or "SOLID") to be accepted
        if type(value) == str:
            if value == "RIVET" or value =="BOLT" or value =="SOLID":
                self._configuration = value
            else:
                msg = N2PLog.Critical.C900('Configuration',"'RIVET' or 'BOLT' or 'SOLID'")
                raise Exception(msg)
        else:
            msg = N2PLog.Critical.C900('Configuration','a string')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @FastenerType.setter
    def FastenerType(self, value: str):

        # "value" must be a str ("LOCK" or "BLIND") to be accepted
        if type(value) == str:
            if value == "LOCK" or value =="BLIND":
                self._fastenertype = value
            else:
                msg = N2PLog.Critical.C900('FastenerType',"'LOCK' or 'BLIND'")
                raise Exception(msg)
        else:
            msg = N2PLog.Critical.C900('FastenerType','a string')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @FastenerInstallation.setter
    def FastenerInstallation(self, value: str):

        # "value" must be a str ("PERMANENT", "REMOVABLE" or "QUICK RELEASE") to be accepted
        if type(value) == str:
            if value == "PERMANENT" or value == "REMOVABLE" or value =="QUICK RELEASE":
                self._fastenerinstallation = value
            else:
                msg = N2PLog.Critical.C900('FastenerInstallation',"'PERMANENT' or 'REMOVABLE' or 'QUICK RELEASE'")
                raise Exception(msg)
        else:
            msg = N2PLog.Critical.C900('FastenerInstallation','a string')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @FastenerHead.setter
    def FastenerHead(self, value: str):

        # "value" must be a str ("PAN" or "CSK") to be accepted
        if type(value) == str:
            if value=="PAN" or value=="CSK":
                self._fastenerhead = value
            else:
                msg = N2PLog.Critical.C900('FastenerHead',"'PAN' or 'CSK'")
                raise Exception(msg)
        else:
            msg = N2PLog.Critical.C900('FastenerHead','a string')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @FloatingNut.setter
    def FloatingNut(self, value: bool):

        # "value" must be a bool to be accepted.
        if type(value) == bool:
            if value == True or value == False:
                self._floatingnut = value
            else:
                msg = N2PLog.Critical.C900('FloatingNut','True or False')
                raise Exception(msg)
        else:
            msg = N2PLog.Critical.C900('FloatingNut','a bool')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------

    @AluminumNut.setter
    def AluminumNut(self, value: bool):

        # "value" must be a bool to be accepted.
        if type(value) == bool:
            if value == True or value == False:
                self._aluminumnut = value
            else:
                msg = N2PLog.Critical.C900('AluminumNut','True or False')
                raise Exception(msg)
        else:
            msg = N2PLog.Critical.C900('AluminumNut','a bool')
            raise Exception(msg)
    #------------------------------------------------------------------------------------------------------------