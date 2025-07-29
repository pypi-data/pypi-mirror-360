from __future__ import annotations
from NaxToPy.Modules.static.fasteners.joints.N2PPlate import N2PPlate
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint
from NaxToPy.Core.Errors.N2PLog import N2PLog 
#
class N2PJointAnalysisParameters:

    """
    class that represents a specific INPUT parameters to obtain the joint RF values (for compositemetal plates and bolt)

    Attributes
        ShearType: str -> defines the support condition for each N2PJoint depending on the surrounding structure and
        the joint configuration. (str = [DLS, SLS-S, SLS-U]) (Default SLS-U)
        CenvMet: float -> enviromental KDF for met parts. For all failure modes in the same way. (Default 1.00)
        CenvComp: float -> enviromental KDF for comp parts. For all failure modes in the same way. (Default 1.00)
        UserKDFComp: float -> user Defined Knock-Down Factor which applies to all comp failure modes at RF level. 
        Intended to account for Fitting Factor, Buttjoint, Safety Factor. (Default 1.00)
        UserKDFMet: float -> user defined Knock-Down Factor which applies to all met failure modes at RF level. 
        Intended to account for Fitting Factor, Buttjoint, Safety Factor. (Default 1.00)
        UserKDFBoltShear: float -> user defined Knock-Down factor for bolt shear failure mode at RF level.
        Intended to account for several bolt factors. (Default 1.00)
        UserKDFBoltTension: float -> user defined Knock-Down factor for bolt tension failure mode at RF level.
        Intended to account for several bolt factors. (Default 1.00)
        M: float -> slope of the composite bearing-bypass interaction curve [-] (float = [3, 4]) (Default 4.0)
        TShim: float -> total shim thickness applied to the joint. Includes solid and liquid shim. (Default 0.0)
        TShimL: float -> liquid shim thickness applied to the joint. Includes solid and liquid shim. (Default 0.0)
        CPrying: float -> aplied to the tension loads of the failure modes of the external plates. (Default 1.0)
        PT_Alpha_Met: float -> coefficient alpha of the pull-througth allowable curve for metallic plates, 
        applicable to head side (and tail side, optionally)
        PT_Gamma_Met: float -> coefficient gamma of the pull-througth allowable curve for metallic plates, 
        applicable to head side (and tail side, optionally)
        EdgeDistance: list[float] -> list which contains the edge distance of each plate of the joint. 
        EffectiveWidth: list[float] -> plate effective width.
        NetRatio: list[float] -> plate net ratio.
        NetSectionArea: list[float] -> net section area for the net section metallic failure mode.
        Coef_A_CombinedMet: list[float] -> coefficient a for combined interaction allowable curve for metallic plates.
        Coef_B_CombinedMet: list[float] -> coefficient b for combined interaction allowable curve for metallic plates.   
        Coef_Alpha_CombinedComp: list[float] -> coefficient alpha for combined interaction allowable curve for composite plates.
        Coef_Beta_CombinedComp: list[float] -> coefficient beta for combined interaction allowable curve for composite plates.
        Coef_SRF_NetSection_Met: list[float] -> stress reduction factor for net section failure of metallic plates.
    """
    __slots__=("_shear_type", 
               "_cenv_met",
               "_cenv_comp",
               "_userKDF_comp",
               "_userKDF_met",
               "_userKDF_boltshear",
               "_userKDF_bolttension",
               "_m",
               "_tshim",
               "_tshiml",
               "_cprying",
               "_pt_alpha_met",
               "_pt_gamma_met",
               "_edge_distance",
               "_effective_width",
               "_net_ratio",
               "_net_section_area",
               "_coef_a_combined_met",
               "_coef_b_combined_met",
               "_coef_alpha_combined_comp",
               "_coef_beta_combined_comp",
               "_coef_srf_netsection_met",
               "_joint")
    #
    # N2PJointAnalysisParameters ----------------------------------------------------------------------------------------
    def __init__(self, n2p_joint: N2PJoint):
        """
        Initialize a single layer of the laminate.

        Args:
            n2p_joint: N2PJoint object
        """
        self._joint = n2p_joint

        if self._joint.FastenerSystem.D_nom == None:
            msg = N2PLog.Critical.C903("D_nom",n2p_joint.ID)
            raise Exception(msg)

        # Atributes not related to a NaxtoPy object (user parameters)
        self._shear_type: str = "SLS-U"
        self._cenv_met: float = 1.00
        self._cenv_comp: float = 1.00
        self._userKDF_comp: float = 1.00
        self._userKDF_met: float = 1.00
        self._userKDF_boltshear: float = 1.00
        self._userKDF_bolttension: float = 1.00
        self._m: float = 4.0
        self._tshim: float = 0.0
        self._tshiml: float = 0.0
        self._cprying: float = 1.00
        self._pt_alpha_met: float = 150.0
        self._pt_gamma_met: float = 270.0

        # Atributes related to (N2PJoint)-(N2PPlate)-(N2PFastenerSystem) objects
        self._edge_distance: list = []
        self._effective_width: list = []
        self._net_ratio: list = []
        self._net_section_area: list = []
    
        # Atributes related to (N2PJoint) - (N2PFastenerSystem) objects
        self._coef_a_combined_met: list = []
        self._coef_b_combined_met: list = []
        self._coef_alpha_combined_comp: list = []
        self._coef_beta_combined_comp: list = []
        self._coef_srf_netsection_met: list = []

    # Getters ---------------------------------------------------------------------------------------------------
    @property
    def ShearType(self) -> str:
        """
        Property that returns the shear_type parameter of the joint.
        """
        return self._shear_type
    #------------------------------------------------------------------------------------------------------------

    @property
    def CenvMet(self) -> float:
        """
        Property that returns the joint enviromental KDF for the metallic parts.
        """
        return self._cenv_met
    #------------------------------------------------------------------------------------------------------------

    @property
    def CenvComp(self) -> float:
        """
        Property that returns the joint enviromental KDF for the composite parts.
        """
        return self._cenv_comp  
    #------------------------------------------------------------------------------------------------------------

    @property
    def UserKDFComp(self) -> float:
        """
        Property that returns the joint user defined KDF for the composite parts.
        """
        return self._userKDF_comp
    #------------------------------------------------------------------------------------------------------------   

    @property
    def UserKDFMet(self) -> float:
        """
        Property that returns the joint user defined KDF for the metallic parts.
        """
        return self._userKDF_met
    #------------------------------------------------------------------------------------------------------------   

    @property
    def UserKDFBoltShear(self) -> float:
        """
        Property that returns the joint user defined KDF for the bolt shear.
        """
        return self._userKDF_boltshear
    #------------------------------------------------------------------------------------------------------------ 

    @property
    def UserKDFBoltTension(self) -> float:
        """
        Property that returns the joint user defined KDF for the bolt tension.
        """
        return self._userKDF_bolttension
    #------------------------------------------------------------------------------------------------------------ 

    @property
    def M(self) -> float:
        """
        Property that returns the slope of the composite bearing-bypass interaction curve.
        """        
        return self._m
    #------------------------------------------------------------------------------------------------------------   

    @property
    def TShim(self) -> float:
        """
        Property that returns the total shim thickness (solid + liquid) of the joint.
        """
        return self._tshim
    #------------------------------------------------------------------------------------------------------------   

    @property
    def TShimL(self) -> float:
        """
        Property that returns the liquid shim thickness of the joint.
        """
        return self._tshiml
    #------------------------------------------------------------------------------------------------------------   

    @property
    def CPrying(self) -> float:
        """
        Property that returns the prying factor of the joint.
        """
        return self._cprying
    #------------------------------------------------------------------------------------------------------------

    @property
    def EdgeDistance(self) -> list:
        """
        Property that returns a list of each plate edge distance.
        """
        return self._edge_distance
    #------------------------------------------------------------------------------------------------------------

    @property
    def EffectiveWidth(self) -> list:
        """
        Property that returns a list of each palte effective width (W).
        """
        return self._effective_width
    #------------------------------------------------------------------------------------------------------------

    @property
    def NetRatio(self) -> list:
        """
        Property that returns a list of each plate net ratio (D/W).
        """
        return self._net_ratio
    #------------------------------------------------------------------------------------------------------------

    @property
    def NetSectionArea(self) -> list:
        """
        Property that returns a list of each plate net section area (W-D)*t.
        """
        return self._net_section_area
    #------------------------------------------------------------------------------------------------------------

    @property
    def Coef_A_CombinedMet(self) -> list:
        """
        Property that returns a list of each plate coefficient "a" for combined interaction allowable curve
        for metallic plates.
        """
        return self._coef_a_combined_met
    #------------------------------------------------------------------------------------------------------------

    @property
    def Coef_B_CombinedMet(self) -> list:
        """
        Property that returns a list of each plate coefficient "b" for combined interaction allowable curve
        for metallic plates.
        """
        return self._coef_b_combined_met
    #------------------------------------------------------------------------------------------------------------

    @property
    def PT_Alpha_Met(self) -> float:
        """
        Property that returns the coefficient alpha of the pull-througth allowable curve 
        for metallic plates.
        """
        return self._pt_alpha_met
    #------------------------------------------------------------------------------------------------------------

    @property
    def PT_Gamma_Met(self) -> float:
        """
        Property that returns a list of each plate coefficient gamma of the pull-througth allowable curve 
        for metallic plates.
        """
        return self._pt_gamma_met
    #------------------------------------------------------------------------------------------------------------

    @property
    def Coef_Alpha_CombinedComp(self) -> list:
        """
        Property that returns a list of each plate coefficient "alpha" for combined interaction allowable curve
        for composite plates.
        """
        return self._coef_alpha_combined_comp
    #------------------------------------------------------------------------------------------------------------

    @property
    def Coef_Beta_CombinedComp(self) -> list:
        """
        Property that returns a list of each plate coefficient "beta" for combined interaction allowable curve
        for composite plates.
        """
        return self._coef_beta_combined_comp
    #------------------------------------------------------------------------------------------------------------

    @property
    def Coef_SRF_NetSection_Met(self) -> list:
        """
        Property that returns a list of each plate coefficient srf for net section failure mode of metallic
        plates.
        """
        return self._coef_srf_netsection_met
    #------------------------------------------------------------------------------------------------------------

    # Setters ---------------------------------------------------------------------------------------------------
    @ShearType.setter
    def ShearType(self, value: str) -> None:

        if isinstance(value, str) and (value == "DLS" or value =="SLS-S" or value =="SLS-U"):
            self._shear_type = value
        else:
            N2PLog.Error.E902("ShearType", "'DLS' or 'SLS-S' or 'SLS-U'")
    #------------------------------------------------------------------------------------------------------------

    @CenvMet.setter
    def CenvMet(self, value: float) -> None:

        if isinstance(value, (float, int)) and (0 < value <= 1.0):
            self._cenv_met = float(value)
        else:
            N2PLog.Error.E902("CenvMet", "a positive float or integer between (0.0, 1.0]")
    #------------------------------------------------------------------------------------------------------------    

    @CenvComp.setter
    def CenvComp(self, value: float) -> None:

        if isinstance(value, (float, int)) and (0 < value <= 1.0):
            self._cenv_comp = float(value)
        else:
            N2PLog.Error.E902("CenvComp", "a positive float or integer between (0.0, 1.0]")
    #------------------------------------------------------------------------------------------------------------ 

    @UserKDFComp.setter
    def UserKDFComp(self, value: float) -> None:

        if isinstance(value, (float, int)) and (0 < value <= 1.0):
            self._userKDF_comp = float(value)
        else:
            N2PLog.Error.E902("UserKDFComp", "a positive float or integer between (0.0, 1.0]")
    #------------------------------------------------------------------------------------------------------------ 

    @UserKDFMet.setter
    def UserKDFMet(self, value: float) -> None:

        if isinstance(value, (float, int)) and (0 < value <= 1.0):
            self._userKDF_met = float(value)
        else:
            N2PLog.Error.E902("UserKDFMet", "a positive float or integer between (0.0, 1.0]")
    #------------------------------------------------------------------------------------------------------------ 

    @UserKDFBoltShear.setter
    def UserKDFBoltShear(self, value: float) -> None:

        if isinstance(value, (float, int)) and (0 < value <= 1.0):
            self._userKDF_boltshear = float(value)
        else:
            N2PLog.Error.E902("UserKDFBoltShear", "a positive float or integer between (0.0, 1.0]")
    #------------------------------------------------------------------------------------------------------------ 

    @UserKDFBoltTension.setter
    def UserKDFBoltTension(self, value: float) -> None:

        if isinstance(value, (float, int)) and (0 < value <= 1.0):
            self._userKDF_bolttension = float(value)
        else:
            N2PLog.Error.E902("UserKDFBoltTension", "a positive float or integer between (0.0, 1.0]")
    #------------------------------------------------------------------------------------------------------------ 

    @M.setter
    def M(self, value: float) -> None:

        if isinstance(value, (float, int)) and (3 <= value <= 4):
            self._m = float(value)
        else:
            N2PLog.Error.E902("M", "a float/integer between 3.0 and 4.0")
    #------------------------------------------------------------------------------------------------------------     

    @TShim.setter
    def TShim(self, value: float) -> None:

        if isinstance(value, (float, int)) and (value >= 0):
            self._tshim = float(value)
        else:
            N2PLog.Error.E902("TShim", "a positive float or integer")
    #------------------------------------------------------------------------------------------------------------  

    @TShimL.setter
    def TShimL(self, value: float) -> None:

        if isinstance(value, (float, int)) and (value >= 0):
            self._tshiml = float(value)
        else:
            N2PLog.Error.E902("TShimL", "a positive float or integer")
    #------------------------------------------------------------------------------------------------------------        
    
    @CPrying.setter
    def CPrying(self, value: float) -> None:

        if isinstance(value, (float, int)) and (value >= 1):
            self._cprying = float(value)
        else:
            N2PLog.Error.E902("CPrying", "a positive float or integer greater than 1")
    #------------------------------------------------------------------------------------------------------------       

    @EdgeDistance.setter
    def EdgeDistance(self, value: list) -> None:

        if isinstance(value, list) and all(isinstance(i, (float, int)) for i in value) and all(i > 0 for i in value):
            if len(value) == len(self._joint.PlateList):
                self._edge_distance = value
            else:
                N2PLog.Error.E903("EdgeDistance","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("EdgeDistance", "a list of positive floats and/or integers")
    #------------------------------------------------------------------------------------------------------------   

    @EffectiveWidth.setter
    def EffectiveWidth(self, value: list) -> None:

        if isinstance(value, list) and all(isinstance(i, (float, int)) for i in value) and all(i > 0 for i in value):
            if len(value) == len(self._joint.PlateList):
                self._effective_width = value
            else:
                N2PLog.Error.E903("EffectiveWidth","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("EffectiveWidth", "a list of positive floats and/or integers")
    #------------------------------------------------------------------------------------------------------------

    @NetRatio.setter
    def NetRatio(self, value: list[float]) -> None:

        if isinstance(value, list) and all(isinstance(i, (float, int)) for i in value) and all(0 < i < 1 for i in value):
            if len(value) == len(self._joint.PlateList):
                self._net_ratio = value
            else:
                N2PLog.Error.E903("NetRatio","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("NetRatio", "a list of positive floats and/or integers between 0 and 1")
    #------------------------------------------------------------------------------------------------------------

    @NetSectionArea.setter
    def NetSectionArea(self, value: list[float]) -> None:

        if isinstance(value, list) and all(isinstance(i, (float, int)) for i in value) and all(i > 0 for i in value):
            if len(value) == len(self._joint.PlateList):
                self._net_section_area = value
            else:
                N2PLog.Error.E903("NetSectionArea","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("NetSectionArea", "a list of positive floats and/or integers")
    #------------------------------------------------------------------------------------------------------------

    @Coef_A_CombinedMet.setter
    def Coef_A_CombinedMet(self, value: list[float]) -> None:

        init_data=self._coef_a_combined_met

        if isinstance(value, list) and all(isinstance(i, (float, int, type(None))) for i in value):
            if len(value) == len(init_data):
                for i,data in enumerate(value):
                    if isinstance(data,(float, int)) and isinstance(init_data[i],(float,int)):
                        if data >0:
                            self._coef_a_combined_met[i] = data
                        else:
                            N2PLog.Error.E902("Coef_A_CombinedMet", "positive")
                    elif data == None and init_data[i] == None:
                        self._coef_a_combined_met[i] = None
                    else:
                        N2PLog.Error.E903("Coef_A_CombinedMet","has an incorrect format, check None values")
            else:
                N2PLog.Error.E903("Coef_A_CombinedMet","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("Coef_A_CombinedMet", "a list [floats-integers(>1)]/None items")
    #------------------------------------------------------------------------------------------------------------

    @Coef_B_CombinedMet.setter
    def Coef_B_CombinedMet(self, value: list[float]) -> None:
        
        init_data=self._coef_b_combined_met

        if isinstance(value, list) and all(isinstance(i, (float, int, type(None))) for i in value):
            if len(value) == len(init_data):
                for i,data in enumerate(value):
                    if isinstance(data,(float, int)) and isinstance(init_data[i],(float,int)):
                        if data >0:
                            self._coef_b_combined_met[i] = data
                        else:
                            N2PLog.Error.E902("Coef_A_CombinedMet", "positive")
                    elif data == None and init_data[i] == None:
                        self._coef_b_combined_met[i] = None
                    else:
                        N2PLog.Error.E903("Coef_B_CombinedMet","has an incorrect format, check None values")
            else:
                N2PLog.Error.E903("Coef_B_CombinedMet","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("Coef_B_CombinedMet", "a list [floats-integers(>1)]/None items")
    #------------------------------------------------------------------------------------------------------------

    @PT_Alpha_Met.setter
    def PT_Alpha_Met(self, value: float) -> None:

        if isinstance(value, (float, int)) and (value >= 1):
            self._pt_alpha_met = float(value)
        else:
            N2PLog.Error.E902("PT_Alpha_Met", "a positive float or integer greater than 1")
    #------------------------------------------------------------------------------------------------------------

    @PT_Gamma_Met.setter
    def PT_Gamma_Met(self, value: float) -> None:

        if isinstance(value, (float, int)) and (value >= 1):
            self._pt_gamma_met = float(value)
        else:
            N2PLog.Error.E902("PT_Gamma_Met", "a positive float or integer greater than 1")
    #------------------------------------------------------------------------------------------------------------

    @Coef_Alpha_CombinedComp.setter
    def Coef_Alpha_CombinedComp(self, value: list[float]) -> None:

        init_data=self._coef_alpha_combined_comp

        if isinstance(value, list) and all(isinstance(i, (float, int, type(None))) for i in value):
            if len(value) == len(init_data):
                for i,data in enumerate(value):
                    if isinstance(data,(float, int)) and isinstance(init_data[i],(float,int)):
                        if data >= 1:
                            self._coef_alpha_combined_comp[i] = data
                        else:
                            N2PLog.Error.E902("Coef_Alpha_CombinedComp", ">1")
                    elif data == None and init_data[i] == None:
                        self._coef_alpha_combined_comp[i] = None
                    else:
                        N2PLog.Error.E903("Coef_Alpha_CombinedComp","has an incorrect format, check None values")
            else:
                N2PLog.Error.E903("Coef_Alpha_CombinedComp","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("Coef_Alpha_CombinedComp", "a list [floats-integers(>1)]/None items")
    #------------------------------------------------------------------------------------------------------------

    @Coef_Beta_CombinedComp.setter
    def Coef_Beta_CombinedComp(self, value: list[float]) -> None:

        init_data=self._coef_beta_combined_comp

        if isinstance(value, list) and all(isinstance(i, (float, int, type(None))) for i in value):
            if len(value) == len(init_data):
                for i,data in enumerate(value):
                    if isinstance(data,(float, int)) and isinstance(init_data[i],(float,int)):
                        if data >= 1:
                            self._coef_beta_combined_comp[i] = data
                        else:
                            N2PLog.Error.E902("Coef_Beta_CombinedComp", ">1")
                    elif data == None and init_data[i] == None:
                        self._coef_beta_combined_comp[i] = None
                    else:
                        N2PLog.Error.E903("Coef_Beta_CombinedComp","has an incorrect format, check None values")
            else:
                N2PLog.Error.E903("Coef_Beta_CombinedComp","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("Coef_Beta_CombinedComp", "a list [floats-integers(>1)]/None items")
    #------------------------------------------------------------------------------------------------------------

    @Coef_SRF_NetSection_Met.setter
    def Coef_SRF_NetSection_Met(self, value: list[float]) -> None:

        init_data=self._coef_srf_netsection_met

        if isinstance(value, list) and all(isinstance(i, (float, int, type(None))) for i in value):
            if len(value) == len(init_data):
                for i,data in enumerate(value):
                    if isinstance(data,(float, int)) and isinstance(init_data[i],(float,int)):
                        if 0 < data <= 1:
                            self._coef_srf_netsection_met[i] = data
                        else:
                            N2PLog.Error.E902("Coef_SRF_NetSection_Met", ">0.0 and <= 1.0")
                    elif data == None and init_data[i] == None:
                        self._coef_srf_netsection_met[i] = None
                    else:
                        N2PLog.Error.E903("Coef_SRF_NetSection_Met","has an incorrect format, check None values")
            else:
                N2PLog.Error.E903("Coef_SRF_NetSection_Met","has an incorrect size, check number of plates")
        else:
            N2PLog.Error.E902("Coef_SRF_NetSection_Met", "a list [floats-integers(>0.0 and <= 1.0)]/None items")
    #------------------------------------------------------------------------------------------------------------

    def _initialize_n2p_plate (self, plate: N2PPlate, thickness: float, proptype: str) -> None:
        """
        Initialize the N2PJoint from which the input joints dependent parameters are calculated
        
        Args:
            plate: plate of the joint to be initialised
            Thickness: thickness of the plate
            proptype: property type (PCOMP or PSHELL) of the plate
        """
        # Hole diameter
        d=self._joint.FastenerSystem.D_nom

        # Effective width & Edge distance (joint pitch)
        #-----------------------------------------------------------------------------#
        #-----------------------------------------------------------------------------#
        distance = plate.Distance
        pitch = self._joint.Pitch

        e_pitch = pitch
        e_distance = distance

        # CASE A -> Pitch data is available
        if not pitch == None:
            e = min(e_pitch,e_distance)
            w = min(2*e, pitch)
        
        # CASE B -> Pitch data is not available
        elif pitch == None:

            # CASE B.1 -> Composite Plate
            if proptype == "PCOMP":
                if e_distance >= 3*d:
                    e = 3*d
                    w = 6*d
                elif e_distance < 3*d:
                    e = e_distance
                    w = 2*e

            # CASE B.2 -> Metallic Plate
            if proptype == "PSHELL":
                if e_distance >= 2*d:
                    e = 2*d
                    w = 4*d
                elif e_distance < 2*d:
                    e = e_distance
                    w = 2*e

        # Effective width
        self._effective_width.append(w)

        # Edge distance
        self._edge_distance.append(e)
        #-----------------------------------------------------------------------------#
        #-----------------------------------------------------------------------------#

        # Assuming that net_ratio = (D_nom/EffectiveWidth)
        self._net_ratio.append(d/w)

        # Net section area
        self._net_section_area.append((w-d)*thickness)     
    #------------------------------------------------------------------------------------------------------------

    def _a_b_coefficients_met(self, thickness: float, proptype: str) -> None:
        """
        Method which assigns a & b coefficients bolt combined failure mode (metallic)

        Args:
            thickness: thickness of the plate
            proptype: property type (PCOMP or PSHELL) of the plate
        """
        # If the plate is made out of composite material, a & b coefficients calculation does not make
        # sense and, therefore, these coefficients become "None".
        if proptype == "PCOMP":
            a_coef = None
            b_coef = None

        else:
            fast_sys=self._joint.FastenerSystem

            configuration=fast_sys.Configuration
            type=fast_sys.FastenerType
            installation=fast_sys.FastenerInstallation
            head=fast_sys.FastenerHead

            t=thickness
            d=fast_sys.D_nom

            if configuration == "BOLT":
            #------------------------------ BOLT CONNECTORS--------------------------------------------
            #------------------------------------------------------------------------------------------

                #--------------------------------------------------------------------------------------
                if installation == "PERMANENT":

                    if type == "LOCK" and fast_sys.AluminumNut == "False":
                        a_coef = 2.0
                        b_coef = 3.0
                    elif type == "LOCK" and fast_sys.AluminumNut == "True":
                        a_coef = 1.0
                        b_coef = 12.0
                    elif type == "BLIND":
                        a_coef = 2.5
                        b_coef = 1.3
                    else:
                        a_coef = 2.0
                        b_coef = 3.0

                if installation == "QUICK RELEASE":
                
                    if head == "CSK":
                        a_coef = 1.3
                        b_coef = min([0.8+(t/d),1.3])
                    else:
                        a_coef = 2.0
                        b_coef = 3.0
                
                if installation == "REMOVABLE":
                        a_coef = 1.3
                        b_coef = min([0.8+(t/d),1.3])
                #--------------------------------------------------------------------------------------

            #----------------------------- RIVET CONNECTORS--------------------------------------------
            #------------------------------------------------------------------------------------------
            elif configuration == "RIVET": 

                if type == "BLIND" and fast_sys.AluminumNut == "False":
                    a_coef = 2.5
                    b_coef = 1.3
                
                else:
                    a_coef = 2.0
                    b_coef = 3.0
                
            #----------------------------- SOLID CONNECTORS--------------------------------------------
            #------------------------------------------------------------------------------------------
            else:
                if head == "PAN":
                    a_coef = 2.0
                    b_coef = 2.0
                else:
                    a_coef = 2.0
                    b_coef = 3.0
        
        self._coef_a_combined_met.append(a_coef)
        self._coef_b_combined_met.append(b_coef)
    # -----------------------------------------------------------------------------------------------------------
    
    def _alpha_beta_coefficients_comp(self, thickness: float, proptype: str, side: str) -> None:
        """
        Method which assigns alpha & beta coefficients for bolt combined failure mode (composite)
        Args:
            thickness: thickness of the plate
            proptype: property type (PCOMP or PSHELL) of the plate
            side: HEAD or TAIL
        """
        # If the plate is made out of metallic material, alpha & beta coefficients calculation does not make
        # sense and, therefore, these coefficients become "None".
        if proptype == "PSHELL":
            alpha_coef = None
            beta_coef = None
        else:
            fast_sys=self._joint.FastenerSystem

            configuration=fast_sys.Configuration
            type=fast_sys.FastenerType
            head=fast_sys.FastenerHead

            t=thickness
            d=fast_sys.D_nom

            #------------------------------------ HEAD SIDE -------------------------------------------
            #------------------------------------------------------------------------------------------
            if side == "Head":

                if configuration == "BOLT":

                    if type == "LOCK":

                        if head == "PAN":
                            alpha_coef = 2.0
                            beta_coef = 2.0

                        elif head == "CSK":
                            alpha_coef = 1.8
                            beta_coef = min([0.8+(t/d),1.8])

                    if type == "BLIND":
                        alpha_coef = 1.8
                        beta_coef = min([0.8+(t/d),1.3])

                elif configuration == "RIVET":
                    alpha_coef = 1.3
                    beta_coef = min([0.8+(t/d),1.3])

                else:
                    alpha_coef = 1.8
                    beta_coef = 1.8

            #------------------------------------ TAIL SIDE -------------------------------------------
            #------------------------------------------------------------------------------------------
            elif side == "Tail":

                if configuration == "BOLT":

                    if type == "LOCK":
                        alpha_coef = 2.0
                        beta_coef = 2.0
                    
                    elif type == "BLIND":
                        alpha_coef = 1.8
                        beta_coef = min([0.8+(t/d),1.3])

                elif configuration == "RIVET" or fast_sys.FloatingNut == True:
                    alpha_coef = 1.3
                    beta_coef = min([0.8+(t/d),1.3])

            #----------------------------------- MIDDLE SIDE ------------------------------------------
            #------------------------------------------------------------------------------------------
            else:
                alpha_coef = 1.8
                beta_coef = 1.8

        self._coef_alpha_combined_comp.append(alpha_coef)
        self._coef_beta_combined_comp.append(beta_coef)
    # -----------------------------------------------------------------------------------------------------------

    def _crf_net_section_met(self, plate: N2PPlate, proptype: str) -> None:
        """
        Method which calculates the SRF for net section RF value following the "Industrial" method
        (Only valid for PSHELL elements)

        Args:
            plate (N2PPlate): N2PPlate working as a plate
            proptype (str): PSHELL or PCOMP
        """
        c_srf_netsection: float

        # Equation coefficients
        all_coefficients = { 
                            "interval_1_7000_series": [0, 0.1235, -0.0247, 0.9553],
                            "interval_2_7000_series": [0, 0, 0.0331, 0.9485],
                            }
        
        if proptype == "PSHELL":
        
            # Plate position inside the joint
            plate_pos = self._joint.PlateElementList.index(plate.ElementList)

            # Ratio (D / W)
            neta = self._net_ratio[plate_pos]

            if neta <= 0.234:
                coefficients = all_coefficients["interval_1_7000_series"]
            elif 0.234 < neta <= 0.500:
                coefficients = all_coefficients["interval_2_7000_series"]
            else:
                coefficients = [0,0,0,1.0]
                N2PLog.Warning.W904(self._joint.ID, plate.ElementList[0].ID)
            
            a = coefficients[0]
            b = coefficients[1]
            c = coefficients[2]
            d = coefficients[3]

            c_srf_netsection = a*pow(neta,3)+b*pow(neta,2)+c*neta+d

        else:
            c_srf_netsection = None

        self._coef_srf_netsection_met.append(c_srf_netsection)
    # -----------------------------------------------------------------------------------------------------------

    def _parameters_manager(self, plate: N2PPlate, thickness: float, proptype: str, side: str) -> None:
        """
        Method which call other methods in order to fullfill the required parameters for RF calculation.
        Args:
            plate: N2PPlate
            thickness: thickness of the plate
            proptype: property type (PCOMP or PSHELL) of the plate
            side: HEAD or TAIL side of the plate
        """
        self._a_b_coefficients_met(thickness, proptype)
        self._alpha_beta_coefficients_comp(thickness, proptype, side)
        self._initialize_n2p_plate(plate, thickness, proptype)
        self._crf_net_section_met(plate, proptype)
    # -----------------------------------------------------------------------------------------------------------