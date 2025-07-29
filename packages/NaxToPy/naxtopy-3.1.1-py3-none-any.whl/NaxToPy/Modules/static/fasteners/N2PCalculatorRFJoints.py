from NaxToPy.Modules.static.fasteners.N2PGetFasteners import N2PGetFasteners
from NaxToPy.Modules.static.fasteners.N2PGetLoadFasteners import N2PGetLoadFasteners
from NaxToPy.Modules.static.fasteners.joints.N2PJointAnalysisParameters import N2PJointAnalysisParameters
from NaxToPy.Modules.static.fasteners.N2PCompRF import N2PCompRF
from NaxToPy.Modules.static.fasteners.N2PMetalRF import N2PMetalRF
from NaxToPy.Modules.static.fasteners.N2PRivetRF import N2PRivetRF
from NaxToPy.Modules.common.model_processor import elem_to_material,get_properties
from NaxToPy.Core.Errors.N2PLog import N2PLog
import numpy as np
import sys 
from time import time
import csv
from NaxToPy.Modules.common.hdf5 import HDF5_NaxTo
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry
import math
from datetime import datetime

class N2PCalculatorRFJoints:

    """
    Class that manages the Reserve Factor (RF) calculation process of the joints obtained through
    the modules N2PGetFasteners and N2PGetLoadFasteners.

    Example: 
        >>> import NaxToPy as n2p 
        >>> from NaxToPy.Modules.Fasteners.N2PGetFasteners import N2PGetFasteners
        >>> from NaxToPy.Modules.Fasteners.N2PGetLoadFasteners import N2PGetLoadFasteners
        >>> from NaxToPy.Modules.Fasteners.Joints.N2PFastenerSystem import N2PFastenerSystem
        >>> from N2PCalculatorRFJoints import N2PCalculatorRFJoints
        >>> model1 = n2p.get_model(route.fem) # model loaded 
        >>> fasteners = N2PGetFasteners() 
        >>> fasteners.Model = model1 # compulsory input 
        >>> fasteners.calculate() # fasteners are obtained  
        >>> loads = N2PGetLoadFasteners()
        >>> loads.GetFasteners = fasteners # compulsory input 
        >>> loads.ResultsFiles = [r"route1.op2", r"route2.op2", r"route3.op2"] # the desired results files are loaded
        >>> loads.OptionalAttributes.DefaultDiameter = 4.0 #  joints with no previously assigned diameter will get this diameter (optional)
        >>> loads.calculate() # calculations will be made and results will be exported
        >>> Fastener_HWGT315 = N2PFastenerSystem() # Fastener system definition to be assigned to one or more joints
        >>> Fastener_HWGT315.Designation = "HWGT315-5-LEADING-EDGE"
        >>> Fastener_HWGT315.Fastener_pin_single_SH_allow = 5555.0
        >>> Fastener_HWGT315.Fastener_collar_single_SH_allow = 5555.0
        >>> Fastener_HWGT315.Fastener_pin_tensile_allow = 5555.0
        >>> Fastener_HWGT315.Fastener_collar_tensile_allow = 5555.0
        >>> Fastener_HWGT315.D_head = 10.5
        >>> Fastener_HWGT315.D_tail = 9.5
        >>> Fastener_HWGT315.D_nom = 5.5
        >>> loads.JointsList[k].FastenerSystem = Fastener_HWGT315 # Fastener system assigned to joint k
        >>> rf = N2PCalculatorRFJoints()
        >>> rf.GetFasteners = fasteners # compulsory input
        >>> rf.ExportLocation = "path"
        >>> rf.elements_manager_filter(mode = "ADVANCED", table_print = "EXCEL") # analysis elements are classified
        >>> # Materials Allowables Definition for Mat ID:11211000
        >>> rf.AnalysisCompMats[(11211000, '0')]._allowableORTO.ILSS = 200.00
        >>> # Laminates Allowables Definition for PCOMP ID:13010000
        >>> rf.AnalysisCompProps[13010000].BearingAllowable = 400.0 
        >>> rf.AnalysisCompProps[13010000].OHTAllowable = 7222.0E-6
        >>> rf.AnalysisCompProps[13010000].OHCAllowable = -3632.0E-6
        >>> rf.AnalysisCompProps[13010000].FHTAllowable = 7222.0E-6
        >>> rf.AnalysisCompProps[13010000].FHCAllowable = -3632.0E-6
        >>> # Metallic Allowables Definition for MAT ID:12345678
        >>> rf.AnalysisMetalProps[12345678].Fbru_e1p5d = 600.0
        >>> rf.AnalysisMetalProps[12345678].Fbru_e2d = 650.0
        >>> rf.AnalysisMetalProps[12345678].Ftu = 500.0
        >>> rf.GetLoadFasteners = loads # compulsory input if "calculate()" is called
        >>> rf.calculate() # RF calculations are performed
        >>> rf.rf_min_and_lc_to_CSV() # (Optional) -> Min reserve factors (RFs,LCs) are exported
        >>> rf.rf_min_and_lc_to_EXCEL() # (Optional) -> Min reserve factors (RFs,LCs) are exported
        >>> rf.rf_and_lc_to_CSV() # (Optional) -> All RFs for all LCs are exported

    """
    
    __slots__= ("_get_fasteners",
                "_get_load_fasteners",
                "_rf_analysis_elems",
                "_analysis_comp_props",
                "_analysis_comp_mats",
                "_analysis_metal_props",
                "_analysis_metal_mats",
                "_rf_results",
                "_export_location",
                "_export_datatime",
                "_joints_no_FastenerSystem",
                "_plates_wrong_property",
                "_fasts_wrong_property"
                )
    
    # N2PCalculatorRF constructor --------------------------------------------------------------------------------------
    def __init__(self):
        """
        The constructor creates an empty N2PCalculatorRF instance. Its attributes must be added as properties.
        
        """
        self._get_fasteners: N2PGetFasteners = None
        self._get_load_fasteners: N2PGetLoadFasteners = None
        self._rf_analysis_elems: dict = None
        self._analysis_comp_props: dict = None
        self._analysis_comp_mats: dict = None
        self._analysis_metal_props: dict = None
        self._analysis_metal_mats: dict = None
        self._rf_results: dict = None
        self._export_location: str = None
        self._export_datatime: str = None
        
    # Getters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @property
    def GetFasteners(self) -> N2PGetFasteners:
        """
        N2PGetFasteners instance. It is a compulsory input and an error will occur if this is not present.
        """

        return self._get_fasteners
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def GetLoadFasteners(self) -> N2PGetLoadFasteners:
        """
        N2PGetLoadFasteners instance. It is a compulsory input and an error will occur if this is not present.
        """

        return self._get_load_fasteners
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def RFResults(self) -> dict:
        """
        Results obtained in calculate().
        """

        return self._rf_results
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def RFAnalysisElems(self) -> dict:
        """
        Dictionary containing the analysis objects (plates and connectors)
        """
    
        return self._rf_analysis_elems
    #-------------------------------------------------------------------------------------------------------------------
    
    @property
    def AnalysisCompProps(self) -> dict:
        """
        Dictionary which contains all the analysis CompositeShell objects.
        """

        return self._analysis_comp_props
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def AnalysisCompMats(self) -> dict:
        """
        Dictionary which contains all the analysis composite materials objects.
        """

        return self._analysis_comp_mats
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def AnalysisMetalProps(self) -> dict:
        """
        Dictionary which contains all the analysis Shell objects.
        """

        return self._analysis_metal_props
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def AnalysisMetalMats(self) -> dict:
        """
        Dictionary which contains all the analysis Isotropic objects.
        """

        return self._analysis_metal_mats
    #-------------------------------------------------------------------------------------------------------------------

    @property
    def ExportLocation(self) -> str:
        """
        Path where the results are to be exported. 
        """

        return self._export_location

    # Setters ----------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    @GetFasteners.setter
    def GetFasteners(self, value: N2PGetFasteners) -> None:

        # If "value" is a N2PGetFasteners object, it is stored.
        if not isinstance(value, N2PGetFasteners):
            msg = N2PLog.Critical.C901('GetFasteners', 'N2PGetFasteners object')
            raise Exception(msg)
        else:
            self._get_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @GetLoadFasteners.setter
    def GetLoadFasteners(self, value: N2PGetLoadFasteners) -> None:

        # If "value" is a N2PGetLoadFasteners object, it is stored.
        if not isinstance(value, N2PGetLoadFasteners):
            msg = N2PLog.Critical.C901('GetLoadFasteners', 'N2PGetLoadFasteners object')
            raise Exception(msg)
        else:
            self._get_load_fasteners = value
    #-------------------------------------------------------------------------------------------------------------------

    @ExportLocation.setter
    def ExportLocation(self, value:str) -> None:

        # If "value" is a str, it is stored.
        if not isinstance(value, str):
            msg = N2PLog.Critical.C901('ExportLocation', 'str')
            raise Exception(msg)
        else:
            self._export_location = value
    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------

    def _elements_manager_filter_printer(self, printer_option):
        """
        Method that prints the dictionaries obtained through the method elements manager filter

        Arg:
            printer_option(str): it controls the type of output file, "EXCEL" or "CSV"
        """

        # Only critical errors are displayed on console
        N2PLog.set_console_level("CRITICAL")

        # Each kind of element is seperated individually in a different dictionary
        comp_elems_dict = self._rf_analysis_elems["COMP_ELEMENTS"]
        metal_elems_dict = self._rf_analysis_elems["METAL_ELEMENTS"]
        connectors_elems_dict = self._rf_analysis_elems["1D_ELEMENTS"]

        # Columns names difinition for printing stage
        shell_columns=["Element Id", "Side","Joint Id","Plate Id","Thickness","Fastener System"]
        connector_columns=["Element Id", "Joint Id", "Fastener System"]

        #
        list_for_comp_dict = []
        list_for_met_dict = []
        list_for_conect_dict = []

        # Loop to navigate through each element-type dictionary created before (except rivets)
        for dict in [comp_elems_dict,metal_elems_dict]:
            # Loop to navigate through each element of each element-type dictionary
            for key in dict:

                if dict[key]["N2PJoint"].FastenerSystem == None:
                    fastenersystem = None
                else:
                    fastenersystem = dict[key]["N2PJoint"].FastenerSystem.Designation

                list_for_el =(key.ID,
                              dict[key]["Side"],
                              dict[key]["N2PJoint"].ID,
                              dict[key]["N2PPlate"].ID,
                              dict[key]["Thickness"],
                              fastenersystem)

                if dict == comp_elems_dict:
                    list_for_comp_dict.append(list_for_el)
                else:
                    list_for_met_dict.append(list_for_el)

        #Loop to navigate through the elements contained in the rivet-element-type dictionary created before
        for key in connectors_elems_dict:

            if connectors_elems_dict[key]["N2PJoint"].FastenerSystem == None:
                fastenersystem = None
            else:
                fastenersystem = connectors_elems_dict[key]["N2PJoint"].FastenerSystem.Designation

            list_for_el =(key.ID,
                          connectors_elems_dict[key]["N2PJoint"].ID,
                          fastenersystem)
            list_for_conect_dict.append(list_for_el)

        if printer_option == "EXCEL":

            # If the printer option selected by the user asks for an EXCEL file, Pandas library must be imported
            # If Pandas is not installed, then a critical error is raised
            try:
                import pandas as pd
                dfr_comp = pd.DataFrame(list_for_comp_dict, columns=shell_columns)
                dfr_met = pd.DataFrame(list_for_met_dict, columns=shell_columns)
                dfr_connect = pd.DataFrame(list_for_conect_dict, columns=connector_columns)

                path_excel = r"{}\\{}.xlsx".format(self.ExportLocation,"ALL_ANALYSIS_ELEMENTS_FILTER_PRINT_"+self._export_datatime)

                with pd.ExcelWriter(path_excel) as writer:
                    
                    dfr_comp.to_excel(writer, sheet_name = "COMP_ELEMENTS", index=False)
                    dfr_met.to_excel(writer, sheet_name = "METAL_ELEMENTS", index=False)
                    dfr_connect.to_excel(writer, sheet_name = "CONNECTORS_ELEMENTS", index=False)

            except:
                # An Error is raised if "Excel" print type is selected but Pandas is not installed
                # In this case, the output is written in CSV format to avoid code interrumption
                N2PLog.Error.E905()
                printer_option == "CSV"

        if printer_option == "CSV":

            path_csv_comp = r"{}\\{}.csv".format(self.ExportLocation,"COMP_ANALYSIS_ELEMENTS_"+self._export_datatime)
            path_csv_met = r"{}\\{}.csv".format(self.ExportLocation,"METAL_ANALYSIS_ELEMENTS_"+self._export_datatime)
            path_csv_connect = r"{}\\\{}.csv".format(self.ExportLocation,"CONNECTORS_ANALYSIS_ELEMENTS_"+self._export_datatime)

            # The CSV file is created and filled into the selected export location
            with open(path_csv_comp, mode='w', newline="") as file:
                writer=csv.writer(file)
                writer.writerow(shell_columns) # Write the data header
                writer.writerows(list_for_comp_dict) # Write the data rows

            # The CSV file is created and filled into the selected export location
            with open(path_csv_met, mode='w', newline="") as file:
                writer=csv.writer(file)
                writer.writerow(shell_columns) # Write the data header
                writer.writerows(list_for_met_dict) # Write the data rows

            # The CSV file is created and filled into the selected export location
            with open(path_csv_connect, mode='w', newline="") as file:
                writer=csv.writer(file)
                writer.writerow(connector_columns) # Write the data header
                writer.writerows(list_for_conect_dict) # Write the data rows
    #-------------------------------------------------------------------------------------------------------------------

    def _composite_allowables_init(self):
        """
        Method that calls get_properties and elem_to_materials methods for composite allowables definition
        """

        # Composite elements for RF calculation
        comp_analysis_elems = list(self._rf_analysis_elems["COMP_ELEMENTS"].keys())

        # CompositeShell objects
        self._analysis_comp_props = get_properties(self._get_fasteners.Model, comp_analysis_elems)[0]

        # Composite materials objects
        self._analysis_comp_mats = elem_to_material(self._get_fasteners.Model, comp_analysis_elems)[2]
    #-------------------------------------------------------------------------------------------------------------------

    def _metallic_allowables_init(self):
        """
        Method that calls get_properties and elem_to_materials methods for composite allowables definition
        """

        # Metallic elements for RF calculation
        metal_analysis_elems = list(self._rf_analysis_elems["METAL_ELEMENTS"].keys())

        # Shell objects
        self._analysis_metal_props = get_properties(self._get_fasteners.Model, metal_analysis_elems)[0]

        # Isotropic objects
        self._analysis_metal_mats = elem_to_material(self._get_fasteners.Model, metal_analysis_elems)[2]
    #-------------------------------------------------------------------------------------------------------------------

    def _laminate_PT_allow_min_obtention(self):
        """
        Method used to determine the laminate pull-through allowable stress if Laminate.PTAllowable 
        has not been previously defined by the user, it is calculated as the minimum allowable "ills" of 
        each material detected inside the laminate 
        """

        for prop in self._analysis_comp_props:
            if self._analysis_comp_props[prop].PTAllowable == None:
                prop_plies=self._analysis_comp_props[prop].Laminate
                ilss_min=100000000.0
                for plie in prop_plies:
                    ply_ilss=self._analysis_comp_mats[plie.mat_ID].Allowables.ILSS
                    if (ply_ilss is not None) and (ply_ilss < ilss_min):
                        ilss_min = ply_ilss

                self._analysis_comp_props[prop].PTAllowable = ilss_min
    #-------------------------------------------------------------------------------------------------------------------    

    def elements_manager_filter(self, mode: str="ADVANCED", table_print: str="NO"):
        """
        Method used to find all the analysis elements (2D & 1D) of a N2PGetFasteners class
        and store them in three different categories: COMP_ELEMENTS, METAL_ELEMENTS & 1D_ELEMENTS.

        Calling example #1: 
            >>> elements_manager_filter(mode = "SIMPLE", table_print = "EXCEL")

        Calling example #2: 
            >>> elements_manager_filter(mode = "ADVANCED", table_print = "CSV")

        The SIMPLE mode only creates the dictionary of analysis elements. This is intended to be
        used when the user first needs a dictionary containing all the analysis elements connected
        to the corresponding N2PJoint and N2PPlates objects.

        The ADVANCED mode creates both the dictionary and each joint N2PJointAnalysisParameters class
        using the corresponding default values. This is intended to be used once the user has assigned
        a N2PFastenerSystem to each N2PJoint of the analysis. (Default).

        table_print (OPTIONAL) = "NO" (DEFAULT) / "EXCEL" / "CSV"

        Arg:
            mode (str): "SIMPLE" or "ADVANCED" (Default)
            table_print (str): "EXCEL", "CSV" or "NO (Default)
        """

        # Boleean to control if there are joints without N2PFastenerSystem
        self._joints_no_FastenerSystem = False

        # Boleean to control if there are plates with no applicable property
        self._plates_wrong_property = False

        # Boleean to control if there are fasts with no applicable property
        self._fasts_wrong_property = False

        # Only critical errors are displayed on console
        N2PLog.set_console_level("CRITICAL")

        # Export data time for files name
        self._export_datatime = datetime.today().strftime('%Y-%m-%d_%H%M%S')

        # If this method do not find a N2PGetLoadFastener object, the code stops
        if self._get_fasteners == None:
            msg = N2PLog.Critical.C902()
            raise Exception(msg)
        
        # If mode or table_print is not properly defined, the code stops
        if mode not in {"SIMPLE","ADVANCED"}:
            N2PLog.Error.E901("mode", "'SIMPLE' or 'ADVANCED'", "SIMPLE")
            mode = "SIMPLE"

        if table_print not in {"NO","CSV","EXCEL"}:
            N2PLog.Error.E901("table_print", "'NO' or 'CSV' or 'EXCEL'", "NO")
            table_print = "NO"

        t1 = time()

        comp_elems={}
        met_elems={}
        rivet_elems={}

        for i,joint_i in enumerate(self._get_fasteners.JointsList, start = 1):

            # N2PJointAnalysisParameters object is created in ADVANCED mode
            if mode == "ADVANCED" and joint_i.FastenerSystem == None:
                N2PLog.Error.E900(joint_i.ID)
                self._joints_no_FastenerSystem = True

            elif mode == "ADVANCED" and not (joint_i.FastenerSystem == None):    
                joint_i_parameters = N2PJointAnalysisParameters(joint_i)

            for j, plate in enumerate(joint_i.PlateList):

                plate_central_elem = plate.ElementList[0]

                #-------------------------------SIDE ASSIGNAMENT----------------------------------------------
                platej_prop = self._get_fasteners.Model.PropertyDict[plate_central_elem.Prop]
                proptype = platej_prop.PropertyType

                if j ==0:
                    side = "Head"
                elif j == (len(joint_i.PlateList)-1):
                    side = "Tail"
                else: 
                    side = "Middle"

                #------------------------------COMPOSITE ELEMENTS----------------------------------------------
                if proptype == "PCOMP":
                    # The total thickness of the laminate is calculated
                    thickness = platej_prop.Thickness
                    t=0
                    for n in thickness:
                        t=t+n
                    
                    comp_elems[plate_central_elem] = {"Side": side, "N2PJoint":joint_i, "N2PPlate": plate, "Thickness": t}

                #------------------------------METALLIC ELEMENTS-----------------------------------------------
                elif proptype == "PSHELL":
                    t = platej_prop.Thickness
                    met_elems[plate_central_elem] = {"Side": side, "N2PJoint":joint_i, "N2PPlate": plate, "Thickness": t}

                #------------------------------OTHER 2D ELEMENTS -> IGNORED AND WARNING W903-------------------
                else:
                    # A warning is raised if the plate hasn't got a PSHELL or PCOMP property.
                    N2PLog.Warning.W902(plate_central_elem.ID)
                    self._plates_wrong_property = True
                
                # Plate parameters are calculated and stored in ADVANCED mode
                if mode == "ADVANCED" and not (joint_i.FastenerSystem == None):
                    joint_i_parameters._parameters_manager(plate, t, proptype, side)

            # N2PJointAnalysisParameters object is assignated to the N2PJoint in ADVANCED mode
            if mode == "ADVANCED" and not (joint_i.FastenerSystem == None):
                joint_i.JointAnalysisParameters = joint_i_parameters

            #------------------------------1D ELEMENTS--------------------------------------------------
            for k in joint_i.Bolt.ElementList:
                # The 1D FEM element is stored 
                rivet_elems[k] = {"N2PJoint": joint_i}

        # Dictionary creation
        self._rf_analysis_elems = {"COMP_ELEMENTS":comp_elems, 
                                  "METAL_ELEMENTS":met_elems,
                                  "1D_ELEMENTS":rivet_elems}

        # ------------------------------- For time debug message ---------------------------------
        t2 = time() 
        dt = t2 - t1
        if dt < 60: 
            #N2PLog.set_file_level("DEBUG")
            N2PLog.Debug.D900(str(dt) + " seconds.")
        else: 
            #N2PLog.set_file_level("DEBUG")
            minutes = int(dt // 60)
            seconds = dt - minutes*60
            N2PLog.Debug.D900(str(minutes) + " min, " + str(seconds) + " sec.")
        # ----------------------------------------------------------------------------------------

        # This dictionary is printed inside an excel file is Excel_Print = True
        if table_print == "EXCEL" or "CSV":

            # If the ExportLocation property is not defined, the code stops and raises an Exception
            if self._export_location == None:
                msg = N2PLog.Critical.C904()
                raise Exception(msg)
            else:    
                self._elements_manager_filter_printer(table_print)

        # Composite allowable parameters are created so as to be fullfilled before calculate()
        self._composite_allowables_init()

        # Metallic allowable parameters are created so as to be fullfilled before calculate()
        self._metallic_allowables_init()
    #-------------------------------------------------------------------------------------------------------------------

    def _input_data_echo_to_CSV(self, data) -> None:
        """
        Method used to export the data input echo to a CSV file

        Args:
            data: list -> list contaning all the elements input data to be printed
        """

        # Define the input format
        input_format=[
                      #-------------------------------------------------------------------------------------------------------------#  
                      #-------------------------------------------------------------------------------------------------------------#
                      ("Element_ID", "i4"),                         # FEM element id
                      ("Property_ID", "i4"),                        # FEM property id
                      ("Side","|S6"),                               # Plate side (Head / Middle / Tail)
                      ("Joint_ID", "i4"),                           # Joint id
                      ("Plate_ID", "i4"),                           # Plate id
                      ("Plate thickness", "f4"),                    # Plate thickness
                      #-------------------------------------------------------------------------------------------------------------# 
                      ("Fastener_System", "S30"),                   #######---------[FASTENER SYSTEM INFORMATION]---------#######----
                      #-------------------------------------------------------------------------------------------------------------# 
                      ("Fastener_pin_single_SH_allow", "f4"),       # F.S. Pin shear allowable value for single shear
                      ("Fastener_collar_single_SH_allow", "f4"),    # F.S. Collar shear allowable value for single shear
                      ("Fastener_pin_tensile_allow", "f4"),         # F.S. Pin tensile allowable value
                      ("Fastener_collar_tensile_allow", "f4"),      # F.S. Collar tensile allowable value
                      ("D_head", "f4"),                             # F.S. Head diameter
                      ("D_tail", "f4"),                             # F.S. Tail diameter
                      ("D_nom", "f4"),                              # F.S. Nominal diameter
                      ("Configuration", "|S5"),                     # F.S. Configuration
                      ("FastenerType", "|S5"),                      # F.S. Type
                      ("FastenerInstallation", "|S13"),             # F.S. Installation
                      ("FastenerHead", "|S3"),                      # F.S. Head
                      ("FloatingNut", "|S5"),                       # F.S. Floating nut
                      ("AluminumNut", "|S5"),                       # F.S. Aluminum nut
                      #-------------------------------------------------------------------------------------------------------------# 
                                                                    #######---------[JOINT ANALYSIS PARAMETERS]---------#######------
                      #-------------------------------------------------------------------------------------------------------------#
                      ("ShearType", "|S5"),                         # J.A.P Shear type
                      ("CenvMet", "f4"),                            # J.A.P Cenv Met                                    ((METALLIC))
                      ("CenvComp", "f4"),                           # J.A.P Cenv Comp                                   ((COMPOSITE))                          
                      ("UserKDFComp", "f4"),                        # J.A.P User KDF Composite                          ((COMPOSITE))
                      ("UserKDFMet", "f4"),                         # J.A.P User KDF Metallic                           ((METALLIC))
                      ("UserKDFBoltShear", "f4"),                   # J.A.P User KDF Bolt Shear                         ((RIVETS))
                      ("UserKDFBoltTension", "f4"),                 # J.A.P User KDF Bolt Tension                       ((RIVETS))
                      ("M", "f4"),                                  # J.A.P Bearing-Bypass interaction slope            ((COMPOSITE))
                      ("TShim", "f4"),                              # J.A.P Tshim
                      ("TShimL", "f4"),                             # J.A.P TshimL
                      ("CPrying", "f4"),                            # J.A.P CPrying
                      ("PT_Alpha_Met", "f4"),                       # J.A.P PT_Alpha_Met                                ((METALLIC))
                      ("PT_Gamma_Met", "f4"),                       # J.A.P PT_Gamma_Met                                ((METALLIC))
                      ("EdgeDistance", "f4"),                       # J.A.P Edge Distance
                      ("EffectiveWidth", "f4"),                     # J.A.P EffectiveWidth
                      ("NetRatio", "f4"),                           # J.A.P NetRatio
                      ("NetSectionArea", "f4"),                     # J.A.P NetSectionArea
                      ("Coef_A_CombinedMet", "f4"),                 # J.A.P Coef_A_CombinedMet                          ((METALLIC))
                      ("Coef_B_CombinedMet", "f4"),                 # J.A.P Coef_B_CombinedMet                          ((METALLIC))
                      ("Coef_Alpha_CombinedComp", "f4"),            # J.A.P Coef_Alpha_CombinedComp                     ((COMPOSITE))
                      ("Coef_Beta_CombinedComp", "f4"),             # J.A.P Coef_Beta_CombinedComp                      ((COMPOSITE))
                      ("Coef_SRF_NetSection_Met", "f4"),            # J.A.P Coef_SRF_NetSection_Met                     ((METALLIC))
                      #-------------------------------------------------------------------------------------------------------------# 
                                                                    #######---------[PULL-THROUGH PARAMETERS]---------#######--------
                      #-------------------------------------------------------------------------------------------------------------#
                      ("F_T", "f4"),                                # P.T Bolt tensile allowable [force]
                      ("F_PT", "f4"),                               # P.T Laminate pull-through allowable [stress]      ((COMPOSITE))
                      ("C_BV", "f4"),                               # P.T Bolt-Value KDF
                      ("C_BT", "f4"),                               # P.T Bolt-Type KDF
                      ("Ksc", "f4"),                                # P.T Ksc                                           ((COMPOSITE))
                      ("C_srf_PT", "f4"),                           # P.T C SRF (Pull-through)                          ((METALLIC))
                      ("F_PT_allow", "f4"),                         # P.T Element pull-through allowable [force]
                      #-------------------------------------------------------------------------------------------------------------# 
                                                                    #######---------[BEARING PARAMETERS]---------#######-------------
                      #-------------------------------------------------------------------------------------------------------------#
                      ("F_base", "f4"),                             # BEA Base laminate bearing allowable strength      ((COMPOSITE))
                      ("C_jt", "f4"),                               # BEA Joint type KDF                                ((COMPOSITE))
                      ("C_e/d", "f4"),                              # BEA Edge distance influence KDF                   ((COMPOSITE))
                      ("C_torq", "f4"),                             # BEA Torque factor KDF                             ((COMPOSITE))
                      ("C_shim", "f4"),                             # BEA Shimming effect KDF                           
                      ("C_mod", "f4"),                              # BEA Bodulus variation KDF                         ((COMPOSITE))
                      ("F_bru_met", "f4"),                          # BEA Base metallic Bearing strength                ((METALLIC))
                      ("F_s_allow", "f4"),                          # BEA Pin allowable shear load [force]              ((METALLIC))
                      ("F_BEA_allow", "f4"),                        # BEA Element bearing allowable [strength]
                      #-------------------------------------------------------------------------------------------------------------# 
                                                                    #######---------[BEARING-BYPASS PARAMETERS]---------#######------
                      #-------------------------------------------------------------------------------------------------------------#
                      ("OHC_Allowable", "f4"),                      # B.P Allowable Open Hole Compression strength      ((COMPOSITE))
                      ("FHC_Allowable", "f4"),                      # B.P Allowable Filled Hole Compression strength    ((COMPOSITE))
                      ("OHT_Allowable", "f4"),                      # B.P Allowable Open Hole Tension strength          ((COMPOSITE))
                      ("FHT_Allowable", "f4"),                      # B.P Allowable Filled Hole Tension strength        ((COMPOSITE))
                      ("E_1", "f4"),                                # B.P Equivalent homogenized modulus E1             ((COMPOSITE))
                      ("E_2", "f4"),                                # B.P Equivalent homogenized modulus E2             ((COMPOSITE))
                      ("S_netsection_tension", "f4"),               # B.P Allowable Net section tension strength        ((COMPOSITE))
                      ("S_netsection_compres", "f4"),               # B.P Allowable Net section compres strength        ((COMPOSITE))
                      #-------------------------------------------------------------------------------------------------------------# 
                                                                    #######---------[NET SECTION PARAMETERS]---------#######---------
                      #-------------------------------------------------------------------------------------------------------------#
                      ("Anet/Agross", "f4"),                        # N.S Anet/Agross ratio                             ((METALLIC))
                      ("C_srf_NS", "f4"),                           # N.S Stress reduction factor for net section       ((METALLIC))
                      ("F_tu", "f4"),                               # N.S Tensile ultimate strength                     ((METALLIC))
                      ("F_NS_allow", "f4")                          # N.S Net section allowable strength [stress]       ((METALLIC))
                      ]
        
        # Header construction
        header = [item[0] for item in input_format]

        # The CSV file is created and filled into the selected export location
        with open(r"{}\\{}.csv".format(self._export_location,
                                        "N2PCalculatorRFJoints_INPUT_DATA_ECHO_"+self._export_datatime),
                                          mode='w', newline="") as file:
            writer=csv.writer(file)
            writer.writerow(header) # Write the data header
            writer.writerows(data) # Write the data rows
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_dataentry(self,i, comp_elements, metal_elements, rivets_elements, comp_rfs_values, metal_rfs_values, rivets_rfs_values) -> DataEntry:
        """
        Method used to create DataEntry objects based on a given LC (i).

        Args:
            comp_elements (dictionary): dictionary which contains 2D composite elements
            metal_elements (dictionary): dictionary which contains 2D metallic elements
            rivets_elements (dictionary): dictionary which contains 1D elements
            comp_rfs_values (np.array): fem 2D elements reserve factors values
            metal_rfs_values (np.array): fem 2D elements reserve factors values
            rivets_rfs_values (np.array): fem rivets reserve factors values
        """

        # Load case id to be written 
        if not self._get_load_fasteners == None:
            lc_id = self._get_load_fasteners.LoadCases[i].ID
        else:
            lc_id = -9999999

        # Format for RF writing process
        rf_format_comp = np.dtype([("ID_ENTITY", "i4"), 
                                   ("RF_PULLTHROUGH", "f4"), 
                                   ("RF_BEARING", "f4"), 
                                   ("RF_BEARINGBYPASS", "f4")])
        
        rf_format_metal = np.dtype([("ID_ENTITY", "i4"), 
                                    ("RF_PULLTHROUGH", "f4"), 
                                    ("RF_BEARING", "f4"), 
                                    ("RF_NETSECTION", "f4")])

        rf_format_rivets = np.dtype([("ID_ENTITY", "i4"), 
                                    ("RF_BOLT_TENSION", "f4"), 
                                    ("RF_BOLT_SHEAR", "f4"), 
                                    ("RF_BOLT_COMBINED", "f4")])
        
        rfs_comp = [(key.ID, 
                    comp_rfs_values[j][0][i], 
                    comp_rfs_values[j][1][i], 
                    comp_rfs_values[j][2][i]) for j,key in enumerate(comp_elements)]
        
        rfs_metal = [(key.ID, 
                    metal_rfs_values[j][0][i], 
                    metal_rfs_values[j][1][i], 
                    metal_rfs_values[j][2][i]) for j,key in enumerate(metal_elements)]
        
        rfs_rivets = [(key.ID, 
                    rivets_rfs_values[j][0][i], 
                    rivets_rfs_values[j][1][i], 
                    rivets_rfs_values[j][2][i]) for j,key in enumerate(rivets_elements)]

        data_entry_comp = DataEntry()
        data_entry_comp.ResultsName = "COMP_RESULTS"
        data_entry_comp.LoadCase = lc_id
        data_entry_comp.LoadCaseDescription = "LOAD CASE " + str(lc_id)
        data_entry_comp.LoadCaseName = "LC " + str(lc_id)
        data_entry_comp.Part = "(0,'0')"
        data_entry_comp.Data = np.array(rfs_comp, dtype=rf_format_comp)

        data_entry_metal = DataEntry()
        data_entry_metal.ResultsName = "METAL_RESULTS"
        data_entry_metal.LoadCase = lc_id
        data_entry_metal.LoadCaseDescription = "LOAD CASE " + str(lc_id)
        data_entry_metal.LoadCaseName = "LC " + str(lc_id)
        data_entry_metal.Part = "(0,'0')"
        data_entry_metal.Data = np.array(rfs_metal, dtype=rf_format_metal)

        data_entry_rivets = DataEntry()
        data_entry_rivets.ResultsName = "RIVETS_RESULTS"
        data_entry_rivets.LoadCase = lc_id
        data_entry_rivets.LoadCaseDescription = "LOAD CASE " + str(lc_id)
        data_entry_rivets.LoadCaseName = "LC " + str(lc_id)
        data_entry_rivets.Part = "(0,'0')"
        data_entry_rivets.Data = np.array(rfs_rivets, dtype=rf_format_rivets)

        return [data_entry_comp, data_entry_metal, data_entry_rivets]
    #-------------------------------------------------------------------------------------------------------------------

    def _export_rf_to_hd5f(self) -> None:
        """
        Method used to export the analysis elements RF to a HD5F file
        """

        hdf5_rf_results = HDF5_NaxTo()
        hdf5_rf_results.FileDescription = "Analysis Elements Reserve Factors"
        hdf5_rf_results.FilePath = r"{}\\{}.h5".format(self._export_location,"RF_RESULTS_"+self._export_datatime)
        hdf5_rf_results.create_hdf5()

        # Composite, metallic and rivet elements
        comp_elements = self._rf_analysis_elems["COMP_ELEMENTS"]
        metal_elements = self._rf_analysis_elems["METAL_ELEMENTS"]
        rivets_elements = self._rf_analysis_elems["1D_ELEMENTS"]

        # RF results to be written
        comp_rf_values=self._rf_results["COMP_ELEMENTS"]
        metal_rf_values=self._rf_results["METAL_ELEMENTS"]
        rivets_rf_values=self._rf_results["1D_ELEMENTS"]

        # RF results are written inside the hdf5 file
        if not self._get_load_fasteners == None:
            num_lcs = len(self._get_load_fasteners.LoadCases)
        else:
            num_lcs = 1

        for i in range(num_lcs):
            data = self._rf_dataentry(i, comp_elements, metal_elements, rivets_elements,
                                      comp_rf_values, metal_rf_values, rivets_rf_values)
            hdf5_rf_results.write_dataset([data[0]])
            hdf5_rf_results.write_dataset([data[1]])
            hdf5_rf_results.write_dataset([data[2]])
    #-------------------------------------------------------------------------------------------------------------------

    def _rf_manager_filter(self) -> list:
        """
        Method used to obtain the minimum RF value for each failure mode and its corresponding LC
        """
        composite_elements = self._rf_analysis_elems["COMP_ELEMENTS"]
        metallic_elements = self._rf_analysis_elems["METAL_ELEMENTS"]
        rivets_elements = self._rf_analysis_elems["1D_ELEMENTS"]

        loadcases_ids = [lc.ID for lc in self._get_load_fasteners.LoadCases]

        composite_rf_min_values = np.min(self._rf_results["COMP_ELEMENTS"], axis=2)
        composite_rf_min_pos = np.argmin(self._rf_results["COMP_ELEMENTS"], axis=2)

        metallic_rf_min_values = np.min(self._rf_results["METAL_ELEMENTS"], axis =2)
        metallic_rf_min_pos = np.argmin(self._rf_results["METAL_ELEMENTS"], axis=2)

        rivet_rf_min_values = np.min(self._rf_results["1D_ELEMENTS"], axis =2)
        rivet_rf_min_pos = np.argmin(self._rf_results["1D_ELEMENTS"], axis=2)

        for i, lc_id in enumerate(loadcases_ids):
            #
            composite_rf_min_pos[composite_rf_min_pos == i] = lc_id
            metallic_rf_min_pos[metallic_rf_min_pos == i] = lc_id
            rivet_rf_min_pos[rivet_rf_min_pos == i] = lc_id

        for x, elem in enumerate(composite_elements):
            if math.isnan(composite_rf_min_values[x][0]):
                composite_rf_min_pos[x][0]= -99999999
            if math.isnan(composite_rf_min_values[x][1]):
                composite_rf_min_pos[x][1]= -99999999
            if math.isnan(composite_rf_min_values[x][2]):
                composite_rf_min_pos[x][2]= -99999999

        for x, elem in enumerate(metallic_elements):
            if math.isnan(metallic_rf_min_values[x][0]):
                metallic_rf_min_pos[x][0]= -99999999
            if math.isnan(metallic_rf_min_values[x][1]):
                metallic_rf_min_pos[x][1]= -99999999
            if math.isnan(metallic_rf_min_values[x][2]):
                metallic_rf_min_pos[x][2]= -99999999

        for x, elem in enumerate(rivets_elements):
            if math.isnan(rivet_rf_min_values[x][0]):
                rivet_rf_min_pos[x][0]= -99999999
            if math.isnan(rivet_rf_min_values[x][1]):
                rivet_rf_min_pos[x][1]= -99999999
            if math.isnan(rivet_rf_min_values[x][2]):
                rivet_rf_min_pos[x][2]= -99999999

        comp_rf_min_value_pos = np.concatenate((composite_rf_min_values,composite_rf_min_pos), axis = 1)
        met_rf_min_value_pos = np.concatenate((metallic_rf_min_values,metallic_rf_min_pos), axis = 1)
        rivet_rf_min_value_pos = np.concatenate((rivet_rf_min_values,rivet_rf_min_pos), axis = 1)

        return [comp_rf_min_value_pos, met_rf_min_value_pos, rivet_rf_min_value_pos]
    #-------------------------------------------------------------------------------------------------------------------

    def rf_min_and_lc_to_CSV(self) -> None:
        """
        Method used to export each element RF min and its corresponding LC to a CSV file
        """
        # Critical error is raised if N2PGetLoadFasteners object has not been provided
        if self._get_load_fasteners == None:
            msg = N2PLog.Critical.C908()
            raise Exception(msg)
        
        # Define the input format
        input_format=[
                        #-------------------------------------------------------------------------------------------------------------#  
                        #-------------------------------------------------------------------------------------------------------------#
                        ("Element_ID", "i4"),                         # FEM element id
                        ("RF_PULLTHROUGH_MIN", "F4"),                 # Minimum Pull-Through RF                 ((METALLIC / COMPOSITE))
                        ("LC_RF_PULLTHROUGH_MIN", "i4"),              # LC of Minimum Pull-Through RF           ((METALLIC / COMPOSITE))
                        ("RF_BEARING_MIN", "F4"),                     # Minimum Bearing RF                      ((METALLIC / COMPOSITE))
                        ("LC_RF_BEARING_MIN", "i4"),                  # LC of Minimum Bearing RF                ((METALLIC / COMPOSITE))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_BEARINGBYPASS_MIN", "F4"),               # Minimum Bearing-Bypass RF               ((COMPOSITE))
                        ("LC_RF_BEARINGBYPASS_MIN", "i4"),            # LC of Minimum Bearing-Bypass RF         ((COMPOSITE))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_NETSECTION_MIN", "F4"),                  # Minimum Net-Section RF                  ((METALLIC))
                        ("LC_RF_NETSECTION_MIN", "i4"),               # LC of Minimum Net-Section               ((METALLIC))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_BOLTTENSION_MIN", "F4"),                 # Minimum Bolt-Tension RF                 ((RIVETS))
                        ("LC_RF_BOLTTENSION_MIN", "i4"),              # LC of Minimum Bolt-Tension RF           ((RIVETS))
                        ("RF_BOLTSHEAR_MIN", "F4"),                   # Minimum Bearing-Bypass RF               ((RIVETS))
                        ("LC_RF_BOLTSHEAR_MIN", "i4"),                # LC of Minimum Bearing-Bypass RF         ((RIVETS))
                        ("RF_BOLTCOMBINED_MIN", "F4"),                # Minimum Bearing-Bypass RF               ((RIVETS))
                        ("LC_RF_BOLTCOMBINED_MIN", "i4")              # LC of Minimum Bearing-Bypass RF         ((RIVETS))
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        ]
        
        # Header construction
        header = [item[0] for item in input_format]

        # Calculation of minimum RF and its LC for each element type
        rf_min_value_pos = self._rf_manager_filter()

        comp_rf_min_value_pos = rf_min_value_pos[0]
        met_rf_min_value_pos = rf_min_value_pos[1]
        rivet_rf_min_value_pos = rf_min_value_pos[2]

        ######################################################################################################################################################################################
        #| FEM ID | RF_PULL | LC_PULL | RF_BEA | LC_BEA | RF_BP | LC_BP | RF_NS | LC_NS | RF_BOLTTENSION | LC_BOLTTENSION | RF_BOLTSHEAR | LC_BOLTSHEAR | RF_BOLTCOMBINED | LC_BOLTCOMBINED |#
        ######################################################################################################################################################################################

        data = []

        rf_all_elements = self._rf_analysis_elems

        for key in rf_all_elements:
            
            if key == "COMP_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    row = comp_rf_min_value_pos[i]
                    rf_and_lc = (element.ID, row[0], row[3], row[1], row[4], row[2], row[5], None, None, None, None, None, None, None, None)
                    data.append(rf_and_lc)
                    
            if key == "METAL_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    row = met_rf_min_value_pos[i]
                    rf_and_lc = (element.ID, row[0], row[3], row[1], row[4], None, None, row[2], row[5], None, None, None, None, None, None)
                    data.append(rf_and_lc)

            if key == "1D_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    row = rivet_rf_min_value_pos[i]
                    rf_and_lc = (element.ID, None, None, None, None, None, None, None, None, row[0], row[3], row[1], row[4], row[2], row[5])
                    data.append(rf_and_lc)

        # The CSV file is created and filled into the selected export location
        with open(r"{}\\{}.csv".format(self._export_location,"RF_MIN_AND_LC_"+self._export_datatime),mode='w', newline="") as file:
            writer=csv.writer(file)
            writer.writerow(header) # Write the data header
            writer.writerows(data) # Write the data rows
    #-------------------------------------------------------------------------------------------------------------------

    def rf_and_lc_to_CSV(self) -> None:
        """
        Method used to export elements ALL RF for each LC to a CSV file
        """
        # Critical error is raised if N2PGetLoadFasteners object has not been provided
        if self._get_load_fasteners == None:
            msg = N2PLog.Critical.C908()
            raise Exception(msg)

        # Define the input format
        input_format=[
                        #-------------------------------------------------------------------------------------------------------------#  
                        #-------------------------------------------------------------------------------------------------------------#
                        ("Element_ID", "i4"),               # FEM element id                          ((ALL))
                        ("LoadCase_ID", "i4"),              # Load Case id                            ((ALL))
                        ("RF_PULLTHROUGH", "F4"),           # Minimum Pull-Through RF                 ((METALLIC / COMPOSITE))
                        ("RF_BEARING", "F4"),               # Minimum Bearing RF                      ((METALLIC / COMPOSITE))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_BEARINGBYPASS", "F4"),         # Minimum Bearing-Bypass RF               ((COMPOSITE))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_NETSECTION", "F4"),            # Minimum Net-Section RF                  ((METALLIC))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_BOLTTENSION", "F4"),           # Minimum Bolt-Tension RF                 ((RIVETS))
                        ("RF_BOLTSHEAR", "F4"),             # Minimum Bearing-Bypass RF               ((RIVETS))
                        ("RF_BOLTCOMBINED", "F4"),          # Minimum Bearing-Bypass RF               ((RIVETS))
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        ]
        
        # Header construction
        header = [item[0] for item in input_format]

        #########################################################################################################
        #| FEM ID | LC_id | RF_PULL | RF_BEA | RF_BP | RF_NS | RF_BOLTTENSION | RF_BOLTSHEAR | RF_BOLTCOMBINED |#
        #########################################################################################################

        # RF results are written inside the hdf5 file
        num_lcs = len(self._get_load_fasteners.LoadCases)

        data = []

        rf_all_elements = self._rf_analysis_elems

        for key in rf_all_elements:
            
            if key == "COMP_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    rfs = self._rf_results[key][i]
                    for x in range(num_lcs):
                        lc_id = self._get_load_fasteners.LoadCases[x].ID
                        rf_and_lc = (element.ID, lc_id, rfs[0][x], rfs[1][x], rfs[2][x], None, None, None, None)
                        data.append(rf_and_lc)

            if key == "METAL_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    rfs = self._rf_results[key][i]
                    for x in range(num_lcs):
                        lc_id = self._get_load_fasteners.LoadCases[x].ID
                        rf_and_lc = (element.ID, lc_id, rfs[0][x], rfs[1][x], None, rfs[2][x], None, None, None)
                        data.append(rf_and_lc)
                    
            if key == "1D_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    rfs = self._rf_results[key][i]
                    for x in range(num_lcs):
                        lc_id = self._get_load_fasteners.LoadCases[x].ID
                        rf_and_lc = (element.ID, lc_id, None, None, None, None, rfs[0][x], rfs[1][x], rfs[2][x])
                        data.append(rf_and_lc)

        # The CSV file is created and filled into the selected export location
        with open(r"{}\\{}.csv".format(self._export_location,"RF_AND_LC_"+self._export_datatime),mode='w', newline="") as file:
            writer=csv.writer(file)
            writer.writerow(header) # Write the data header
            writer.writerows(data) # Write the data rows
    #-------------------------------------------------------------------------------------------------------------------

    def rf_min_and_lc_to_EXCEL(self) -> None:
        """
        Method used to export each element RF min and its corresponding LC to an EXCEL file
        """

        # Critical error is raised if N2PGetLoadFasteners object has not been provided
        if self._get_load_fasteners == None:
            msg = N2PLog.Critical.C908()
            raise Exception(msg)
        
        # Define the input format
        input_format_comp=[
                        #-------------------------------------------------------------------------------------------------------------#  
                        #-------------------------------------------------------------------------------------------------------------#
                        ("Element_ID", "i4"),                         # FEM element id
                        ("RF_PULLTHROUGH_MIN", "F4"),                 # Minimum Pull-Through RF                 ((METALLIC / COMPOSITE))
                        ("LC_RF_PULLTHROUGH_MIN", "i4"),              # LC of Minimum Pull-Through RF           ((METALLIC / COMPOSITE))
                        ("RF_BEARING_MIN", "F4"),                     # Minimum Bearing RF                      ((METALLIC / COMPOSITE))
                        ("LC_RF_BEARING_MIN", "i4"),                  # LC of Minimum Bearing RF                ((METALLIC / COMPOSITE))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_BEARINGBYPASS_MIN", "F4"),               # Minimum Bearing-Bypass RF               ((COMPOSITE))
                        ("LC_RF_BEARINGBYPASS_MIN", "i4"),            # LC of Minimum Bearing-Bypass RF         ((COMPOSITE))
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        ]
        
        input_format_met=[
                        #-------------------------------------------------------------------------------------------------------------#  
                        #-------------------------------------------------------------------------------------------------------------#
                        ("Element_ID", "i4"),                         # FEM element id
                        ("RF_PULLTHROUGH_MIN", "F4"),                 # Minimum Pull-Through RF                 ((METALLIC / COMPOSITE))
                        ("LC_RF_PULLTHROUGH_MIN", "i4"),              # LC of Minimum Pull-Through RF           ((METALLIC / COMPOSITE))
                        ("RF_BEARING_MIN", "F4"),                     # Minimum Bearing RF                      ((METALLIC / COMPOSITE))
                        ("LC_RF_BEARING_MIN", "i4"),                  # LC of Minimum Bearing RF                ((METALLIC / COMPOSITE))
                        #-------------------------------------------------------------------------------------------------------------#
                        ("RF_NETSECTION_MIN", "F4"),                  # Minimum Net-Section RF                  ((METALLIC))
                        ("LC_RF_NETSECTION_MIN", "i4"),               # LC of Minimum Net-Section               ((METALLIC))
                        #-------------------------------------------------------------------------------------------------------------#
                        #-------------------------------------------------------------------------------------------------------------#
                        ]
        
        input_format_rivet=[
                            #-------------------------------------------------------------------------------------------------------------#  
                            #-------------------------------------------------------------------------------------------------------------#
                            ("Element_ID", "i4"),                         # FEM element id
                            ("RF_BOLTTENSION_MIN", "F4"),                 # Minimum Bolt-Tension RF                 ((RIVETS))
                            ("LC_RF_BOLTTENSION_MIN", "i4"),              # LC of Minimum Bolt-Tension RF           ((RIVETS))
                            ("RF_BOLTSHEAR_MIN", "F4"),                   # Minimum Bearing-Bypass RF               ((RIVETS))
                            ("LC_RF_BOLTSHEAR_MIN", "i4"),                # LC of Minimum Bearing-Bypass RF         ((RIVETS))
                            ("RF_BOLTCOMBINED_MIN", "F4"),                # Minimum Bearing-Bypass RF               ((RIVETS))
                            ("LC_RF_BOLTCOMBINED_MIN", "i4")              # LC of Minimum Bearing-Bypass RF         ((RIVETS))
                            #-------------------------------------------------------------------------------------------------------------#
                            #-------------------------------------------------------------------------------------------------------------#
                            ]
        
        # Header construction
        header_comp = [item[0] for item in input_format_comp]
        header_met = [item[0] for item in input_format_met]
        header_rivet = [item[0] for item in input_format_rivet]

        rf_min_value_pos = self._rf_manager_filter()

        comp_rf_min_value_pos = rf_min_value_pos[0]
        met_rf_min_value_pos = rf_min_value_pos[1]
        rivet_rf_min_value_pos = rf_min_value_pos[2]

        data_comp = []
        data_met = []
        data_rivet = []

        rf_all_elements = self._rf_analysis_elems

        for key in rf_all_elements:
            
            if key == "COMP_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    row = comp_rf_min_value_pos[i]
                    rf_and_lc = (element.ID, row[0], row[3], row[1], row[4], row[2], row[5])
                    data_comp.append(rf_and_lc)
                    
            if key == "METAL_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    row = met_rf_min_value_pos[i]
                    rf_and_lc = (element.ID, row[0], row[3], row[1], row[4], row[2], row[5])
                    data_met.append(rf_and_lc)

            if key == "1D_ELEMENTS":
                for i,element in enumerate(rf_all_elements[key]):
                    row = rivet_rf_min_value_pos[i]
                    rf_and_lc = (element.ID, row[0], row[3], row[1], row[4], row[2], row[5])
                    data_rivet.append(rf_and_lc)

        try:
            import pandas as pd
            dfr_comp = pd.DataFrame(data_comp, columns=header_comp)
            dfr_met = pd.DataFrame(data_met, columns=header_met)
            dfr_connect = pd.DataFrame(data_rivet, columns=header_rivet)

            path_excel = r"{}\\{}.xlsx".format(self._export_location,"RF_MIN_AND_LC_"+self._export_datatime)

            with pd.ExcelWriter(path_excel) as writer:
                
                dfr_comp.to_excel(writer, sheet_name = "COMP_ELEMENTS", index=False)
                dfr_met.to_excel(writer, sheet_name = "METAL_ELEMENTS", index=False)
                dfr_connect.to_excel(writer, sheet_name = "CONNECTORS_ELEMENTS", index=False)

        except:
            # An Error raised if "Excel" print type is selected but Pandas is not installed
            msg = N2PLog.Error.E906()
    #-------------------------------------------------------------------------------------------------------------------

    def calculate(self):
        """
        Method used to do all the RF calculations and, optionally, export the results. 
        """

        # Only critical errors are displayed on console
        N2PLog.set_console_level("CRITICAL")
        
        # If this method do not receive a N2PGetLoadFastener object, it raises a warning
        if self._get_load_fasteners == None:
            N2PLog.Warning.W900()

        # If the ExportLocation property is not defined, the code stops and raises an Exception
        if self._export_location == None:
            msg = N2PLog.Critical.C904()
            raise Exception(msg)
        
        self._laminate_PT_allow_min_obtention()

        # RF Composite
        # ----------------------------------------------------------------------------------------------- #
        rf_comp = N2PCompRF()
        rf_comp.CompElements = self._rf_analysis_elems["COMP_ELEMENTS"]
        rf_comp.GetLoadFasteners = self._get_load_fasteners
        rf_comp.GetFasteners = self._get_fasteners
        rf_comp.CompShells = self._analysis_comp_props
        rf_comp.RFExportLocation = self._export_location
        rf_comp.calculate()
        echo_data_comp = rf_comp.CalculationInputEcho

        # A list containing all the composite elements ids is created for N2PRivetRF class
        composite_elements_list = [key for key in self._rf_analysis_elems["COMP_ELEMENTS"]]
        # ----------------------------------------------------------------------------------------------- #
        
        # RF Metallic
        # ----------------------------------------------------------------------------------------------- #
        rf_metal = N2PMetalRF()
        rf_metal.MetalElements = self._rf_analysis_elems["METAL_ELEMENTS"]
        rf_metal.GetLoadFasteners = self._get_load_fasteners
        rf_metal.GetFasteners = self._get_fasteners
        rf_metal.Shells = self._analysis_metal_props
        rf_metal.RFExportLocation = self._export_location
        rf_metal.calculate()
        echo_data_met = rf_metal.CalculationInputEcho
        # ----------------------------------------------------------------------------------------------- #

        # RF Connectors
        # ----------------------------------------------------------------------------------------------- #
        rf_rivets = N2PRivetRF()
        rf_rivets.RivetElements = self._rf_analysis_elems["1D_ELEMENTS"]
        rf_rivets.GetLoadFasteners = self._get_load_fasteners
        rf_rivets.GetFasteners = self._get_fasteners
        rf_rivets.CompElementsList = composite_elements_list
        rf_rivets.CompRFResults = rf_comp.RFResults
        rf_rivets.calculate()
        echo_data_rivets = rf_rivets.CalculationInputEcho
        # ----------------------------------------------------------------------------------------------- #

        # Dictionary containing all the RF results
        self._rf_results={"COMP_ELEMENTS": rf_comp.RFResults,
                          "METAL_ELEMENTS": rf_metal.RFResults,
                          "1D_ELEMENTS": rf_rivets.RFResults}
        
        # Relevant Errors and Warnings to be shown in console:
        # ---------------------------------------------------#
        # ---------------------------------------------------#
        if self._joints_no_FastenerSystem == True:
            N2PLog.set_console_level("DEBUG")
            N2PLog.Error.E908()

        if self._plates_wrong_property == True:
            N2PLog.set_console_level("DEBUG")
            N2PLog.Warning.W905()

        if self._fasts_wrong_property == True:
            N2PLog.set_console_level("DEBUG")
            N2PLog.Warning.W906()

        if rf_comp._booleans["edge_distance_problems"] == True:
            N2PLog.set_console_level("DEBUG")
            N2PLog.Warning.W907()

        if rf_comp._booleans["shim_problems"] == True:
            N2PLog.set_console_level("DEBUG")
            N2PLog.Error.E909()
            
        if rf_metal._booleans["bru_allow_problems"] == True:
            N2PLog.set_console_level("DEBUG")
            N2PLog.Warning.W908()

        if rf_metal._booleans["a_net_gross_problems"] == True:
            N2PLog.set_console_level("DEBUG")
            N2PLog.Error.E910()
        # ---------------------------------------------------#
        # ---------------------------------------------------#
        N2PLog.set_console_level("CRITICAL")
        
        # Input data echo is written into a CSV file
        data = echo_data_comp + echo_data_met + echo_data_rivets
        self._input_data_echo_to_CSV(data)
        
        # RF values are exported to a HD5F file
        self._export_rf_to_hd5f()
    #-------------------------------------------------------------------------------------------------------------------