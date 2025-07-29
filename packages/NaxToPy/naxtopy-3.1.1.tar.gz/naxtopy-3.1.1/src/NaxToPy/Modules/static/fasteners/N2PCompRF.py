from NaxToPy.Modules.static.fasteners.N2PGetLoadFasteners import N2PGetLoadFasteners
from NaxToPy.Modules.static.fasteners.N2PGetFasteners import N2PGetFasteners
from NaxToPy.Modules.common.property import CompositeShell
from NaxToPy.Modules.common.hdf5 import HDF5_NaxTo
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry
from NaxToPy.Core.Errors.N2PLog import N2PLog
import numpy as np
import math
import sys 
from time import time
#
class N2PCompRF:
    """
    Class that manages the RF calculation of PCOMP 2D elements based on several failures modes.
    """
    __slots__= ("_comp_elements",
                "_get_load_fasteners",
                "_get_fasteners",
                "_compshells",
                "_rf_results",
                "_c_qi_mod",
                "_elms_id_and_rfs",
                "_input_h5_comp",
                "_bea_allows_list",
                "_rf_export_location",
                "_calculation_input_echo",
                "_booleans"
                )
    
    # N2PCompRF constructor --------------------------------------------------------------------------------------
    def __init__(self):
        """
        The constructor creates an empty N2PCompRF instance. Its attributes must be addes as properties.
        """
        self._comp_elements: dict=None
        self._get_load_fasteners: N2PGetLoadFasteners=None
        self._get_fasteners: N2PGetFasteners=None
        self._compshells: dict=None
        self._c_qi_mod: dict = {}
        self._bea_allows_list: list = []
        self._rf_export_location: str=None
        self._calculation_input_echo: list = []
        self._booleans: dict = {"edge_distance_problems":False, "shim_problems": False}

    # Getters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @property
    def CompElements(self) -> dict:
        """
        Dictonary which contains all the composite elements to be studied
        """
        return self._comp_elements
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def GetLoadFasteners(self) -> N2PGetLoadFasteners:
        """
        N2PGetLoadFasteners instance. It is a compulsory input
        """
        return self._get_load_fasteners
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def GetFasteners(self) -> N2PGetFasteners:
        """
        N2PGetFasteners instance. It is a compulsory input
        """
        return self._get_fasteners
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def CompShells(self) -> dict:
        """
        Dictionary containing required CompShell-like classes information
        """
        return self._compshells
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def RFExportLocaton(self) -> str:
        """
        Path to the directory where the RFs are to be printed
        """
        return self._rf_export_location
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def CalculationInputEcho(self) -> np.array:
        """
        Numpy array which contains all the input data for Composite elements calculation
        """
        return self._calculation_input_echo
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def RFResults(self) -> np.array:
        """
        Numpy array which contains all the Metallic elements RF results
        """
        return self._rf_results

    # Setters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @CompElements.setter
    def CompElements(self, value: dict) -> None:

        self._comp_elements = value
    #-------------------------------------------------------------------------------------------------------------------

    @GetLoadFasteners.setter
    def GetLoadFasteners(self, value: N2PGetLoadFasteners) -> None:

        self._get_load_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @GetFasteners.setter
    def GetFasteners(self, value: N2PGetFasteners) -> None:

        self._get_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @CompShells.setter
    def CompShells(self, value: dict) -> None:

        self._compshells = value
    #-------------------------------------------------------------------------------------------------------------------

    @RFExportLocaton.setter
    def RFExportLocation(self, value: str) -> None:

        self._rf_export_location = value
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_pullthrough_comp_industrial(self, i, element, side, joint, plate, t) -> None:
        """
        Method used to obtain the Pull Through RF for each COMP element.

        Arg:
            element (N2PElement): composite element to be studied
            side (str): Side of the element: "Head", "Middle" or "Tail"
            joint (N2PJoint): joint object related to the element considered
            plate (N2PPlate): plate object related to the element considered
            t (float): element thickness
        """

        # Pull through fitting factor, prying and allowable value
        user_kdf = joint.JointAnalysisParameters.UserKDFComp
        c_prying = joint.JointAnalysisParameters.CPrying
        f_pt_allow = self._f_pullthrough_allow_comp_industrial(element,side,joint,t,i)

        # Only RFs are calculated if a N2PGetLoadFasteners is provided
        if not self._get_load_fasteners == None:
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                # Pull through force for LC j
                p = plate.BearingForce[loadcase_id][2]

                # Calculate RF (Reserve Factor) based on several conditions:

                # Connector under tension, the element is head/tail and the FastenerSystem is defined:
                if p>0:
                    rf_pull_through = int(((f_pt_allow*user_kdf)/(p*c_prying))*100)/100
                    rf_pull_through = format(rf_pull_through,'.2f')

                    # Array filling step
                    self._rf_results[i][0][j] = rf_pull_through

                # Connector NOT under tension, the element is head/tail and the FastenerSystem is defined:  
                elif p<=0:
                    rf_pull_through = format(9999.00,'.2f')
                    
                    # Array filling step
                    self._rf_results[i][0][j] = rf_pull_through
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_bearing_comp_industrial(self, i, element, joint, plate, t) -> float:
        """
        Method used to obtain bearing RF for each COMP element.

        Arg:
            element (N2PElement): composite element to be studied
            joint (N2PJoint): joint object related to the element considered
            plate (N2PPlate): plate object related to the element considered
            t (float): element thickness

        Returns:
            f_BEA_allow (float): Bearing allowable calculated in Bearing method
        """

        d=joint.FastenerSystem.D_nom
        user_kdf=joint.JointAnalysisParameters.UserKDFComp
        f_BEA_allow=self._f_bearing_allow_comp_industrial(element,joint,t,i)

        # Only RFs are calculated if a N2PGetLoadFasteners is provided
        if not self._get_load_fasteners == None:
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                # Bearing force for LC j
                bearing_load=pow((pow(plate.BearingForce[loadcase_id][0],2)+pow(plate.BearingForce[loadcase_id][1],2)),0.5)

                if not math.isnan(bearing_load):
                    bea_stress=bearing_load/(t*d)
                    if bea_stress == 0:
                        # Default RF for zero bearing stress
                        rf_bearing=format(9999.00,'.2f')
                    else:
                        rf_bearing=int(((f_BEA_allow*user_kdf)/(bea_stress))*100)/100
                        rf_bearing=format(rf_bearing,'.2f')
                        
                    self._rf_results[i][1][j] = rf_bearing

        return f_BEA_allow
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_bearingbypass_comp_industrial(self, i, element, joint, plate, t, f_BEA_allow) -> None:
        """
        Method used to obtain bearing-bypass RF for each COMP element.

        Arg:
            element (N2PElement): composite element to be studied
            joint (N2PJoint): joint object related to the element considered
            plate (N2PPlate): plate object related to the element considered
            t (float): element thickness
            f_BEA_allow (float): Bearing allowable calculated in Bearing method
        """

        user_kdf=joint.JointAnalysisParameters.UserKDFComp 
        m_bypass=joint.JointAnalysisParameters.M
        d=joint.FastenerSystem.D_nom

        # A critical error is raised if the nominal diameter has not been defined
        if d==None:
            msg = N2PLog.Critical.C903("D_nom",joint.ID)
            raise Exception(msg)
        
        # Net section allowables
        net_allow=self._f_netsection_allow_comp_industrial(element, joint,i)
        s_netsection_tension=net_allow[0]
        s_netsection_compres=net_allow[1]

        # Only RFs are calculated if a N2PGetLoadFasteners is provided
        if not self._get_load_fasteners == None:
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                # BY-PASS STRESS
                # Nx, Ny, Nxy
                nx=plate.NxBypass[loadcase_id]
                ny=plate.NyBypass[loadcase_id]
                nxy=plate.NxyBypass[loadcase_id]

                # Compression curve side
                n_min_ppal=(nx+ny)*0.5-pow((pow((nx-ny)*0.5,2)+pow(nxy,2)),0.5)
                min_ppal=n_min_ppal/t

                # Tension curve side
                n_max_ppal=(nx+ny)*0.5+pow((pow((nx-ny)*0.5,2)+pow(nxy,2)),0.5)
                max_ppal=n_max_ppal/t

                # BEARING FORCE
                bearing_force=pow((pow(plate.BearingForce[loadcase_id][0],2)+pow(plate.BearingForce[loadcase_id][1],2)),0.5)

                if math.isnan(min_ppal) or math.isnan(max_ppal) or math.isnan(bearing_force) or joint.FastenerSystem is None:
                    rf_bearing_bypass=[None]
                
                elif (not all(math.isnan(j) for j in (min_ppal, max_ppal, bearing_force))) and joint.FastenerSystem is not None:
                    # Bearing Stress
                    bearing_stress=bearing_force/(t*d)

                    # Logic filter:
                    if (min_ppal < 0) and (max_ppal <= 0):
                        # CASE (#1) - >> MIN PPAL = NEGATIVE ; MAX PPAL = NEGATIVE or ZERO
                        point_P = (min_ppal, bearing_stress)
                        rf_bearing_bypass = self._bypass_intersection_finder_compression_side(f_BEA_allow,s_netsection_compres, point_P, user_kdf)
                        
                    elif (min_ppal >= 0) and (max_ppal > 0):
                        # CASE (#2) - >> MIN PPAL = POSITIVE OR ZERO ; MAX PPAL = POSITIVE
                        point_P = (max_ppal, bearing_stress)
                        rf_bearing_bypass = self._bypass_intersection_finder_tension_side(f_BEA_allow,s_netsection_tension, point_P, user_kdf, m_bypass)

                    elif (min_ppal < 0) and (max_ppal > 0):
                        # CASE (#3) - >> MIN PPAL = NEGATIVE ; MAX PPAL = POSITIVE
                        point_P_min = (min_ppal, bearing_stress)
                        point_P_max = (max_ppal, bearing_stress)
                        rf_min_ppal = self._bypass_intersection_finder_compression_side(f_BEA_allow, s_netsection_compres, point_P_min, user_kdf)
                        
                        rf_max_ppal = self._bypass_intersection_finder_tension_side(f_BEA_allow, s_netsection_tension, point_P_max, user_kdf, m_bypass)
                        
                        # Boths rfs are calculated but only the minimum is displayed
                        if rf_min_ppal[0] < rf_max_ppal[0]:
                            rf_bearing_bypass = rf_min_ppal
                        else:
                            rf_bearing_bypass = rf_max_ppal

                    elif (min_ppal == max_ppal):
                        # CASE (3) - >> MIN PPAL = MAX PPAL
                        point_P_min = (min_ppal, bearing_stress)
                        point_P_max = (max_ppal, bearing_stress)
                        if min_ppal <= 0:
                            rf_bearing_bypass = self._bypass_intersection_finder_compression_side(f_BEA_allow, s_netsection_compres, point_P_min, user_kdf)
                        elif min_ppal > 0:
                            rf_bearing_bypass  = self._bypass_intersection_finder_tension_side(f_BEA_allow, s_netsection_tension, point_P_max, user_kdf, m_bypass)
                
                # Array filling step  
                self._rf_results[i][2][j] = rf_bearing_bypass[0]
    #-------------------------------------------------------------------------------------------------------------------

    def _f_pullthrough_allow_comp_industrial(self, element_2d, side, joint, t, i) -> float:
        """
        Method which calculates the allowable pull through value following the "Industrial" method
        (Only valid for COMP elements)

        Args:
            element_2d (N2PElement): composite element to be studied
            side (str): Side of the element: "Head", "Middle" or "Tail"
            joint (N2PJoint): joint object related to the element considered
            t (float): element thickness

        Returns:
            f_pt_allow (float): allowable pull through load (maximum force)
        """

        f_pt_allow:float

        # Connector head type and laminate f_PT:
        head = joint.FastenerSystem.FastenerHead
        f_PT=self._compshells[element_2d.Prop[0]].PTAllowable

        # If the code detects that f_PT == 100000000.0 it is because the method "_laminate_PT_allow_min_obtention"
        # from N2PCalculatorRFJoints couldn't find a way to obtain the pull-through value
        if f_PT == 100000000.0:
            msg = N2PLog.Critical.C906(element_2d.Prop[0])
            raise Exception(msg)

        # Bolt tensile allowable value and head/nut diameter
        if side =="Head":
            # Head side tensile allowable
            f_T=joint.FastenerSystem.Fastener_pin_tensile_allow

            # An error is raised if f_T of the head has not been defined
            if f_T==None:
                msg = N2PLog.Critical.C903("Fastener_pin_tensile_allow",joint.ID)
                raise Exception(msg)

            # Head diameter
            d=joint.FastenerSystem.D_head

            # An error is raised if f_T of the head has not been defined
            if d==None:
                msg = N2PLog.Critical.C903("D_head",joint.ID)
                raise Exception(msg)
            
        elif side == "Tail":
            # Tail side tensile allowable
            f_T=joint.FastenerSystem.Fastener_collar_tensile_allow

            # An error is raised if f_T of the head has not been defined
            if f_T==None:
                msg = N2PLog.Critical.C903("Fastener_collar_tensile_allow",joint.ID)
                raise Exception(msg)
            
            d=joint.FastenerSystem.D_tail
            if d==None:
                msg = N2PLog.Critical.C903("D_tail",joint.ID)
                raise Exception(msg)
        
        # Method parameters
        c_env = joint.JointAnalysisParameters.CenvComp
        c_bv = 1.0
        ksc = 1.0

        # KDF due to head CSK o PAN (for tail side = 1.00)
        if side =="Head" and head == "CSK":
            c_bt = 0.90
        elif side == "Head" and head == "PAN":
            c_bt = 1.00
        elif side =="Tail":
            c_bt = 1.00

        # Allowable tensile load=min[pull-through load, bolt tension load]
        f_pt_allow=min((2/3)*f_PT*np.pi*d*t*c_bv*c_env*c_bt*(1/ksc),f_T)

        # Input HDF5 file filling step
        self._input_h5_comp[i][1] = f_PT
        self._input_h5_comp[i][2] = f_T
        self._input_h5_comp[i][3] = c_bv
        self._input_h5_comp[i][4] = c_bt
        self._input_h5_comp[i][5] = ksc
        self._input_h5_comp[i][6] = f_pt_allow

        return f_pt_allow
    #-------------------------------------------------------------------------------------------------------------------

    def _f_bearing_allow_comp_industrial(self, element_2d, joint, t, i) -> float:
        """
        Method which calculates the allowable bearing value following the "Industrial" method
        (Only valid for COMP elements)

        Args:
            element_2d (N2PElement): N2PElement working as a plate (head or nut side)
            joint (N2PJoint): N2PJoint working as the studied joint
            t (float): element thickness
            i (int): positioner of the element inside the composite element dictionary
        
        Returns:
            f_bea_allow (float): allowable bearing load (maximum force)
        """

        f_BEA_allow: float       

        # Laminate allowable bearing strength (stress)
        f_base=self._compshells[element_2d.Prop[0]].BearingAllowable

        shear_type = joint.JointAnalysisParameters.ShearType
        d_nom = joint.FastenerSystem.D_nom
        t_shim = joint.JointAnalysisParameters.TShim
        plate_pos = joint.PlateElementList.index(self._comp_elements[element_2d]["N2PPlate"].ElementList)
        edge = joint.JointAnalysisParameters.EdgeDistance[plate_pos]

        # KDF joint type factor
        if shear_type == "DLS":
            c_jt = 1.00
        else:
            c_jt = 0.75
        
        # KDF effect of edge distance
        if 1.8 <= (edge/d_nom) <= 3.0:
            c_ed = edge/(3*d_nom)
        elif (edge/d_nom) > 3.0:
            c_ed = 1.00
        elif (edge/d_nom) < 1.8:
            c_ed = edge/(3*d_nom)
            N2PLog.Warning.W901(element_2d.ID)
            self._booleans["edge_distance_problems"] = True

        # KDF effect of environment
        c_env = joint.JointAnalysisParameters.CenvComp

        # KDF effect of torque factor
        c_torq = 1.00

        # KDF effect of shim
        if shear_type == "DLS":
            c_shim = 1.00
        else:
            if t_shim <= 2.5:
                c_shim = 1.00 - min(0.16*(t_shim/t),0.08)*t_shim
            else:
                # An error is raised if t_shim is greater than 2.5 mm, this is not allowed in INDUSTRIAL method
                N2PLog.Error.E904(joint.ID)
                self._booleans["shim_problems"] = True
                t_shim = 2.5
                c_shim = 1.00 - min(0.16*(t_shim/t),0.08)*t_shim

        # KDF modulus variation factor
        c_mod = self._c_qi_mod[element_2d.Prop[0]]["C_mod"]

        # KDF effect of b-basis factor
        c_b_value = 1.00

        f_BEA_allow = f_base*c_jt*c_ed*c_env*c_torq*c_shim*c_mod*c_b_value

        # Input HDF5 file filling step
        self._input_h5_comp[i][7] = f_base
        self._input_h5_comp[i][8] = c_jt
        self._input_h5_comp[i][9] = c_ed
        self._input_h5_comp[i][10] = c_torq
        self._input_h5_comp[i][11] = c_shim
        self._input_h5_comp[i][12] = c_mod
        self._input_h5_comp[i][13] = f_BEA_allow

        return f_BEA_allow
    #-------------------------------------------------------------------------------------------------------------------

    def _f_netsection_allow_comp_industrial(self, element_2d, joint, i) -> tuple:
        """
        Method used to calculate net section allowables

        Args:
            element_2d (N2PElement): N2PElement working as a plate (head or nut side)
            joint (N2PJoint): N2PJoint working as the studied joint
            i (int): positioner of the element inside the composite element dictionary

        Returns:
            f_netsection_tension (float): allowable net section tension
            f_netsection_compress (float): allowable net section compression
        """

        f_netsection_tension: float
        f_netsection_compress: float

        # KDF effect of environment
        c_env = joint.JointAnalysisParameters.CenvComp

        # It is assumed that E1 = Ex (Equivalent Membrane modulus in x-dir)
        e_1 = self._get_fasteners.Model.PropertyDict[element_2d.Prop].EqMemProps[0]
        
        # It is assumed that E2 = Ey (Equivalent Membrane modulus in y-dir)
        e_2 = self._get_fasteners.Model.PropertyDict[element_2d.Prop].EqMemProps[1]

        oht=self._compshells[element_2d.Prop[0]].OHTAllowable
        if oht == None:
            msg = N2PLog.Critical.C907("OHTAllowable",element_2d.Prop)
            raise Exception(msg)
        
        ohc=self._compshells[element_2d.Prop[0]].OHCAllowable
        if ohc == None:
            msg = N2PLog.Critical.C907("OHCAllowable",element_2d.Prop)
            raise Exception(msg)

        fht=self._compshells[element_2d.Prop[0]].FHTAllowable
        if fht == None:
            msg = N2PLog.Critical.C907("FHTAllowable",element_2d.Prop)
            raise Exception(msg)
        
        fhc=self._compshells[element_2d.Prop[0]].FHCAllowable
        if fhc == None:
            msg = N2PLog.Critical.C907("FHCAllowable",element_2d.Prop)
            raise Exception(msg)

        f_netsection_tension = min(oht,fht)*min(e_1,e_2)*c_env
        f_netsection_compress = min(ohc,fhc)*min(e_1,e_2)*c_env

        # Input HDF5 file filling step
        self._input_h5_comp[i][14] = e_1
        self._input_h5_comp[i][15] = e_2
        self._input_h5_comp[i][16] = oht
        self._input_h5_comp[i][17] = ohc
        self._input_h5_comp[i][18] = fht
        self._input_h5_comp[i][19] = fhc
        self._input_h5_comp[i][20] = f_netsection_tension
        self._input_h5_comp[i][21] = f_netsection_compress

        return (f_netsection_tension, f_netsection_compress)
    #-------------------------------------------------------------------------------------------------------------------
    
    def _bypass_intersection_finder_tension_side(self, bearing_allow, fbp_netsection_tension, point_P, kdf, m) -> tuple:
        """
        Method used to detect the intersection point between the load line and the allowable line
        for bearing-bypass failure analysis in the tension region.

        Args:
            bearing_allow (float)
            fbp_netsection_tension (float)
            point_P (list)
            kdf (float)
            m (float)

        Returns:
            (rf, critical_failure_mod) (tuple): rf value and critical failure mod
        """

        x_p=point_P[0]
        y_p=point_P[1]

        if not x_p == 0:
            # Line o-p definition (y = m*x)
            m_op = y_p/x_p

            if m_op == 0:
                # CASE 1.1---------------------------------------------------------
                #------------------------------------------------------------------
                # Intersection point (W)
                x_w = fbp_netsection_tension
                y_w = 0.0

                # Failure Mode
                critical_failure_mod = "NETSECTION_ULTIMATE_TENSION"
                #------------------------------------------------------------------

            elif 0 < m_op <= m:
                # CASE 1.2---------------------------------------------------------
                #------------------------------------------------------------------
                # Point A location
                x_a = fbp_netsection_tension
                y_a = 0.0

                # Point B location
                x_b = bearing_allow/m
                y_b = bearing_allow

                # Line A-B definition (y = m*x + n)
                m_ab = (y_b-y_a)/(x_b-x_a)
                n_ab = y_b - m_ab*x_b

                # Intersection point (W)
                x_w = (-n_ab)/(m_ab-m_op)
                y_w = m_op*x_w

                # Failure Mode
                critical_failure_mod = "BYPASS_ULTIMATE_TENSION"
                #------------------------------------------------------------------

            elif m_op > m:
                # CASE 1.3---------------------------------------------------------
                #------------------------------------------------------------------
                # Line B-C definition (paralell to x-axis, y = Fbearing_Tension)
                # Intersection point (W)
                x_w = (bearing_allow)/(m_op)
                y_w = bearing_allow

                # Failure Mode
                critical_failure_mod = "BEARING_ULTIMATE_TENSION"
                #------------------------------------------------------------------

        else:
            # CASE 1.4---------------------------------------------------------
            #------------------------------------------------------------------
            # Line O-P definition -> y-axis (x = 0)
            # Intersection point (W)
            x_w = 0
            y_w = bearing_allow

            # Failure Mode
            critical_failure_mod = "BEARING_ULTIMATE_TENSION"
            #------------------------------------------------------------------

        ow=pow(pow(y_w,2)+pow(x_w,2),0.5)
        op=pow(pow(y_p,2)+pow(x_p,2),0.5)

        rf=int(kdf*(ow/op)*100)/100

        return (rf, critical_failure_mod)
    #-------------------------------------------------------------------------------------------------------------------

    def _bypass_intersection_finder_compression_side(self, bearing_allow, fbp_netsection_compress, point_P, kdf) -> tuple:
        """
        Method used to detect the intersection point between the load line and the allowable line
        for bearing-bypass failure analysis in the compression region.

        Arg:
            bearing_allow (float)
            fbp_netsection_compress (float)
            point_P (list)
            kdf (float)

        Returns:
            (rf, critical_failure_mod) (tuple): rf value and critical failure mod
        """

        x_p=point_P[0]
        y_p=point_P[1]

        # Line o-p definition (y = m*x)
        m_op = y_p/x_p

        if m_op < -3.0:
            # CASE 2.1---------------------------------------------------------
            #------------------------------------------------------------------
            # Line C-D definition (y = n)
            n_cd = abs(bearing_allow)

            # Intersection point (W)
            x_w = abs(bearing_allow)/m_op
            y_w = n_cd

            # Failure Mode
            critical_failure_mod = "BEARING_ULTIMATE_COMPRESSION"
            #------------------------------------------------------------------

        elif -1.0 >= m_op >= -3.0:
            # CASE 2.2---------------------------------------------------------
            #------------------------------------------------------------------
            # Point D location
            x_d = abs(bearing_allow)/(-3)
            y_d = abs(bearing_allow)

            # Point E location
            x_e = -abs(fbp_netsection_compress)
            y_e = abs(fbp_netsection_compress)

            # Line D-E definition (y = m*x + n)
            m_de = (y_e-y_d)/(x_e-x_d)
            n_de = y_e - m_de*x_e

            # Intersection point (W)
            x_w = (-n_de)/(m_de-m_op)
            y_w = m_op*x_w

            # Failure Mode
            critical_failure_mod = "BYPASS_ULTIMATE_COMPRESSION"
            #------------------------------------------------------------------

        elif 0 > m_op > -1:
            # CASE 2.3---------------------------------------------------------
            #------------------------------------------------------------------
            # Line E-F definition (parallel to y-axis, x = Fbypass_compress)
            # Intersection point (W)
            x_w = -abs(fbp_netsection_compress)
            y_w = m_op*x_w

            # Failure Mode
            critical_failure_mod = "BYPASS_ULTIMATE_COMPRESSION"
            #------------------------------------------------------------------
        
        elif m_op == 0:
            # CASE 2.4---------------------------------------------------------
            #------------------------------------------------------------------
            # Intersection point (W)
            x_w = -abs(fbp_netsection_compress)
            y_w = 0.0

            # Failure Mode
            critical_failure_mod = "NETSECTION_ULTIMATE_COMPRESSION"
            #------------------------------------------------------------------

        ow=pow(pow(y_w,2)+pow(x_w,2),0.5)
        op=pow(pow(y_p,2)+pow(x_p,2),0.5)

        rf=int(kdf*(ow/op)*100)/100

        return (rf, critical_failure_mod)
    #-------------------------------------------------------------------------------------------------------------------

    def _kdf_quasi_isotropic_laminate(self, compositeshell_id) -> None:
        """
        Method used to create quasi-isotropic laminates in order to determine a modulus KDF.
        """

        composite_shell_mats = [] # Different material(s) found on the laminate
        comp_shell_qi_data ={} # Dictionary to store information of the QI laminate
        quasi_mat_ids = [] # Mat ids of the QI laminate
        quasi_plies_t = [] # Plies thicknesses of the QI laminate
        quasi_stacking = [] # Plies stacking of the QI laminate
        stacking = [-45,45,0,90] # Generic stacking for each material

        # Composite Shell object and its thickness
        composite_shell_i = self._compshells[compositeshell_id]
        laminate_thickness=composite_shell_i.Thickness

        # MAT8 materials detection inside the CompositeShell
        for j in composite_shell_i.MatIDs:
            if j not in composite_shell_mats:
                composite_shell_mats.append(j)
                number_plies_mat_j=0
                thickness_mat_j=0
                for y in composite_shell_i.Laminate:
                    if y.mat_ID == j:
                        number_plies_mat_j += 1
                        thickness_mat_j += y.thickness
                
                comp_shell_qi_data[j]={"Number_Plies":number_plies_mat_j,"t_total":thickness_mat_j,
                                       "t_plie":(thickness_mat_j/number_plies_mat_j), "Weight":(thickness_mat_j/laminate_thickness)}
                for k in range(4):
                    quasi_mat_ids.append(j)
                    quasi_plies_t.append(thickness_mat_j/laminate_thickness)
                    quasi_stacking.append(stacking[k])
     
        # CompositeShell object
        quasitropi_laminate = CompositeShell()
        quasitropi_laminate.NumPlies = 4*len(comp_shell_qi_data)
        quasitropi_laminate.PartIDs = '0'
        quasitropi_laminate.MatIDs = quasi_mat_ids
        quasitropi_laminate.thicknesses = quasi_plies_t
        quasitropi_laminate.theta = quasi_stacking
        quasitropi_laminate.MaterialDict = self._get_fasteners.Model.MaterialDict
        quasitropi_laminate.simmetry = True

        # "Industrial" method to obtain KDF based on modulus variation
        Ex_qi, Ey_qi, nuxy_qi, Gxy_qi = quasitropi_laminate.EqMemProps()
        Ex, Ey, nuxy, Gxy = composite_shell_i.EqMemProps()
        modulus_ratio = (Ex*nuxy*Gxy)/(Ex_qi*Gxy_qi*nuxy_qi)

        if modulus_ratio < 0.60:
            c_mod = 0.441*(modulus_ratio-0.6)+1
        else:
            c_mod = 1.00

        self._c_qi_mod[compositeshell_id]={"C_mod": c_mod, "QI_Laminate": quasitropi_laminate}
    #-------------------------------------------------------------------------------------------------------------------

    def _input_data_echo(self) -> None:
        """
        Method used to create the input data echo for the elements analysed in this class.
        """

        # Create a list of tuples for the structured array containing information about each element
        data = []
        for x, key in enumerate(self._comp_elements):
            joint_x = self._comp_elements[key]["N2PJoint"]
            if not joint_x.FastenerSystem == None:

                # FastenerSystem object assignated to element x
                fastsyst=joint_x.FastenerSystem

                # JointAnalysisParameter object assiganted to element x
                fast_jap=joint_x.JointAnalysisParameters

                # Plate positioner inside the whole joint
                pos = joint_x.PlateElementList.index(self._comp_elements[key]["N2PPlate"].ElementList)

                entry = (
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        key.ID,
                        key.Prop[0],
                        self._comp_elements[key]["Side"],
                        self._comp_elements[key]["N2PJoint"].ID,
                        self._comp_elements[key]["N2PPlate"].ID,
                        self._comp_elements[key]["Thickness"],
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        fastsyst.Designation,
                        #-------------------------------------------------------------------------------------------------------------#
                        #-----------------------------#######---------[FASTENER SYSTEM INFORMATION]---------#######-------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        fastsyst.Fastener_pin_single_SH_allow,
                        fastsyst.Fastener_collar_single_SH_allow,
                        fastsyst.Fastener_pin_tensile_allow,
                        fastsyst.Fastener_collar_tensile_allow,
                        fastsyst.D_head,
                        fastsyst.D_tail,
                        fastsyst.D_nom,
                        fastsyst.Configuration,
                        fastsyst.FastenerType,
                        fastsyst.FastenerInstallation,
                        fastsyst.FastenerHead,
                        str(fastsyst.FloatingNut),
                        str(fastsyst.AluminumNut),
                        #-------------------------------------------------------------------------------------------------------------#
                        #-----------------------------#######---------[JOINT ANALYSIS PARAMETERS]---------#######---------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        fast_jap.ShearType,
                        None,                                       #fast_jap.CenvMet, NOT USED IN COMPOSITE
                        fast_jap.CenvComp,
                        fast_jap.UserKDFComp,
                        None,                                       #fast_jap.UserKDFMet, NOT USED IN COMPOSITE
                        None,                                       #fast_jap.UserKDFBoltShear, NOT USED IN COMPOSITE
                        None,                                       #fast_jap.UserKDFBoltTension, NOT USED IN COMPOSITE
                        fast_jap.M,
                        fast_jap.TShim,
                        fast_jap.TShimL,
                        fast_jap.CPrying,
                        None,                                       #fast_jap.PT_Alpha_Met, NOT USED IN COMPOSITE
                        None,                                       #fast_jap.PT_Gamma_Met, NOT USED IN COMPOSITE
                        fast_jap.EdgeDistance[pos],
                        fast_jap.EffectiveWidth[pos],
                        fast_jap.NetRatio[pos],
                        fast_jap.NetSectionArea[pos],
                        None,                                       #fast_jap.Coef_A_CombinedMet[pos], NOT USED IN COMPOSITE
                        None,                                       #fast_jap.Coef_B_CombinedMet[pos], NOT USED IN COMPOSITE
                        fast_jap.Coef_Alpha_CombinedComp[pos],
                        fast_jap.Coef_Beta_CombinedComp[pos],
                        None,                                       #fast_jap.Coef_SRF_NetSection_Met[pos], NOT USED IN COMPOSITE
                        #-------------------------------------------------------------------------------------------------------------#
                        #-----------------------------#######---------[PULL-THROUGH PARAMETERS]---------#######-----------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        self._input_h5_comp[x][2],
                        self._input_h5_comp[x][1],
                        self._input_h5_comp[x][3],
                        self._input_h5_comp[x][4],
                        self._input_h5_comp[x][5],
                        None,
                        self._input_h5_comp[x][6],
                        #-------------------------------------------------------------------------------------------------------------#
                        #------------------------------#######-----------[BEARING PARAMETERS]----------#######------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        self._input_h5_comp[x][7],
                        self._input_h5_comp[x][8],
                        self._input_h5_comp[x][9],
                        self._input_h5_comp[x][10],
                        self._input_h5_comp[x][11],
                        self._input_h5_comp[x][12],
                        None,                                       #F_bru_metd, NOT USED IN COMPOSITE
                        None,                                       #F_s_allow, NOT USED IN COMPOSITE
                        self._input_h5_comp[x][13],
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------#######----------[BEARING-BYPASS PARAMETERS]----------#######-----------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        self._input_h5_comp[x][17],
                        self._input_h5_comp[x][19],
                        self._input_h5_comp[x][16],
                        self._input_h5_comp[x][18],
                        self._input_h5_comp[x][14],
                        self._input_h5_comp[x][15],
                        self._input_h5_comp[x][20],
                        self._input_h5_comp[x][21],
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------#######------------[NET SECTION PARAMETERS]-----------#######-----------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        None,
                        None,
                        None,
                        None
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        )
                data.append(entry)
                
        self._calculation_input_echo = data
    #-------------------------------------------------------------------------------------------------------------------

    def calculate(self) -> None:
        """
        Method used to start RF calculations for composite elements.
        """

        # An zeros-like numpy array is created so as to store the RFs:
        long_1=len(self._comp_elements) # Number of studied composite elements
        long_2=3 # Number of failure modes studied

        # If no GetLoadFasteners is provided, then LoadCases list is set to 1
        if self._get_load_fasteners == None:
            long_3 = 1
        else:
            long_3=len(self._get_load_fasteners.LoadCases) # Number of loadcases

        # Numpy array to store the composite elements RF values
        self._rf_results=np.full((long_1,long_2,long_3), np.nan)

        # A numpy array is created in order to store the composite input echo data
        self._input_h5_comp=np.full((long_1,22), np.nan)

        # Modulus Variation KDFs (Quasi-Isotropic laminate calculation) are calculated for every analysed laminate
        for key in self._compshells:
            self._kdf_quasi_isotropic_laminate(key)

        t1 = time()

        for i,key in enumerate(self._comp_elements):

            comp_element_dict = self._comp_elements[key]

            self._input_h5_comp[i][0] = key.ID

            # Element side, joint, plate, thickness
            side = comp_element_dict["Side"]
            joint = comp_element_dict["N2PJoint"]
            plate = comp_element_dict["N2PPlate"]
            t = comp_element_dict["Thickness"]

            # RF values calculation for each failure mode considered

            # If the associated joint has no FastenerSystem, this elem id RF cannot be calculated
            if joint.FastenerSystem is not None:

                # Pull-through RF calculation
                if not (side=="Middle"):
                    self._rf_pullthrough_comp_industrial(i,key, side, joint, plate, t)

                # Bearing RF calculation and f_BEA_allowable obtention for Bearing-ByPass method
                BEA_rf_and_allowable = self._rf_bearing_comp_industrial(i,key, joint, plate, t)

                # Bearing-Bypass RF calculation
                self._rf_bearingbypass_comp_industrial(i,key, joint, plate, t, BEA_rf_and_allowable)

        # ---- For time checking ----
        t2 = time() 
        dt = t2 - t1
        if dt < 60:
            #N2PLog.set_file_level("DEBUG") 
            N2PLog.Debug.D901(str(dt) + " seconds.")
        else: 
            #N2PLog.set_file_level("DEBUG")
            minutes = int(dt // 60)
            seconds = dt - minutes*60
            N2PLog.Debug.D901(str(minutes) + " min, " + str(seconds) + " sec.")
        # ---------------------------

        # Composite input data echo array is created
        self._input_data_echo()
    #-------------------------------------------------------------------------------------------------------------------
        