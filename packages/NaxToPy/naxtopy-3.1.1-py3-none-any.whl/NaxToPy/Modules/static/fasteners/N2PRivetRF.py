from NaxToPy.Modules.static.fasteners.N2PGetLoadFasteners import N2PGetLoadFasteners
from NaxToPy.Modules.static.fasteners.N2PGetFasteners import N2PGetFasteners
from NaxToPy.Core.Errors.N2PLog import N2PLog
import numpy as np
import sys 
from time import time
import math
#
class N2PRivetRF:
    """
    Class that manages the RF calculation of 1D elements (called "rivets") based on several failure modes
    """
    __slots__= ("_rivet_elements",
                "_get_load_fasteners",
                "_get_fasteners",
                "_rf_results",
                "_elms_id_and_rfs",
                "_input_h5_rivet",
                "_echo_dataentry",
                "_calculation_input_echo",
                "_comp_elements_list",
                "_comp_rf_results"
                )
    
        # N2PRivetRF constructor --------------------------------------------------------------------------------------
    def __init__(self):
        """
        The constructor creates an empty N2PRivetRF instance. Its attributes must be addes as properties.
        """
        self._rivet_elements: dict=None
        self._get_load_fasteners: N2PGetLoadFasteners=None
        self._get_fasteners: N2PGetFasteners=None
        self._echo_dataentry: np.array=None
        self._calculation_input_echo: list=[]
        self._rf_results: np.array=None
        self._comp_elements_list: list=[]
        self._comp_rf_results: np.array=None

    # Getters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @property
    def RivetElements(self) -> dict:
        """
        Dictonary which contains all the rivet elements to be studied
        """
        return self._rivet_elements
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
    def CalculationInputEcho(self) -> np.array:
        """
        Numpy array which contains all the input data for Metallic elements calculation
        """
        return self._calculation_input_echo
    #-------------------------------------------------------------------------------------------------------------------
  
    @property
    def RFResults(self) -> np.array:
        """
        Numpy array which contains all the RF results
        """
        return self._rf_results
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def CompElementsList(self) -> list:
        """
        List which contains all the composite elements to be studied
        """
        return self._comp_elements_list
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def CompRFResults(self) -> np.array:
        """
        Numpy array which contains Composite RF results
        """
        return self._comp_rf_results
    #-------------------------------------------------------------------------------------------------------------------
    # Setters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @RivetElements.setter
    def RivetElements(self, value: dict) -> None:

        self._rivet_elements = value
    #-------------------------------------------------------------------------------------------------------------------

    @GetLoadFasteners.setter
    def GetLoadFasteners(self, value: N2PGetLoadFasteners) -> None:

        self._get_load_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @GetFasteners.setter
    def GetFasteners(self, value: N2PGetFasteners) -> None:

        self._get_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @CompElementsList.setter
    def CompElementsList(self, value: list) -> None:

        self._comp_elements_list = value
    #-------------------------------------------------------------------------------------------------------------------

    @CompRFResults.setter
    def CompRFResults(self, value: np.array) -> None:

        self._comp_rf_results = value
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    def _rf_bolttension_rivet_industrial(self, i, element, joint) -> None:
        """
        Method used to obtain the Bolt Tension RF for each 1D element.

        Args:
            element (N2PElement): N2PElement from the 1D element dictionary
            i (int): positioner of the element inside the 1D element dictionary 
            joint (N2PJoint): joint object related to the element considered
        """

        user_kdf = joint.JointAnalysisParameters.UserKDFBoltTension
        c_prying = joint.JointAnalysisParameters.CPrying

        pin_tensile_allow = joint.FastenerSystem.Fastener_pin_tensile_allow
        collar_tensile_allow = joint.FastenerSystem.Fastener_collar_tensile_allow
        
        if pin_tensile_allow == None:
            msg = N2PLog.Critical.C903("Fastener_pin_tensile_allow", joint.ID)
            raise Exception(msg)
        
        if collar_tensile_allow == None:
            msg = N2PLog.Critical.C903("Fastener_collar_tensile_allow", joint.ID)
            raise Exception(msg)

        f_T_allow = min (pin_tensile_allow, collar_tensile_allow)
    
        # Only RFs are calculated if N2PGetLoadFasteners is defined
        if (not self._get_load_fasteners == None):
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                p = joint.Bolt.AxialForce[loadcase_id][element.ID]

                # Bolt tension is calculated only if there is TENSION
                if p > 0:
                    rf_bolt_tension = int(((f_T_allow*user_kdf)/(p*c_prying))*100)/100
                    rf_bolt_tension = format(rf_bolt_tension, '.2f')
                else:
                    rf_bolt_tension = format(9999.00, '.2f')

                # Array filling step
                self._rf_results[i][0][j]=rf_bolt_tension
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_boltshear_boltcombined_rivet_industrial(self, i, element, joint) -> None:
        """
        Method used to obtain the Bolt Shear RF for each 1D element.

        Args:
            element (N2PElement): N2PElement from the 1D element dictionary
            i (int): positioner of the element inside the 1D element dictionary 
            joint (N2PJoint): joint object related to the element considered
        """
        # FastenerSystem object
        fastsys = joint.FastenerSystem

        # JointAnalysisParameter object
        jap = joint.JointAnalysisParameters

        # Bolt Tension allowables and kdfs
        user_kdf = jap.UserKDFBoltShear

        # Fastener pin and collar shear allowables from N2PFastenerSystem
        f_sh_allow_pin = fastsys.Fastener_pin_single_SH_allow
        f_sh_allow_collar = fastsys.Fastener_collar_single_SH_allow

        if f_sh_allow_pin == None:
            msg = N2PLog.Critical.C903("Fastener_pin_single_SH_allow", joint.ID)
            raise Exception(msg)
        
        if f_sh_allow_collar == None:
            msg = N2PLog.Critical.C903("Fastener_collar_single_SH_allow", joint.ID)
            raise Exception(msg)

        rivet_pos = joint.BoltElementIDList.index(element.ID)
        pos_plate_a = rivet_pos
        pos_plate_b = rivet_pos +1

        coef_a_combined_metal = jap.Coef_A_CombinedMet
        coef_b_combined_metal = jap.Coef_B_CombinedMet

        coef_alpha_combined_comp = jap.Coef_Alpha_CombinedComp
        coef_beta_combined_comp = jap.Coef_Beta_CombinedComp

        plate_a = joint.PlateList[pos_plate_a]
        plate_a_coef_a_combined_met = coef_a_combined_metal[pos_plate_a]
        plate_a_coef_b_combined_met = coef_b_combined_metal[pos_plate_a]
        plate_a_coef_alpha_combined_comp = coef_alpha_combined_comp[pos_plate_a]
        plate_a_coef_beta_combined_comp = coef_beta_combined_comp[pos_plate_a]

        if not (plate_a_coef_a_combined_met == None):
            plate_a_type = "METALLIC"
        else:
            plate_a_type = "COMPOSITE"

        plate_b = joint.PlateList[pos_plate_b]
        plate_b_coef_a_combined_met = coef_a_combined_metal[pos_plate_b]
        plate_b_coef_b_combined_met = coef_b_combined_metal[pos_plate_b]
        plate_b_coef_alpha_combined_comp = coef_alpha_combined_comp[pos_plate_b]
        plate_b_coef_beta_combined_comp = coef_beta_combined_comp[pos_plate_b]

        if not (plate_b_coef_a_combined_met == None):
            plate_b_type = "METALLIC"
        else:
            plate_b_type = "COMPOSITE"

        # Allowables assignation:
        #---------------------------------------------------------------------------
        # Plate A is always at head or middle position ->> Pin Allowable
        # Plate B can be at middle (Pin Allowable) or Tail position (Collar Allowable)
        f_sh_allow_a = f_sh_allow_pin

        if (rivet_pos + 2) == len(joint.PlateList):
            f_sh_allow_b = f_sh_allow_collar
        else:
            f_sh_allow_b = f_sh_allow_pin
        
        #---------------------------------------------------------------------------

        # Only RFs are calculated if a N2PGetLoadFasteners
        if (not self._get_load_fasteners == None):
            # RF Calculation for each LC (j -> loadcase considered)
            for j in range(0,len(self._get_load_fasteners.LoadCases)):
                # LC j id
                loadcase_id=self._get_load_fasteners.LoadCases[j].ID

                plate_a_forces = plate_a.BearingForce[loadcase_id]
                plate_b_forces = plate_b.BearingForce[loadcase_id]

                f_sh_a = pow((pow(plate_a_forces[0],2)+pow(plate_a_forces[1],2)),0.5)
                f_sh_b = pow((pow(plate_b_forces[0],2)+pow(plate_b_forces[1],2)),0.5)

                # BOLT SHEAR CALCULATION
                #---------------------------------------------------------------------------
                # Plate A:
                if f_sh_a > 0:
                    rf_bolt_shear_a = int(((f_sh_allow_a*user_kdf)/(f_sh_a))*100)/100
                else:
                    rf_bolt_shear_a = 9999.00

                # Plate B:
                if f_sh_b > 0:
                    rf_bolt_shear_b = int(((f_sh_allow_b*user_kdf)/(f_sh_b))*100)/100
                else:
                    rf_bolt_shear_b = 9999.00
                #---------------------------------------------------------------------------

                # BOLT COMBINED CALCULATION
                #------------------------------------------------------------------------------------------------------------
                #------------------------------------------------------------------------------------------------------------
                # Plate A:
                if plate_a_type == "METALLIC":
                    rf_combined_plate_a = self._rf_boltcombined_met_plate_industrial(rf_bolt_shear_a,
                                                                                    plate_a_coef_a_combined_met,
                                                                                    plate_a_coef_b_combined_met,
                                                                                    i,j)
                    
                elif plate_a_type == "COMPOSITE":
                    rf_combined_plate_a = self._rf_boltcombined_comp_plate_industrial(rf_bolt_shear_a,
                                                                                        plate_a_coef_alpha_combined_comp,
                                                                                        plate_a_coef_beta_combined_comp,
                                                                                        i,j,plate_a)
                #------------------------------------------------------------------------------------------------------------
                # Plate B:
                if plate_b_type == "METALLIC":
                    rf_combined_plate_b = self._rf_boltcombined_met_plate_industrial(rf_bolt_shear_b,
                                                                                    plate_b_coef_a_combined_met,
                                                                                    plate_b_coef_b_combined_met,
                                                                                    i,j)

                elif plate_b_type == "COMPOSITE":
                    rf_combined_plate_b = self._rf_boltcombined_comp_plate_industrial(rf_bolt_shear_b,
                                                                                        plate_b_coef_alpha_combined_comp,
                                                                                        plate_b_coef_beta_combined_comp,
                                                                                        i,j,plate_b)
                #------------------------------------------------------------------------------------------------------------
                #------------------------------------------------------------------------------------------------------------

                rf_bolt_shear = min(rf_bolt_shear_a, rf_bolt_shear_b)

                rf_bolt_combined = min(rf_combined_plate_a[0], rf_combined_plate_b[0])
                rf_bolt_combined = format(rf_bolt_combined, '.2f')

                # Array filling step
                self._rf_results[i][1][j]=rf_bolt_shear
                self._rf_results[i][2][j]=rf_bolt_combined
    #-------------------------------------------------------------------------------------------------------------------

    def _jacobian(self, f, x, h=1e-5):
        """
        Approximates the Jacobian matrix of a given function using finite differences.

        Parameters:
        f (callable): Function for which the Jacobian is computed. It must return an array.
        x (array-like): Point at which the Jacobian is evaluated.
        h (float, optional): Step size for finite differences. Default is 1e-5.

        Returns:
        numpy.ndarray: Approximated Jacobian matrix.
        """
        n = len(x)
        J = np.zeros((n, n))
        fx = f(x)
        for i in range(n):
            x_i = x.copy()
            x_i[i] += h
            J[:, i] = (f(x_i) - fx) / h
        return J
    #-------------------------------------------------------------------------------------------------------------------

    def _newton_raphson(self, f, x0, tol=1e-8, max_iter=100):
        """
        Solves a system of nonlinear equations using the Newton-Raphson method.

        Parameters:
        f (callable): Function representing the system of equations. It must return an array.
        x0 (array-like): Initial guess for the solution.
        tol (float, optional): Tolerance for convergence. Default is 1e-8.
        max_iter (int, optional): Maximum number of iterations. Default is 100.

        Returns:
        numpy.ndarray: Approximate solution to the system.

        Raises:
        ValueError: If the Jacobian is singular or if the method does not converge within max_iter iterations.
        """
        x = np.array(x0, dtype=float)
        for _ in range(max_iter):
            fx = f(x)
            if np.linalg.norm(fx, ord=2) < tol:
                return x
            J = self._jacobian(f, x)
            try:
                dx = np.linalg.solve(J, -fx)
            except np.linalg.LinAlgError:
                raise ValueError("Jacobian is singular, try a different initial guess")
            x += dx
        raise ValueError("No convergence: reached max_iter")
    #-------------------------------------------------------------------------------------------------------------------

    def _f_solve(self, func, x0):
        """
        Finds the roots of a nonlinear equation or system of equations.

        Parameters:
        func (callable): Function representing the equation or system. It must return an array.
        x0 (array-like): Initial guess for the root.

        Returns:
        numpy.ndarray: Computed root of the equation/system.
        """
        x0 = np.atleast_1d(x0)  # Ensure input is an array
        return self._newton_raphson(func, x0)
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_boltcombined_met_plate_industrial(self, rf_bolt_shear, coef_a, coef_b, i, j) -> None:
        """
        Method used to obtain the Bolt Combined RF for each 1D element for a metallic plate.

        Args:
            rf_boltshear: bolt shear RF
            coef_a (float): coefficient "a" for boltcombined industrial RF calculation for metallic plates
            coef_b (float): coefficient "b" for boltcombined industrial RF calculation for metallic plates
            i (int): positioner of the element inside the 1D element dictionary 
            j (int): positioner of the LC studied
        """
        rf_bolt_tenion = self._rf_results[i][0][j]
        r_T = 1/rf_bolt_tenion
        r_S = 1/rf_bolt_shear

        def equation(rf):
            return (rf*r_T)**coef_a + (rf*r_S)**coef_b - 1
        
        solution = self._f_solve(equation, min(rf_bolt_tenion,rf_bolt_shear))

        return solution
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_boltcombined_comp_plate_industrial(self, rf_boltshear, coef_alpha, coef_beta, i, j, plate) -> None:
        """
        Method used to obtain the Bolt Combined RF for each 1D element for a composite plate.

        Args:
            rf_boltshear: bolt shear RF
            coef_alpha (float): coefficient "a" for boltcombined industrial RF calculation for composite plates
            coef_beta (float): coefficient "b" for boltcombined industrial RF calculation for composite plates
            i (int): positioner of the element inside the 1D element dictionary 
            j (int): positioner of the LC studied
            plate (N2Plate): composite plate being evaluated
        """
        # Pull-through RF for this plate
        composite_elem_pos = self._comp_elements_list.index(plate.ElementList[0])

        rf_pull_through = self._comp_rf_results[composite_elem_pos][0][j]
        rf_bolt_tension = self._rf_results[i][0][j]

        if math.isnan(rf_pull_through):
            r_T = rf_bolt_tension
        else:
            r_T = min(rf_pull_through, rf_bolt_tension)

        r_S = rf_boltshear

        def equation(rf):
            return (rf/r_T)**coef_alpha + (rf/r_S)**coef_beta - 1
        
        solution = self._f_solve(equation, min(r_T, r_S))

        return solution
    #-------------------------------------------------------------------------------------------------------------------

    def _input_data_echo(self) -> None:
        """
        Method used to create the input data echo for the elements analysed in this class.
        """

        # Create a list of tuples for the structured array containing information about each element
        data = []
        for x, key in enumerate(self._rivet_elements):
            joint_x = self._rivet_elements[key]["N2PJoint"]
            if not joint_x.FastenerSystem == None:

                # FastenerSystem object assignated to element x
                fastsyst=joint_x.FastenerSystem

                # JointAnalysisParameter object assiganted to element x
                fast_jap=joint_x.JointAnalysisParameters

                entry = (
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        key.ID,
                        key.Prop[0],
                        "**RIVET**",                                #self._comp_elements[key]["Side"], NOT USED IN RIVETS
                        self._rivet_elements[key]["N2PJoint"].ID,
                        None,                                       #self._comp_elements[key]["N2PPlate"].ID, NOT USED IN RIVETS
                        None,                                       #self._comp_elements[key]["Thickness"], NOT USED IN RIVETS
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
                        None,                                       #fast_jap.ShearType, NOT USED IN RIVETS
                        None,                                       #fast_jap.CenvMet, NOT USED IN RIVETS
                        None,                                       #fast_jap.CenvComp, NOT USED IN RIVETS
                        None,                                       #fast_jap.UserKDFComp, NOT USED IN RIVETS
                        None,                                       #fast_jap.UserKDFMet, NOT USED IN RIVETS
                        fast_jap.UserKDFBoltShear,
                        fast_jap.UserKDFBoltTension,
                        None,                                       #fast_jap.M, NOT USED IN RIVETS
                        None,                                       #fast_jap.TShim, NOT USED IN RIVETS
                        None,                                       #fast_jap.TShimL, NOT USED IN RIVETS
                        None,                                       #fast_jap.CPrying, NOT USED IN RIVETS
                        None,                                       #fast_jap.PT_Alpha_Met, NOT USED IN RIVETS
                        None,                                       #fast_jap.PT_Gamma_Met, NOT USED IN RIVETS
                        None,                                       #fast_jap.EdgeDistance[pos],
                        None,                                       #fast_jap.EffectiveWidth[pos],
                        None,                                       #fast_jap.NetRatio[pos],
                        None,                                       #fast_jap.NetSectionArea[pos],
                        fast_jap.Coef_A_CombinedMet,
                        fast_jap.Coef_B_CombinedMet,
                        fast_jap.Coef_Alpha_CombinedComp,
                        fast_jap.Coef_Beta_CombinedComp,
                        None,                                       #fast_jap.Coef_SRF_NetSection_Met[pos], NOT USED IN RIVETS
                        #-------------------------------------------------------------------------------------------------------------#
                        #-----------------------------#######---------[PULL-THROUGH PARAMETERS]---------#######-----------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        #-------------------------------------------------------------------------------------------------------------#
                        #------------------------------#######-----------[BEARING PARAMETERS]----------#######------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
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
        Method used to start RF calculations for 1D elements.
        """

        # An zeros-like numpy array is created so as to store the RFs:
        long_1=len(self._rivet_elements) # Number of studied metallic elements
        long_2=3 # Number of failure modes studied

        # If no GetLoadFasteners is provided, then LoadCases list is set to 1
        if self._get_load_fasteners == None:
            long_3 = 1
        else:
            long_3=len(self._get_load_fasteners.LoadCases) # Number of loadcases

        elems_ids=np.zeros((long_1,1,long_3), dtype=np.int64)
        self._rf_results=np.full((long_1,long_2,long_3), np.nan)

        # A numpy array is created in order to create the HDF5 input file
        self._input_h5_rivet=np.full((long_1,6), np.nan)

        t1 = time()

        for i,key in enumerate(self._rivet_elements):

            rivet_element_dict = self._rivet_elements[key]

            # Element id is written inside the input h5 file
            self._input_h5_rivet[i][0] = key.ID

            # N2PJoint associated to this 1D element
            joint = rivet_element_dict["N2PJoint"]

            # RF values calculation for each failure mode considered

            # If the associated joint has no FastenerSystem, this elem id RF cannot be calculated
            if (not joint.FastenerSystem == None):

                # Pull-through RF calculation
                self._rf_bolttension_rivet_industrial(i,key,joint)

                # Bearing and Bearing-ByPass RF calculation
                self._rf_boltshear_boltcombined_rivet_industrial(i,key,joint)

            for j in range(long_3):
                elems_ids[i][0][j] = key.ID

        # ---- For time checking ----
        t2 = time() 
        dt = t2 - t1
        if dt < 60:
            #N2PLog.set_file_level("DEBUG") 
            N2PLog.Debug.D903(str(dt) + " seconds.")
        else: 
            #N2PLog.set_file_level("DEBUG")
            minutes = int(dt // 60)
            seconds = dt - minutes*60
            N2PLog.Debug.D903(str(minutes) + " min, " + str(seconds) + " sec.")
        # ---------------------------

        # Rivets input data echo array is created
        self._input_data_echo()
    #-------------------------------------------------------------------------------------------------------------------