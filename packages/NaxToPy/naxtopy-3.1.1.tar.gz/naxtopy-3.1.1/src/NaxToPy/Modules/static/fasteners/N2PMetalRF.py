from NaxToPy.Modules.static.fasteners.N2PGetLoadFasteners import N2PGetLoadFasteners
from NaxToPy.Modules.static.fasteners.N2PGetFasteners import N2PGetFasteners
from NaxToPy.Core.Errors.N2PLog import N2PLog
import numpy as np
import sys 
from time import time
#
class N2PMetalRF:
    """
    Class that manages the RF calculation of PSHELL 2D elements based on several failures modes.
    """
    __slots__= ("_metal_elements",
                "_get_load_fasteners",
                "_get_fasteners",
                "_rf_results",
                "_elms_id_and_rfs",
                "_input_h5_metal",
                "_echo_dataentry",
                "_shells",
                "_rf_export_location",
                "_calculation_input_echo",
                "_booleans"
                )
    
    # N2PMetRF constructor --------------------------------------------------------------------------------------
    def __init__(self):
        """
        The constructor creates an empty N2PMetRF instance. Its attributes must be addes as properties.
        """
        self._metal_elements: dict=None
        self._get_load_fasteners: N2PGetLoadFasteners=None
        self._get_fasteners: N2PGetFasteners=None
        self._echo_dataentry: np.array=None
        self._shells: dict=None
        self._rf_export_location: str=None
        self._calculation_input_echo: list=[]
        self._booleans: dict={"bru_allow_problems":False, "a_net_gross_problems":False}

    # Getters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @property
    def MetalElements(self) -> dict:
        """
        Dictonary which contains all the metallic elements to be studied
        """
        return self._metal_elements
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
    def RFExportLocaton(self) -> str:
        """
        Path to the directory where the RFs are to be printed
        """
        return self._rf_export_location

    @property
    def Shells(self) -> dict:
        """
        Dictionary which contains the Shells objects
        """
        return self._shells
    
    @property
    def CalculationInputEcho(self) -> np.array:
        """
        Numpy array which contains all the input data for Metallic elements calculation
        """
        return self._calculation_input_echo
    
    @property
    def RFResults(self) -> np.array:
        """
        Numpy array which contains all the RF results
        """
        return self._rf_results
    # Setters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @MetalElements.setter
    def MetalElements(self, value: dict) -> None:

        self._metal_elements = value
    #-------------------------------------------------------------------------------------------------------------------

    @GetLoadFasteners.setter
    def GetLoadFasteners(self, value: N2PGetLoadFasteners) -> None:

        self._get_load_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @GetFasteners.setter
    def GetFasteners(self, value: N2PGetFasteners) -> None:

        self._get_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @Shells.setter
    def Shells(self, value: dict) -> None:

        self._shells = value
    #-------------------------------------------------------------------------------------------------------------------

    @RFExportLocaton.setter
    def RFExportLocation(self, value: str) -> None:

        self._rf_export_location = value
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    def _rf_pullthrough_metal_industrial(self, i, element, side, joint, plate, t) -> None:
        """
        Method used to obtain the Pull Through RF for each METAL element.

        Arg:
            side (str): Side of the element: "Head", "Middle" or "Tail"
            joint (N2PJoint): joint object related to the element considered
            plate (N2PPlate): plate object related to the element considered
            t (float): element thickness
        """

        # Pull-Through allowables and kdfs
        user_kdf = joint.JointAnalysisParameters.UserKDFMet
        c_prying = joint.JointAnalysisParameters.CPrying
        f_pt_allow = self._f_pullthrough_allow_metal_industrial(joint,side,t,i)

        # Only RFs are calculated if a N2PGetLoadFasteners is provided
        if not self._get_load_fasteners == None:
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                # Pull through force for LC j
                p = plate.BearingForce[loadcase_id][2]

                # Calculate RF (Reserve Factor) based on several conditions:

                # Connector under TENSION:
                if p>0:
                    rf_pull_through = int(((f_pt_allow*user_kdf)/(p*c_prying))*100)/100
                    rf_pull_through = format(rf_pull_through,'.2f')
                    # Array filling step
                    self._rf_results[i][0][j]=rf_pull_through

                # Connector under COMPRESSION:  
                elif p<=0:
                    rf_pull_through = format(9999.00,'.2f')
                    # Array filling step
                    self._rf_results[i][0][j]=rf_pull_through
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_bearing_metal_industrial(self, i, element, side, joint, plate, t) -> None:
        """
        Method used to obtain the Bearing RF for each METAL element.


        Arg:
            element (N2PElement): composite element to be studied
            side (str): Side of the element: "Head", "Middle" or "Tail"
            joint (N2PJoint): joint object related to the element considered
            plate (N2PPlate): plate object related to the element considered
            t (float): element thickness
        """

        # Bearing allowables and kdfs
        f_bea_allow = self._f_bearing_allow_metal_industrial(element,joint,i, side, t)
        user_kdf = joint.JointAnalysisParameters.UserKDFMet

        # Only RFs are calculated if a N2PGetLoadFasteners is provided
        if not self._get_load_fasteners == None:
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                # Bearing force for LC j
                f_bea=pow((pow(plate.BearingForce[loadcase_id][0],2)+pow(plate.BearingForce[loadcase_id][1],2)),0.5)

                # Calculate RF (Reserve Factor) based on several conditions:

                # Bearing force is not zero:
                if f_bea>0:
                    rf_bearing = int(((f_bea_allow*user_kdf)/f_bea)*100)/100
                    rf_bearing = format(rf_bearing,'.2f')
                    # Array filling step
                    self._rf_results[i][1][j]=rf_bearing

                # Bearing force is zero:  
                elif f_bea==0:
                    rf_bearing = format(9999.00,'.2f')
                    # Array filling step
                    self._rf_results[i][1][j]=rf_bearing
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_netsection_metal_industrial(self, i, element, joint, plate, t) -> None:
        """
        Method used to obtain the Net Secion RF for each METAL element.

        Arg:
            element (N2PElement): composite element to be studied
            joint (N2PJoint): joint object related to the element considered
            plate (N2PPlate): plate object related to the element considered
            t (float): element thickness 
        """

        user_kdf = joint.JointAnalysisParameters.UserKDFMet
        f_NS_allow = self._f_netsection_allow_metal_industrial(element, joint, i)

        # Only RFs are calculated if a N2PGetLoadFasteners is provided
        if not self._get_load_fasteners == None:
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                # Total Fluxes
                # Nx, Ny, Nxy
                nx=plate.NxTotal[loadcase_id]
                ny=plate.NyTotal[loadcase_id]
                nxy=plate.NxyTotal[loadcase_id]

                # Max and min principal
                n_maxppal=(nx+ny)*0.5+pow((pow((nx-ny)*0.5,2)+pow(nxy,2)),0.5)
                n_minppal=(nx+ny)*0.5-pow((pow((nx-ny)*0.5,2)+pow(nxy,2)),0.5)
                n_ppal = max(abs(n_maxppal),abs(n_minppal))

                # Calculate RF (Reserve Factor) based on several conditions:

                # Nppal is not zero:
                if n_ppal>0:
                    rf_ns = int(((f_NS_allow*user_kdf)/(n_ppal/t))*100)/100
                    rf_ns = format(rf_ns,'.2f')
                    self._rf_results[i][2][j]=rf_ns

                # Nppal is zero:  
                elif n_ppal==0:
                    rf_ns = format(9999.00,'.2f')
                    self._rf_results[i][2][j]=rf_ns
    #-------------------------------------------------------------------------------------------------------------------

    def _f_pullthrough_allow_metal_industrial(self, joint, side, t, i) -> float:
        """
        Method which calculates the allowable pull through value following the "Industrial" method
        (Only valid for PSHELL elements)

        Arg:
            side (str): Side of the element: "Head", "Middle" or "Tail"
            joint (N2PJoint): joint object related to the element considered
            t (float): element thickness
        
        Returns:
            f_pt_allow (float): allowable pull through load [force]
        """

        f_pt_allow:float

        # FastenerSystem object
        fastsys = joint.FastenerSystem

        # JointAnalysisParameters object
        jap = joint.JointAnalysisParameters

        # Fastener diameter
        d = fastsys.D_nom
        if d == None:
            msg = N2PLog.Critical.C903("D_nom", joint.ID)
            raise Exception(msg)

        # Empirical coefficients alpha & gamma
        pt_alpha_met = jap.PT_Alpha_Met
        pt_gamma_met = jap.PT_Gamma_Met

        # Bolt tensile allowable value and head/nut diameter
        if side =="Head":

            f_T=fastsys.Fastener_pin_tensile_allow

            if f_T==None:
                msg = N2PLog.Critical.C903("Fastener_pin_tensile_allow",joint.ID)
                raise Exception(msg)

        elif side == "Tail":
            f_T=fastsys.Fastener_collar_tensile_allow
            if f_T==None:
                msg = N2PLog.Critical.C903("Fastener_collar_tensile_allow",joint.ID)
                raise Exception(msg)
            
        # Allowable KDFs
        c_srf_pt = 0.60
        c_env_met = jap.CenvMet
        c_b_value = 1.00
  
        # Allowable tensile load=min[pull-through load, bolt tension load]
        f_pt_allow=pow(d,2)*min((pt_alpha_met*(t/d)+pt_gamma_met),(f_T/pow(d,2)))*c_srf_pt*c_env_met*c_b_value

        # Input HDF5 file filling step
        self._input_h5_metal[i][1] = c_srf_pt
        self._input_h5_metal[i][2] = c_b_value
        self._input_h5_metal[i][3] = f_T
        self._input_h5_metal[i][4] = f_pt_allow

        return f_pt_allow
    #-------------------------------------------------------------------------------------------------------------------

    def _f_bearing_allow_metal_industrial(self, element_2d, joint, i, side, t) -> float:
        """
        Method which calculates the allowable bearing value following the "Industrial" method
        (Only valid for PSHELL elements)

        Args:
            element_2d (N2PElement): N2PElement working as a plate
            joint (N2PJoint): N2PJoint working as the studied joint
            i (int): positioner of the element inside the metallic element dictionary
            side (str): Side of the element: "Head", "Middle" or "Tail"
            t (float): element thickness
        
        Returns:
            f_bea_allow (float): allowable bearing load [force]
        """

        f_bea_allow:float

        # Fastener diameter
        d = joint.FastenerSystem.D_nom
        if d == None:
            msg = N2PLog.Critical.C903("D_nom", joint.ID)
            raise Exception(msg)
        
        # Edge distance / Diameter ratio
        plate_pos = joint.PlateElementList.index(self._metal_elements[element_2d]["N2PPlate"].ElementList)
        e_d = (joint.JointAnalysisParameters.EdgeDistance[plate_pos]/d)

        #f_bru obtention
        f_bru_2d = self._shells[element_2d.Prop[0]].Fbru_e2d
        f_bru_1p5d = self._shells[element_2d.Prop[0]].Fbru_e1p5d

        if f_bru_2d == None:
            msg = N2PLog.Critical.C905("Fbru_e2d", element_2d.Prop[0])
            raise Exception(msg)
        
        if f_bru_1p5d == None:
            msg = N2PLog.Critical.C905("Fbru_e1p5d", element_2d.Prop[0])
            raise Exception(msg)

        if e_d >= 2.0:
            f_bru = f_bru_2d
        
        elif 1.5 <= e_d < 2.0:
            f_bru = f_bru_1p5d + ((f_bru_2d-f_bru_1p5d)*(e_d-1.5))/(2.0-1.5)

        elif e_d < 1.5:
            f_bru = min(f_bru_2d,f_bru_1p5d)
            N2PLog.Warning.W903(element_2d.ID, e_d, f_bru)
            self._booleans["bru_allow_problems"] = True

        # Bolt shear allowable value
        if side =="Head" or "Middle":
            f_s_allow=joint.FastenerSystem.Fastener_pin_single_SH_allow
            if f_s_allow==None:
                msg = N2PLog.Critical.C903("Fastener_pin_single_SH_allow",joint.ID)
                raise Exception(msg)

        elif side == "Tail":
            f_s_allow=joint.FastenerSystem.Fastener_collar_single_SH_allow
            if f_s_allow==None:
                msg = N2PLog.Critical.C903("Fastener_collar_single_SH_allow",joint.ID)
                raise Exception(msg)
        
        # Bearing allowables and kdfs
        c_env_met = joint.JointAnalysisParameters.CenvMet
        c_shim = self._shimming_kdf_metal_industrial(element_2d,joint,i)
        c_b_value = 1.00

        # Allowable tensile load=min[pull-through load, bolt tension load]
        f_bea_allow=min(f_bru*t*d,f_s_allow)*c_env_met*c_shim*c_b_value

        # Input file filling step
        self._input_h5_metal[i][5] = c_shim
        self._input_h5_metal[i][6] = f_bru
        self._input_h5_metal[i][7] = f_s_allow
        self._input_h5_metal[i][8] = f_bea_allow

        return f_bea_allow
    #-------------------------------------------------------------------------------------------------------------------

    def _f_netsection_allow_metal_industrial(self, element_2d, joint, i) -> float:
        """
        Method which calculates the allowable net section value following the "Industrial" method
        (Only valid for PSHELL elements)

        Args:
            element_2d (N2PElement): N2PElement working as a plate
            joint (N2PJoint): N2PJoint working as the studied joint
            i (int): positioner of the element inside the metallic element dictionary
        
        Returns:
            f_NS_allow (float): allowable net section [stress]
        """

        f_NS_allow:float

        # Plate position inside joint
        plate_pos = joint.PlateElementList.index(self._metal_elements[element_2d]["N2PPlate"].ElementList)

        # Net section parameters
        a_net_gross = 1-joint.JointAnalysisParameters.NetRatio[plate_pos]
        c_srf_netsection = joint.JointAnalysisParameters.Coef_SRF_NetSection_Met[plate_pos]
        f_tu = self._shells[element_2d.Prop[0]].Ftu
        if f_tu == None:
            msg = N2PLog.Critical.C905("ftu", element_2d.Prop[0])
            raise Exception(msg)
        
        c_env_met = joint.JointAnalysisParameters.CenvMet

        f_NS_allow = a_net_gross*c_srf_netsection*f_tu*c_env_met

        # If a_net_gross is negative due to an user input error, an error is raised and the net-section allowable
        # is set to 0 in order to obtain RF_NS = 0.00 for all load cases
        if f_NS_allow <= 0:
            f_NS_allow = 0
            N2PLog.Error.E907(joint.ID, element_2d.ID)
            self._booleans["a_net_gross_problems"] = True

        # Input Echo file filling:
        self._input_h5_metal[i][9] = a_net_gross
        self._input_h5_metal[i][10] = c_srf_netsection
        self._input_h5_metal[i][11] = f_tu
        self._input_h5_metal[i][12] = f_NS_allow

        return f_NS_allow
    #-------------------------------------------------------------------------------------------------------------------

    def _shimming_kdf_metal_industrial(self, element_2d,joint, i) -> float:
        """
        Method which calculates the shimming KDF C_shim for bearing RF value following the "Industrial" method
        (Only valid for PSHELL elements)

        Args:
            element_2d (N2PElement): N2PElement working as a plate
            joint (N2PJoint): N2PJoint working as the studied joint
            i (int): positioner of the element inside the metallic element dictionary
        
        Returns:
            c_shim (float): shimming effect KDF
        """

        c_shim: float

        # Plate thickness
        t = self._metal_elements[element_2d]["Thickness"]

        # Solid shim thickness
        t_shim = joint.JointAnalysisParameters.TShim
        if t_shim==None:
            msg = N2PLog.Critical.C903("TShim",joint.ID)
            raise Exception(msg)
        
        # Liquid shim thickness
        t_shim_l = joint.JointAnalysisParameters.TShimL
        if t_shim_l==None:
            msg = N2PLog.Critical.C903("TShimL",joint.ID)
            raise Exception(msg)
        
        t_shim_eq = t_shim + t_shim_l

        # KDF calculation
        c_shim = min(1,(1.06-min(0.7*(t_shim_eq/t),0.165)*t_shim_eq))

        return c_shim
    #-------------------------------------------------------------------------------------------------------------------

    def _input_data_echo(self) -> None:
        """
        Method used to create the input data echo for the elements analysed in this class.
        """

        # Create a list of tuples for the structured array containing information about each element
        data = []
        for x, key in enumerate(self._metal_elements):
            joint_x = self._metal_elements[key]["N2PJoint"]
            if not joint_x.FastenerSystem == None:

                # FastenerSystem object assignated to element x
                fastsyst=joint_x.FastenerSystem

                # JointAnalysisParameter object assiganted to element x
                fast_jap=joint_x.JointAnalysisParameters

                # Plate positioner inside the whole joint
                pos = joint_x.PlateElementList.index(self._metal_elements[key]["N2PPlate"].ElementList)

                entry = (
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        key.ID,
                        key.Prop[0],
                        self._metal_elements[key]["Side"],
                        self._metal_elements[key]["N2PJoint"].ID,
                        self._metal_elements[key]["N2PPlate"].ID,
                        self._metal_elements[key]["Thickness"],
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
                        fast_jap.CenvMet,
                        None,                                       #fast_jap.CenvComp, NOT USED IN METALLIC
                        None,                                       #fast_jap.UserKDFComp, NOT USED IN METALLIC
                        fast_jap.UserKDFMet,
                        None,                                       #fast_jap.UserKDFBoltShear, NOT USED IN METALLIC
                        None,                                       #fast_jap.UserKDFBoltTension, NOT USED IN METALLIC
                        fast_jap.M,
                        fast_jap.TShim,
                        fast_jap.TShimL,
                        fast_jap.CPrying,
                        fast_jap.PT_Alpha_Met,
                        fast_jap.PT_Gamma_Met,
                        fast_jap.EdgeDistance[pos],
                        fast_jap.EffectiveWidth[pos],
                        fast_jap.NetRatio[pos],
                        fast_jap.NetSectionArea[pos],
                        fast_jap.Coef_A_CombinedMet[pos],
                        fast_jap.Coef_B_CombinedMet[pos],
                        None,                                       #fast_jap.Coef_Alpha_CombinedComp[pos], NOT USED IN METALLIC
                        None,                                       #fast_jap.Coef_Beta_CombinedComp[pos], NOT USED IN METALLIC
                        fast_jap.Coef_SRF_NetSection_Met[pos],
                        #-------------------------------------------------------------------------------------------------------------#
                        #-----------------------------#######---------[PULL-THROUGH PARAMETERS]---------#######-----------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        self._input_h5_metal[x][3],
                        None,
                        self._input_h5_metal[x][2],
                        None,
                        None,
                        self._input_h5_metal[x][1],
                        self._input_h5_metal[x][4],
                        #-------------------------------------------------------------------------------------------------------------#
                        #------------------------------#######-----------[BEARING PARAMETERS]----------#######------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        None,
                        None,
                        None,
                        None,
                        self._input_h5_metal[x][5],
                        None,
                        self._input_h5_metal[x][6],
                        self._input_h5_metal[x][7],
                        self._input_h5_metal[x][8],
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------#######----------[BEARING-BYPASS PARAMETERS]----------#######-----------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------#######------------[NET SECTION PARAMETERS]-----------#######-----------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        self._input_h5_metal[x][9],
                        self._input_h5_metal[x][10],
                        self._input_h5_metal[x][11],
                        self._input_h5_metal[x][12]
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        )
                data.append(entry)
                
        self._calculation_input_echo = data
    #-------------------------------------------------------------------------------------------------------------------

    def calculate(self) -> None:
        """
        Method used to start RF calculations for metallic elements.
        """
        
        # An zeros-like numpy array is created so as to store the RFs:
        long_1=len(self._metal_elements) # Number of studied metallic elements
        long_2=3 # Number of failure modes studied

        # If no GetLoadFasteners is provided, then LoadCases list is set to 1
        if self._get_load_fasteners == None:
            long_3 = 1
        else:
            long_3=len(self._get_load_fasteners.LoadCases) # Number of loadcases

        elems_ids=np.zeros((long_1,1,long_3), dtype=np.int64)
        self._rf_results=np.full((long_1,long_2,long_3), np.nan)

        # A numpy array is created in order to create the HDF5 input file
        self._input_h5_metal=np.full((long_1,13), np.nan)

        t1 = time()

        for i,key in enumerate(self._metal_elements):

            metal_element_dict = self._metal_elements[key]

            # Element id is written inside the input h5 file
            self._input_h5_metal[i][0] = key.ID

            # Element side, joint, plate, thickness
            side = metal_element_dict["Side"]
            joint = metal_element_dict["N2PJoint"]
            plate = metal_element_dict["N2PPlate"]
            t = metal_element_dict["Thickness"]

            # RF values calculation for each failure mode considered

            # If the associated joint has no FastenerSystem, this elem id RF cannot be calculated
            if joint.FastenerSystem is not None:

                # Pull-through RF calculation
                if not (side == "Middle"):
                    self._rf_pullthrough_metal_industrial(i,key, side, joint, plate, t)

                # Bearing RF calculation
                self._rf_bearing_metal_industrial(i,key, side, joint, plate, t)

                # Net-Section RF calculation
                self._rf_netsection_metal_industrial(i,key, joint, plate, t)

            for j in range(long_3):
                elems_ids[i][0][j] = key.ID

        # ---- For time checking ----
        t2 = time() 
        dt = t2 - t1
        if dt < 60: 
            #N2PLog.set_file_level("DEBUG")
            N2PLog.Debug.D902(str(dt) + " seconds.")
        else: 
            #N2PLog.set_file_level("DEBUG")
            minutes = int(dt // 60)
            seconds = dt - minutes*60
            N2PLog.Debug.D902(str(minutes) + " min, " + str(seconds) + " sec.")
        sys.stdout.write("\n")
        # ---------------------------

        self._input_data_echo()
    #-------------------------------------------------------------------------------------------------------------------
   