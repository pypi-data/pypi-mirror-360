from NaxToPy.Core import N2PModelContent
import pandas as pd
import numpy as np
import json
import csv



class ARAttachment:
    """Class of POC_riveting module containing the list of ARBolts that form the same attachement. An attachement is
    understood as the set of bolts that join the exact same plates.

    Attributes:
        ID: int
        AttachedPlatesIDs: list[ints]
        AttachedPlates: list[ARPlates]
        Bolts: list[ARBolts]
        Pitch: float
        JointsFilejson: str
        PanelsLoadFile: str
        FastenersLoadFile: str

        """

    def __init__(self, id):
        self.ID: int = id
        self.AttachedPlatesIDs: list = None
        self.AttachedPlates: list = None
        self.Bolts: list = []
        self.Pitch: float = None
        self.JointsFilejson: str = None
        self.PanelsLoadFile: str = None
        self.FastenersLoadFile: str = None

        self.serialized: bool = False


    ###################################################################################################################
    ####################################################### FUNCIONES #################################################
    ###################################################################################################################

    def sort(self) -> None:
        '''
        This fuction is a shortcut to sort all bolts in an attachment class.
        '''
        for b in self.Bolts:
            b.sort()

    def get_pitch(self, option = 'min') -> None:
        '''This function fills the pitch in each “ARBolt” considering the bolts in each “ARAttachment” instance.
        Different options will be available, but by now the only existent one is min: the pitch is the minimum distance
        from each bolt to all its neighbours.

        Args:
            option: str (Default value is "min")

        Calling example:

                attachment.get_pitch()

        '''

        intersection_points = []

        # Select the id of the first plate of the first bolt, since bolts might be disordered.
        plate_id = self.Bolts[0].Plates[0].ID
        normal = np.array(self.Bolts[0].Plates[0].Normal)

        # Gets the intersection point coordinates of each bolt for the selected plate
        for bolt in self.Bolts:
            plate = [plate for plate in bolt.Plates if plate.ID == plate_id][0]
            intersection_points.append(np.array(plate.IntersectionPoint))

        # Gets distances between all points
        # distances

        num_points = len(intersection_points)
        distances = np.zeros((num_points, num_points))

        for i in range(num_points):
            for j in range(i + 1, num_points):
                distance = np.linalg.norm(intersection_points[i] - intersection_points[j])
                distances[i, j] = distances[j, i] = distance

        np.fill_diagonal(distances, np.inf)


        # CASE SELECTION
        # MIN: The minimum distance to all neighbors is selected as pitch.
        if option == 'min':
            distances = np.min(distances, axis=0)
            for i, bolt in enumerate(self.Bolts):
                bolt.Pitch = distances[i]
            self.Pitch = np.min(distances)

        # Implement other methods
        else:
            ...

        return self

    def export_joints_json(self, path_file_json: str, analysis_name: str, conection_file: str, propertiesData: list):
        """ Method which takes an attachment and a path file and gives as output a json file with the corresponding data
        for the joints. Each of the files that gives this method is related to only one attachment. If the function is
        called several times, it will continue writing over the same file; unless the file does not exist or another
        path is given.
        
        Args:
            path_file_json: str
            analysis_name: str
            conection_file: str
            propertiesData: list of dataframes with databases (allowables, faasteners properties)

        Returns:
            joints data: json

        Calling example:

                attachment.export_joints_json(path_file_json 0 output_path, analysis_name = analysis_name,
                                              conection_file = conection_file, propertiesData = propertiesData)
        
        """
        data_final = []
        path_file_new_joints_json = "{}\\{}_json_joints_for_attachment_{}.json".format(path_file_json, analysis_name, self.ID)
        self.JointsFilejson = path_file_new_joints_json
        connectionDF = pd.read_csv(conection_file, delimiter=",", on_bad_lines='skip', skiprows=0, low_memory=False)

        # Loop made in each of the joints of the attachment.
        for bolt in self.Bolts:
            name = "Joint {}".format(bolt.ID)
            id = bolt.ID

            # Definition of lists.
            material_type = []
            platesnames = []
            thicknesses = []
            material_properties = []
            allowables_stress_plates = []
            security_Factors_plate = []
            material_properties_final = []
            allowables_stress_plates_final = []
            security_Factors_plate_final = []
            fasteners_geometry = []
            fast_geom_diam_list = []
            fast_geom_diam_head_list = []
            fasteners_names = []

            # Check if the joint is simple or multiple.
            if len(bolt.Elements1D) == 1:
                jointtype = "simple"
            else:
                jointtype = "multiple"
                
            ############################################################ PLATES #####################################################

            for i, plate in enumerate(bolt.Plates):
                platename = "Plate {}".format(plate.ElementIDs[0]) # Name of plate.
                platesnames.append(platename)
                thickness = plate.Elements[0].Property.Thickness # Thickness of plate. If it is a composite, all the layersÂ´ thicknesses will be saved.
                thicknesses.append(thickness)

                # Check if it is a composite or a metal.
                if plate.Elements[0].Property.PropertyType == "PSHELL":
                    mat_type = "metal_{}".format(plate.Elements[0].Material.ID) # Type of material. (metal)

                    # Properties structure:["met_id","Ex[N/mm2]", "vxy"]
                    mat_props = ["Metal {}".format(plate.Elements[0].Material.ID), plate.Elements[0].Material.Young, plate.Elements[0].Material.Poisson] # Material properties.

                    # Allowables stress metal structure: ["Bearing[Mpa]","pull[Mpa]"]
                    try:
                        plateAllows = self.getAllowablesPlates(id, plate.ElementIDs[0], "metal", plate.Elements[0].Material.ID, propertiesData, connectionDF)                    
                        allow_stress_plate = [plateAllows[0], plateAllows[4]] # Allowables stress.
                    except:
                        allow_stress_plate = [np.nan, np.nan]

                    # Security factors metal structure: ["Bearing[-]", "pull[-]", "fitting", "Prying"]
                    sec_factors_plate = [np.nan, np.nan, np.nan, np.nan] # Safety factors.


                elif plate.Elements[0].Property.PropertyType == "PCOMP":
                    layUp = '/'.join(str(round(e)) for e in plate.Elements[0].Property.Theta)
                    thicknesses[i] = sum(thicknesses[i])
                    
                    mat_type = "composite_{}".format(plate.Elements[0].Material.ID) # Type of material. (composite)

                    # Properties structure: [ "Lam_id", "layup", "layers", "Ex[N/mm2]", "Ey[N/mm2]","Gxy[N/mm2]", "vxy", "vyx", "D11[Nmm]","D22[Nmm]","D12[Nmm]","D66[Nmm]" ]
                    mat_props = ["Laminate {}".format(plate.Elements[0].Material.ID), layUp, plate.Elements[0].Property.NumPiles, plate.Elements[0].Material.YoungX, \
                        plate.Elements[0].Material.YoungY, plate.Elements[0].Material.ShearXY, plate.Elements[0].Material.PoissonXY, plate.Elements[0].Material.PoissonXY,  plate.Elements[0].Property.EqQMatrix[0][0], \
                        plate.Elements[0].Property.EqQMatrix[1][1],  plate.Elements[0].Property.EqQMatrix[0][1],  plate.Elements[0].Property.EqQMatrix[2][2]] # Material properties.

                    # Allowables stress composite structure: ["Bearing[Mpa]", "OHT[Mpa]", "OHC[Mpa]",	"ILSS[Mpa]"]
                    try:
                        plateAllows = self.getAllowablesPlates(id, plate.ElementIDs[0], "composite", plate.Elements[0].Material.ID, propertiesData, connectionDF, layUp)
                        allow_stress_plate = [plateAllows[0], plateAllows[1], plateAllows[2], np.nan, plateAllows[4]] # Allowables stress.
                    except:
                        allow_stress_plate = [np.nan, np.nan, np.nan, np.nan, np.nan]

                    # Security factors composite structure: ["Bearing[Mpa]", "OHT[Mpa]", "OHC[Mpa]", "ILSS[Mpa]", "fitting", "Prying"]
                    sec_factors_plate = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan] # Safety factors.

                material_type.append(mat_type)
                material_properties.append(mat_props)
                allowables_stress_plates.append(allow_stress_plate)
                security_Factors_plate.append(sec_factors_plate)
                material_properties_dict = (material_type[i], material_properties[i])
                allowables_stress_plates_dict = (material_type[i], allowables_stress_plates[i])
                security_Factors_plate_dict = (material_type[i], security_Factors_plate[i])
                
                material_properties_final.append(material_properties_dict)
                allowables_stress_plates_final.append(allowables_stress_plates_dict)
                security_Factors_plate_final.append(security_Factors_plate_dict)

            material_properties = {name: properties for name, properties in material_properties_final}
            allowables_stress = {name: properties for name, properties in allowables_stress_plates_final}
            security_factors = {name: properties for name, properties in security_Factors_plate_final}

            ############################################################ FASTENERS #####################################################

            for element1D in bolt.Elements1D:
                fastener_name = "Fastener {}".format(element1D.ID) # Fastener name.
                fasteners_names.append(fastener_name)

                fast_geom_diam = element1D.Property.D # Fastener diameter.
                fast_geom_diam_list.append(fast_geom_diam)
                fast_geom_diam_head = np.nan  # Fastener head diameter.
                fast_geom_diam_head_list.append(fast_geom_diam_head)

                # Allowables stress structure: ["shear[Mpa]", "tension[Mpa]"]
                try:
                    allowables_stress_fast =  self.getAllowablesFasteners(self, bolt.Nut, bolt.Designation, propertiesData[2])
                    type_fast =  [bolt.Type, bolt.Nut] # Type of fastener.
                except: 
                    allowables_stress_fast = [np.nan, np.nan]
                    type_fast = [np.nan, np.nan]

                # Security factors structure: ["shear", "tension", "fitting", "prying"]
                security_Factors_fast = [np.nan, np.nan, np.nan, np.nan] # Safety factors.

            fasteners_geometry = {
                "diameters[mm]": fast_geom_diam_list,
                "diam_head[mm]": fast_geom_diam_head_list
            }
            ################################################# DEFINITION OF JSON STRUCTURE ############################################

            json_data = {
                "name": name,
                "id": id,
                "type": jointtype,
                "plates": {
                    "plates_names": platesnames,
                    "thickness[mm]": thicknesses,
                    "material_type": material_type,
                    "material_properties": material_properties,
                    "allowables_stress": allowables_stress,
                    "security_factors": security_factors
                },
                "fasteners":{
                    "fasteners_names": fasteners_names,
                    "fasteners_geometry": fasteners_geometry,
                    "allowables_stress": allowables_stress_fast,
                    "type":type_fast,
                    "security_factors": security_Factors_fast
                }
            }
            data_final.append(json_data)
        data = {"joints": data_final}

        # Write in the json file.
        with open(path_file_new_joints_json, 'a+') as file:            
            json.dump(data, file, indent=4)

    def export_forces_csv(self, path_file_Outputs: str, analysis_name: str, results: dict ) -> None:
        """Method which takes an ARBolt element and a directory path in order to export the corresponding data for
        forces and bypasses in the fasteners and plates in two .csv files. The output is defined by two different csvs
        files: one for fasteners and one for plates. The csv file is created in the path file if it does not exist, and
        the new information is added if the csv file already exists. The data exported in the fasteners file is defined
        in Element Reference Frame, whereas the data in the plates file is defined in Material Reference Frame.

        Args:
            path_file_Outputs: str
            analysis_name: str
            results: dict
            
        Returns:
            fastener forces: csv
            plates forces: csv

        Calling example:

                attachment.export_forces_csv(path_file_Outputs = output_path, analysis_name = analysis_name, results = results)

        """
            
        ####################################################### FASTENERS CSV CREATION ###################################################

        # ELEMENT REFERENCE FRAME

        path_file_new_fasteners = "{}\\{}_fasteners_for_attachment_{}.csv".format(path_file_Outputs, analysis_name, self.ID)

        self.FastenersLoadFile = path_file_new_fasteners

        # Definition of the top headline of the csv file.
        headline_fast = ["Joint ID", "CFAST_ID", "Load_case_ID", "Load_case_Name", "Fz [N]", "Shear [N]"]

        with open(path_file_new_fasteners, 'a+', newline='') as file_csv_fast: 

            writer_csv_fast = csv.writer(file_csv_fast)

            if file_csv_fast.tell() == 0: # If the file is non-existent, the headline is written; if it already exists, if keeps adding the new bolts studied.
                writer_csv_fast.writerow(headline_fast)

            for bolt in self.Bolts:

                for fastener in bolt.Elements1D:
                    for lc_id, result in results.items():
                        lc_name = result.get("Name")
                        Fz_max_bolt = bolt.FZmax[lc_id]
                        Fshear_fast = fastener.F_shear[lc_id]

                        data = ["Joint {}".format(bolt.ID), fastener.ID, lc_id, lc_name, Fz_max_bolt, Fshear_fast]
                        writer_csv_fast.writerow(data)

        ####################################################### PLATES CSV CREATION ###################################################

        # MATERIAL REFERENCE FRAME

        path_file_new_plates = "{}\\{}_plates_for_attachment_{}.csv".format(path_file_Outputs, analysis_name, self.ID)

        self.PanelsLoadFile = path_file_new_plates

        headline_plates = ["Joint ID", "Panel_ID", "CFAST_ID", "Load_case_ID", "Load_case_Name", "Bearing [N]", "BypassMaxPpal [N/mm]", "BypassMinPpal [N/mm]", "Load Angle [deg]", "Distance to Edge"]

        with open(path_file_new_plates, 'a+', newline='') as file_csv_plates: 

            writer_csv_plates = csv.writer(file_csv_plates)

            if file_csv_plates.tell() == 0: # If the file is non-existent, the headline is written, if it already exists, if keeps adding the new bolts studied.
                writer_csv_plates.writerow(headline_plates)
                
            for bolt in self.Bolts:
                for element1d in bolt.Elements1D:
                    ### TOP PLATE
                    top_plate = [plate for plate in bolt.Plates if plate.ID == element1d.TopPlateID][0]

                    for lc_id, result in results.items():
                            data = ["Joint {}".format(bolt.ID),
                                    top_plate.ElementIDs[0],
                                    element1d.ID,
                                    lc_id,
                                    result.get("Name"),
                                    element1d.F_shear[lc_id],
                                    top_plate.BypassMaxPpal[lc_id],
                                    top_plate.BypassMinPpal[lc_id],
                                    element1d.LoadAngle[lc_id],
                                    top_plate.DistanceToEdge]
                            writer_csv_plates.writerow(data)

                    ### BOTTOM PLATE
                    bottom_plate = [plate for plate in bolt.Plates if plate.ID == element1d.BottomPlateID][0]

                    for lc_id, result in results.items():
                            data = ["Joint {}".format(bolt.ID),
                                    bottom_plate.ElementIDs[0],
                                    element1d.ID,
                                    lc_id,
                                    result.get("Name"),
                                    element1d.F_shear[lc_id],
                                    bottom_plate.BypassMaxPpal[lc_id],
                                    bottom_plate.BypassMinPpal[lc_id],
                                    element1d.LoadAngle[lc_id],
                                    bottom_plate.DistanceToEdge]
                            writer_csv_plates.writerow(data)

    def export_attachments_json(self, path_file_json: str, analysis_type: str, analysis_name: str):
        """ Method which takes an attachment and a path file and gives as output a json file with the corresponding data
        for the attachment. If the function is called several times, it will continue writing over the same file;
        unless the file does not exist or another path is given.
        
        Args:
            path_file_json: str
            analysis_type: str
            analysis_name: str

        Returns:
            attachment data: json

        Calling example:

                attachment.export_attachments_json(path_file_json = output_path, analysis_type = analysis_type, analysis_name = analysis_nameº)
        
        """

        data_final = []
        # Definition of variables
        name = "attachment_{}".format(self.ID)
        joints_file = self.JointsFilejson
        panels_load_file = self.PanelsLoadFile
        fasteners_load_file = self.FastenersLoadFile
        pitch = self.Pitch

        path_file_new = "{}\\{}_json_attachments.json".format(path_file_json, analysis_name)

        ################################################# DEFINITION OF JSON STRUCTURE ############################################

        json_data = {
                "name": name,
                "joints_file": joints_file,
                "analysis_type": analysis_type,
                "panels_load_file": panels_load_file,
                "fasteners_load_file": fasteners_load_file,
                "pitch": pitch
        }

        data_final.append(json_data)
        data = {"attachments": data_final}

        # Write in the json file.
        with open(path_file_new, 'a+') as file:            
            json.dump(data, file, indent=4)

    def serialize(self):
        '''
        Serialize method substitutes all N2P objects by integer or tuple IDs so that ARAttachment can be serialized by pickle.
        ARBolt and ARPlate serialize methods all called.

        Returns: self
        '''
        if not self.serialized:
            for bolt in self.Bolts:
                bolt.serialize()

            for plate in self.AttachedPlates:
                plate.serialize()

            self.serialized = True

        return self

    def deserialize(self, model: N2PModelContent):
        '''
        Deserialize method rebuilds ARAttachment using the model and the IDs left by the serialize method.
        ARBolt and ARPlate deserialize methods all called.

        Returns: self
        '''
        if self.serialized:
            for bolt in self.Bolts:
                bolt.deserialize(model)

            for plate in self.AttachedPlates:
                plate.deserialize(model)

            self.serialized = False

        return self

    def get_CriticalLoads(self, fastID, panelID=' '):
        """
        This function calculates the critical loads for a given fastener and panel, if provided.

        Args:
            fastID: ID of the fastener
            panelID: ID of the panel, default is empty string
        Returns:
            List containing the maximum tension, maximum bearing, maximum bypass, maximum principal,
            maximum bypass minimum principal, maximum shear, and bearing angle.
        """
       
        lcMaxTension = []; lcMaxBearing = []; lcMaxBypassMaxPpal = []; lcMaxBypassMinPpal = []; lcMaxShear = []; 
        MaxTension = []; MaxBearing = []; MaxBypassMaxPpal = []; MaxBypassMinPpal = []; MaxShear = []; bearingAngle = []
        thlc_names = ["ROOM", "COLD", "HOT"]
              
        fast_Loads = pd.read_csv(self.FastenersLoadFile, delimiter=",", on_bad_lines='skip', low_memory=False)   
        
        for i, thlc in enumerate(thlc_names):
            try:
                MaxTension.append(max(fast_Loads[(fast_Loads["CFAST_ID"] == fastID) & (thlc in fast_Loads["Load_case_Name]"] )].iloc[:,4]) + 0.01)
                lcMaxTension.append(fast_Loads[(fast_Loads["CFAST_ID"] == fastID) & (fast_Loads["Fz [N]"] == (MaxTension[i] - 0.01))].iloc[0,3])
                MaxShear.append(max(fast_Loads[(fast_Loads["CFAST_ID"] == fastID)& (thlc in fast_Loads["Load_case_Name]"] )].iloc[:,5]) + 0.01) 
                lcMaxShear.append(fast_Loads[(fast_Loads["CFAST_ID"] == fastID) & (fast_Loads["Shear [N]"] == (MaxShear[i] - 0.01))].iloc[0,3])  
            except:
                MaxTension.append(max(fast_Loads[(fast_Loads["CFAST_ID"] == fastID)].iloc[:,4]) + 0.01)
                lcMaxTension.append(fast_Loads[(fast_Loads["CFAST_ID"] == fastID) & (fast_Loads["Fz [N]"] == (MaxTension[i] - 0.01))].iloc[0,3])
                MaxShear.append(max(fast_Loads[(fast_Loads["CFAST_ID"] == fastID)].iloc[:,5]) + 0.01)
                lcMaxShear.append(fast_Loads[(fast_Loads["CFAST_ID"] == fastID) & (fast_Loads["Shear [N]"] == (MaxShear[i] - 0.01))].iloc[0,3]) 
                              
        if  panelID != ' ':
            plates_Loads = pd.read_csv(self.PanelsLoadFile, delimiter=",", on_bad_lines='skip', skiprows=0, low_memory=False)
            for i, thlc in enumerate(thlc_names):
                try:    
                    MaxBearing.append(max(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Panel_ID"] == panelID) & (thlc in plates_Loads["Load_case_Name]"] )].iloc[:,5]) + 0.01)
                    lcMaxBearing.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["BypassMinPpal [N/mm]"] == (MaxBearing[i] - 0.01))].iloc[0,4])              
                    MaxBypassMaxPpal.append(max(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Panel_ID"] == panelID) & (thlc in plates_Loads["Load_case_Name]"] )].iloc[:,6]) + 0.01)
                    lcMaxBypassMaxPpal.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["BypassMaxPpal [N/mm]"] == (MaxBypassMaxPpal[i]-0.01))].iloc[0,2])
                    MaxBypassMinPpal.append(min(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Panel_ID"] == panelID) & (thlc in plates_Loads["Load_case_Name]"] )].iloc[:,7]) - 0.01)
                    lcMaxBypassMinPpal.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["BypassMinPpal [N/mm]"] == (MaxBypassMinPpal[i] + 0.01))].iloc[0,2])
                    bearingAngle.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["BypassMinPpal [N/mm]"] == (MaxBearing[i] - 0.01))].iloc[0,8])
                except:
                    MaxBearing.append(max(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Panel_ID"] == panelID) ].iloc[:,5]) + 0.01)
                    lcMaxBearing.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Bearing [N]"] == (MaxBearing[i] - 0.01))].iloc[0,4])              
                    MaxBypassMaxPpal.append(max(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Panel_ID"] == panelID) ].iloc[:,6]) + 0.01)
                    lcMaxBypassMaxPpal.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["BypassMaxPpal [N/mm]"] == (MaxBypassMaxPpal[i]-0.01))].iloc[0,2])
                    MaxBypassMinPpal.append(min(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Panel_ID"] == panelID) ].iloc[:,7]) - 0.01)
                    lcMaxBypassMinPpal.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["BypassMinPpal [N/mm]"] == (MaxBypassMinPpal[i] + 0.01))].iloc[0,2])
                    bearingAngle.append(plates_Loads[(plates_Loads["CFAST_ID"] == fastID) & (plates_Loads["Bearing [N]"] == (MaxBearing[i] - 0.01))].iloc[0,8])
                                
        return [MaxTension , MaxBearing , MaxBypassMaxPpal , MaxBypassMinPpal , MaxShear , bearingAngle]
                 
    def get_metal_allow(self, database, mat_ID):
        """
        Get metal allowables from the database based on the material ID.

        Args:
            database: The database containing metal allowables
            mat_ID: The material ID to look up

        Returns:
         A list containing the fsu and fbu values for the specified material ID
        """
        try:
            metal = database.groupby(['ID [-]']).get_group((mat_ID))
            fsu_room = metal[metal["Temperture [-]"] == "ROOM"].iloc[:,10].values[0]
            fbu_room = metal[metal["Temperture [-]"] == "ROOM"].iloc[:,11].values[0]
            fsu_cold = metal[metal["Temperture [-]"] == "COLD"].iloc[:,10].values[0]
            fbu_cold = metal[metal["Temperture [-]"] == "COLD"].iloc[:,11].values[0]
            fsu_hot = metal[metal["Temperture [-]"] == "HOT"].iloc[:,10].values[0]
            fbu_hot = metal[metal["Temperture [-]"] == "HOT"].iloc[:,11].values[0]
            fsu = [fsu_room, fsu_cold, fsu_hot]
            fbu = [fbu_room, fbu_cold, fbu_hot]
        except:
            msg = ["material " , mat_ID ,  " doesn't found in metal allowables database"]
            print("\n".join(msg))
        return [fsu, fbu]
   
    def get_composite_allow(self, database, lam_ID, layup, orientation):
        """
        A function to calculate the composite allowables based on the given parameters.

        Args:
            self: the object itself
            database: the database containing the laminate properties
            lam_ID: the ID of the laminate
            layup: the layup configuration of the laminate
            orientation: the orientation of the laminate

        Returns:
            comp_allow: a list containing the composite allowables for bearing, OHT, OHC, ir_buck, and pull_through
        """

        lam_props = []
        layup_SL = layup.replace("45","99").replace("0","45").replace("99","0")
        limite_inferior = -22.5
        orient = ""
        temp_order = ["ROOM","COLD","HOT"]

        # 288 Lam type calculator
        n0 = layup.count("0")
        n_45 = layup.count(r"-45")
        n45 = layup.count(r"45")-n_45
        n90 = layup.count("90")
        total_plies = layup.count("/")+1

        # 288 The value provided by Lilium Tool is 0.25 but this is for Fabric, for UD Tape 0.5 is used because 0 and 90 plies are combined
        if round(n0/total_plies,2)==0.5: lam_type = "QI"
        if round(n0/total_plies,2)>0.5: lam_type = "HL"
        if round(n0/total_plies,2)<0.5: lam_type = "SL"

        try:
            for lam in database.itertuples():
                if (lam[1] == lam_ID) and (lam[2]==layup or lam[2]==layup_SL):
                    lam_props.append(lam)
            lam_props_DF = pd.DataFrame(lam_props)
            if lam_props_DF.shape[0] == 0 and lam_props_DF.shape[1] == 0:
                msg = ["Laminate" , lam_ID ,"with layup",layup,  "was not found in StrainAllowable database"]
                print(" ".join(msg))
                return [["nan","nan","nan"],["nan","nan","nan"],["nan","nan","nan"],["nan","nan","nan"]]
        except:
            msg = ["Laminate " , lam_ID ,"with layup ",layup,  " was not found in StrainAllowable database"]
            print("\n".join(msg))
            return [["nan","nan","nan"],["nan","nan","nan"],["nan","nan","nan"],["nan","nan","nan"]]

        # Reorder of the dataframe as: ROOM, COLD, HOT--------------------------------------------------------
        # For general allowable 288
        temp_index = lam_props_DF['_4'].str.split('_').str[0]
        lam_props_DF['_4'] = temp_index
        lam_props_DF = lam_props_DF.iloc[pd.Categorical(lam_props_DF["_4"],temp_order).argsort()]    # If changing the order is desired just modify this vector
        
        # For bearing allowable
        if lam_type != "QI": bearing_props_DF = lam_props_DF

        # Dropdown by orientation and temperature ----------------------------------------------------------------------------
        if lam_type == "QI":
            pass
        else:
            for i,temp in enumerate(temp_order): # This is made assuming that the orientation list is for LC in ROOM, COLD, HOT
                theta = orientation[i]
                cuadrante = (theta - limite_inferior) / 45
                # Only for bearing allowable
                if int(cuadrante)%2 == 0:
                    print("Original laminate properties used for bearing if there is no UD Tape: "+ lam_type + " for temperature "+temp)
                    lam_props_DF = lam_props_DF.drop(lam_props_DF[(lam_props_DF._5 !=lam_type) & (lam_props_DF._4 ==temp)].index)
                    bearing_props_DF = bearing_props_DF.drop(bearing_props_DF[(bearing_props_DF._5 !=lam_type) & (bearing_props_DF._4 ==temp)].index)
                else:
                    if lam_type == "HL": orient = "SL"
                    if lam_type == "SL": orient = "HL"
                    
                    print("Alternative properties used for bearing if there is no UD Tape: " + orient+ " for temperature "+temp)
                    bearing_props_DF = bearing_props_DF.drop(bearing_props_DF[(bearing_props_DF._5 !=orient) & (bearing_props_DF._4 ==temp)].index)
                    lam_props_DF = lam_props_DF.drop(lam_props_DF[(lam_props_DF._5 ==orient) & (lam_props_DF._4 ==temp)].index)    

        
        # Allowables selection based on configuration --------------------------------------------------------

        if ("Tape" or "tape") in lam_props_DF.iloc[0,3]:
            print("The laminate used includes Tape plies, allowable rotation using load angle will not be used")
            bearing_allow = lam_props_DF.iloc[:,9].to_list()
        else:
            if orient =="": bearing_allow = lam_props_DF.iloc[:,9].to_list()
            else: bearing_allow = bearing_props_DF.iloc[:,9].to_list()

        OHT_allow = lam_props_DF.iloc[:,6].to_list()                                       # OHT [10e-6]
        OHC_allow = lam_props_DF.iloc[:,7].to_list()                                       # OHC [10e-6]
        ir_buck_allow = ["nan","nan","nan"]             
        pull_through_allow = lam_props_DF.iloc[:,10].to_list()                              # ILSS [Mpa]

        if (len(bearing_allow) or len(OHT_allow)) >3: print("There might be some laminate duplicated on the database... \
            please make sure that the laminate ID is only repeated for the soft layup and not for another laminate")

        # Values selection -----------------------------------------------------------------------------------
        # Remember IrBuckAllow is NaN and PullThrougAllow is ILSS 288
        comp_allow = [bearing_allow,OHT_allow,OHC_allow,ir_buck_allow,pull_through_allow]
        return comp_allow
    
    def getAllowablesPlates(self, fastID, panelID, mat, propID, propertiesData, connectionDF, layup=''):
        """
        Calculate the allowables of plates for a given fastener, panel, material, and properties.

        Args:
            self: The object itself.
            fastID (int): The fastener ID.
            panelID (int): The panel ID.
            mat (str): The material type ('composite' or 'metal').
            propID (int): The properties ID.
            propertiesData (list): List of properties data.
            connectionDF (pandas.DataFrame): The connection dataframe.
            layup (str, optional): The layup parameter. Defaults to ''.

        Returns:
            list: A list of allowable plate values including bearing, OHT, OHC, IRBuck, and PullThrough.
        """
        
        bearingAllowPlate = np.nan; OHTAllowPlate = np.nan; OHCAllowPlate= np.nan; IRBuckAllowPlate= np.nan; PullThroughAllowPlate = np.nan
        try:
            # critical load cases 
            lcBearing = self.get_CriticalLoads(fastID, panelID)[1]
            lcpullTrough = self.get_CriticalLoads(fastID, panelID)[0]
            lcOHT = self.get_CriticalLoads(fastID, panelID)[2]
            lcOHC = self.get_CriticalLoads(fastID, panelID)[3]
            orientation = self.get_CriticalLoads(fastID, panelID)[5]

            # material allowables for all temperatures
            if mat == 'composite' :     
                lam_ID = self.getLaminateId(propID, connectionDF)           
                compAllow = self.get_composite_allow(propertiesData[0], lam_ID, layup, orientation)              
                bearingAllow = compAllow[0]
                OHTAllow = compAllow[1]
                OHCAllow = compAllow[2]
                PullThroughAllow = compAllow[4]
                # choosing worse ratio
                bearingAllowPlate = bearingAllow[np.argmin([i / j for i, j in zip(bearingAllow, lcBearing)])]
                orientation = orientation[np.argmin([i / j for i, j in zip(bearingAllow, lcBearing)])]
                OHTAllowPlate = OHTAllow[np.argmin([i / j for i, j in zip(OHTAllow,lcOHT)])]
                OHCAllowPlate = OHCAllow[np.argmin([i / j for i, j in zip(OHCAllow,lcOHC)])]
                PullThroughAllowPlate = PullThroughAllow[np.argmin([i / j for i, j in zip(PullThroughAllow, lcpullTrough)])]
                            
            elif mat == 'metal':
                metal_ID = self.getLaminateId(propID, connectionDF)
                metAllow = self.get_metal_allow(propertiesData[1], metal_ID)                 
                bearingAllow = metAllow[1]
                PullThroughAllow = metAllow[0]
                # choosing worse ratio
                bearingAllowPlate = bearingAllow[np.argmin([i / j for i, j in zip(bearingAllow, lcBearing)])]
                OHTAllowPlate = "---"
                OHCAllowPlate = "---"
                PullThroughAllowPlate = PullThroughAllow[np.argmin([i / j for i, j in zip(PullThroughAllow, lcpullTrough)])]
        except:
            msg = "No allowables values will be written in joints file for plate" + panelID
            print(msg)
            return [bearingAllowPlate, OHTAllowPlate, OHCAllowPlate, IRBuckAllowPlate, PullThroughAllowPlate]
    
        return [bearingAllowPlate, OHTAllowPlate, OHCAllowPlate, IRBuckAllowPlate, PullThroughAllowPlate]

    def getAllowablesFasteners(self, type, designation, database):
        """
        Get the allowable fasteners based on the type and designation from the provided database.

        Parameters:
            type (str): The type of the fastener.
            designation (str): The designation of the fastener.
            database (pd.DataFrame): The database containing fastener information.

        Returns:
            list: A list containing the shear and tension allowable values for the specified fastener.
        """
        shearAllow = np.nan; TensionAllow = np.nan
        try:
            fast = database.groupby(['Type','Designation']).get_group((type,designation))
            shearAllow = fast['FSS[N]']
            TensionAllow = fast['FTS_b[N]']
        except:
            msg = "fastener " + designation + " " +  type +  " doesn't found in fasteners allowables database"
            print(msg)
            return [shearAllow, TensionAllow]
        return [shearAllow, TensionAllow]

    def getLaminateId(self, panelID, database):
        """
        This function takes in the panel ID and a database, and retrieves the material ID associated with the panel ID from the database.

        Args:
            panelID (str): The panel ID to look up in the database.
            database (DataFrame): The database containing the material IDs.

        Returns:
            str: The material ID associated with the panel ID.
        """
        materialId = ''
        try:
            connection = database.groupby(['Material ID']).get_group((panelID))
            materialId = connection['Material ID (ddbb)']._values[0]
        except:
            msg = "plate material id " + panelID ,  " doesn't found in material connection input file"
            print(msg)
            return materialId

        return materialId
