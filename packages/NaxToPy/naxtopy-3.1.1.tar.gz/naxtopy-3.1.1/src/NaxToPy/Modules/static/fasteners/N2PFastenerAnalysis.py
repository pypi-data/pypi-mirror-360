from time import time
import sys

from NaxToPy.Core.N2PModelContent import N2PModelContent
from ._N2PFastenerAnalysisDeprecated.Core.Classes.ARBolt import ARBolt
from ._N2PFastenerAnalysisDeprecated.Core.Functions.ARGetBolts import get_bolts
from ._N2PFastenerAnalysisDeprecated.Core.Functions.ARResults import get_results
from ._N2PFastenerAnalysisDeprecated.Core.Functions.ARGetAttachments import get_attachments
from NaxToPy.Core.Errors.N2PLog import N2PLog


class N2PFastenerAnalysis:
    """
    This class provides information about fasteners in a model and provides methods to calculate the corresponding forces
    in the fasteners themselves and bypass forces in the plates they are connected to. The only input in order to be able
    to construct the class is a model defined as a N2PModelContent object.

    Attributes:
        Model: N2PModelContent (Compulsory Input)
        ListBolts: list
        ListAttachments: list
        Bolt_Ids_List: list
        Element1D_Ids_List: list
        CornerData: bool (Default = False) Must eb defined True by the user if wanted.
        LC_Ids_List: list
        __BypassParameters: list (Default = [[2.5], [4.0, 4.5], [1e-3]] which is [area factor, material factor, box tolerance])
        __Results: dict

    All the procedure that can be carried out in two different ways are described below:

        Example 1: calling the methods separately.

        >>> import NaxToPy as n2p
        >>> model1 = n2p.load_model(route_fem)  # Reading of the model.
        >>> fast1 = N2PFastenerAnalysis(model1) # Creation of the N2PFastenerAnalysis object.
        >>> fast1.get_results_fasteners() # Obtaining the results from the model.
        >>> fast1.get_model_fasteners(diameter = 4.8) # Obtaining the fasteners from the model.
        >>> fast1.get_analysis_fasteners(analysis_name="TEST", export_location = path) # Analysing the fasteners.
        >>> fast1.get_attachments_fasteners() # Obtaining the attachments from the model.

        Example 2: Using the method "calculate()".

        >>> import NaxToPy as n2p
        >>> model1 = n2p.load_model(route_fem)  # Reading of the model.
        >>> fast2 = N2PFastenerAnalysis(model1) # Creation of the N2PFastenerAnalysis object.
        >>> fast2.calculate(analysis_name = 'Test', export_location = path, diameter = 4.8) # Call to the method "calculate()".


    Comments:

    There are some other methods in the classes ARBolt and ARAttachment that are not used in this class. In a similar way,
    there are other functions that can be used in order to facilitate the use of this class and its methods.

    The most important ones are:

        Serialize and deserialize. Function "serialize()" serializes a list of “ARBolt” or “ARAttachment” and dumps the data
        into a file. This file will be a .pkl with all the stored data. It is important to recognize that serialize must
        only be used at the end of the script. Objects in memory may change when serialize is called, even if they are
        not directly passed to the function. Thus, when using this function, only the most important data of each of the
        objects is stored, and leaving everything as a function of the elements, properties and materials IDs. When it is
        wanted to continue the analysis with a serialized file of bolts, it is important to deserialize at first.

            Example:

                >>> serial_location = r"C:\EXPORTS\serialized.pkl" # Path to the .pkl file
                >>> serialize(self.ListBolts, serial_location) # Serializing the list of bolts
                >>> self.ListBolts = deserialize(serial_location) # Deserializing the list of bolts


        Getting derived load cases. Function "get_derived_loadcases()" stores in a list the resultant derived loadcases
        IDs. The user must define the load cases that are set to be combined with the rest of the loadcases of the model.
        If this input list of IDs is empty: either the function will either not have an output or it will calculate the
        proportional cases to the ones in the model. Useful to use when wanting only to analyse the derived load cases.
        Can be used to fill the attribute "LC_Ids_List".

            Example:

                >>> derived_loadcases_ids = get_derived_loadcases(model = model1, loadcases_names= ["LC1", "LC2"],
                >>>                                               derived_type = "Derived" , derived_factors = [1.5, 1.0])
                >>> self.LC_Ids_List = derived_loadcases_ids

    """
    def __init__(self, model: N2PModelContent):
        """ N2PFastenerAnalysis Constructor. This class provides information about fasteners in a model and provides methods to calculate the corresponding forces
        in the fasteners themselves and bypass forces in the plates they are connected to. The only input in order to be able
        to construct the class is a model defined as a N2PModelContent object.

        Attributes:
            Model: N2PModelContent (Compulsory Input)
            ListBolts: list
            ListAttachments: list
            Bolt_Ids_List: list
            Element1D_Ids_List: list
            CornerData: bool (Default = False) Must eb defined True by the user if wanted.
            LC_Ids_List: list
            __BypassParameters: list (Default = [[2.5], [4.0, 4.5], [1e-3]] which is [area factor, material factor, box tolerance])
            __Results: dict

        All the procedure that can be carried out in two different ways are described below:

            Example 1: calling the methods separately.

            >>> import NaxToPy as n2p
            >>> model1 = n2p.load_model(route_fem)  # Reading of the model.
            >>> fast1 = N2PFastenerAnalysis(model1) # Creation of the N2PFastenerAnalysis object.
            >>> fast1.get_results_fasteners() # Obtaining the results from the model.
            >>> fast1.get_model_fasteners(diameter = 4.8) # Obtaining the fasteners from the model.
            >>> fast1.get_analysis_fasteners(analysis_name="TEST", export_location = path) # Analysing the fasteners.
            >>> fast1.get_attachments_fasteners() # Obtaining the attachments from the model.

            Example 2: Using the method "calculate()".

            >>> import NaxToPy as n2p
            >>> model1 = n2p.load_model(route_fem)  # Reading of the model.
            >>> fast2 = N2PFastenerAnalysis(model1) # Creation of the N2PFastenerAnalysis object.
            >>> fast2.calculate(analysis_name = 'Test', export_location = path, diameter = 4.8) # Call to the method "calculate()".


        Comments:

        There are some other methods in the classes ARBolt and ARAttachment that are not used in this class. In a similar way,
        there are other functions that can be used in order to facilitate the use of this class and its methods.

        The most important ones are:

            Serialize and deserialize. Function "serialize()" serializes a list of “ARBolt” or “ARAttachment” and dumps the data
            into a file. This file will be a .pkl with all the stored data. It is important to recognize that serialize must
            only be used at the end of the script. Objects in memory may change when serialize is called, even if they are
            not directly passed to the function. Thus, when using this function, only the most important data of each of the
            objects is stored, and leaving everything as a function of the elements, properties and materials IDs. When it is
            wanted to continue the analysis with a serialized file of bolts, it is important to deserialize at first.

                Example:

                    >>> serial_location = r"C:\EXPORTS\serialized.pkl" # Path to the .pkl file
                    >>> serialize(self.ListBolts, serial_location) # Serializing the list of bolts
                    >>> self.ListBolts = deserialize(serial_location) # Deserializing the list of bolts


            Getting derived load cases. Function "get_derived_loadcases()" stores in a list the resultant derived loadcases
            IDs. The user must define the load cases that are set to be combined with the rest of the loadcases of the model.
            If this input list of IDs is empty: either the function will either not have an output or it will calculate the
            proportional cases to the ones in the model. Useful to use when wanting only to analyse the derived load cases.
            Can be used to fill the attribute "LC_Ids_List".

                Example:

                    >>> derived_loadcases_ids = get_derived_loadcases(model = model1, loadcases_names= ["LC1", "LC2"],
                    >>>                                               derived_type = "Derived" , derived_factors = [1.5, 1.0])
                    >>> self.LC_Ids_List = derived_loadcases_ids

        """

        N2PLog.Warning.W110("N2PFastenerAnalysis", "N2PGetFasteners")

        self.Model: N2PModelContent = model
        self.ListBolts: list = []
        self.ListAttachments: list = []
        self.Bolt_Ids_List: list = []
        self.Element1D_Ids_List: list = []
        self.CornerData: bool = False
        self.LC_Ids_List: list = []
        self.__BypassParameters: list = [[2.5], [4.0, 4.5], [1e-3]]
        self.__Results: dict = {}

    ##################################################################################################
    ####################################### CLASS METHODS ############################################
    ##################################################################################################
    def get_results_fasteners(self):
        """
        Method of N2PFastenerAnalysis which obtains the results from the model. This is done only once per model in
        order to save time.

        The steps are the following:

        1. The list of loadcases in the model is obtained. The list of loadcases is defined as an attribute of the
        N2PFastenerAnalysis class. If this list is not defined, all the loadcases will be analysed.

        2. Function "get_results(model, loadcase, corner_data)" which obtains the results from the model. The model is
        defined as a N2PFastenerAnalysis attribute and it is a N2PModelContent object. The loadcase is defined as a list
        of loadcases to be analysed and as a N2PFastenerAnalysis attribute. The corner data is defined as an attribute
        of the N2PFastenerAnalysis class.

        Calling example:

                        fastener.get_results_fasteners()

        Comments:

        Important to know that the load cases are directly obtained from the N2PModelContent object. Therefore, if some
        study of derived load cases is wanted, these load cases must be obtained before calling this function.

        The fact of having corner data as True, makes the results to be more precise; nonetheless, the running time will
        be higher as well.

        When a great amount of result files has been loaded (a folder full of op2 files), the result retrieving may take
        some time. Therefore, it is recommended to get the results once and serialize the obtained dictionary when the
        same model will be used for different analysis.

            -	In order to serialize the dictionary into a file, package pickle can be used, using the following code
                lines. Where “serialized_file_location” is the path where the file will be saved (must be a pkl file as:
                "C:\\results.pkl") and “self.__Results” is the results dictionary obtained.

                                    with open(serialized_file_location, 'wb') as f):
                                        pickle.dump(self.__Results, f)

            -	In order to deserialize the file once it was created in a previous analysis, a similar procedure is
                followed. Now, in a new study, there will not be a reason for using the function “get_results_fasteners”,
                as it is possible to directly obtain the same dictionary from the .pkl file using the following code lines.
                As previously mentioned, “serialized_file_location” will be the path where the dictionary was serialized
                before (a .pkl file), and “self.__Results” is the dictionary that will be used in the following functions.

                                    with open(serialized_file_location, 'rb') as f:
                                        self.__Results = pickle.load(f)

            -	This is just an example using this method; however, this same procedure can be done using some other
                packages, like JSON.

        """
        t1 = time()

        # Step 1: All bolts will be analysed if no list of IDs is provided.

        if self.LC_Ids_List == []:
            self.LC_Ids_List = [lc.ID for lc in self.Model.LoadCases]
            N2PLog.Info.I500()

        # Step 2: function "get_results(model, loadcase, corner_data)"
        self.__Results = get_results(model = self.Model, loadcase = self.LC_Ids_List, corner_data = self.CornerData)

        # Show the time.
        N2PLog.Debug.D600(time(), t1)

    def get_model_fasteners(self, diameter: float = -1) -> list[ARBolt]:
        """
        Method of N2PFastenerAnalysis class which takes the model and obtains all the bolt elements in it.

        Args:
            diameter: float (Default value is -1)

        Calling example:

                        fastener.get_model_fasteners(diameter = 1)

        The steps are the following:

        1. Function "get_bolts(model)" which obtains all the bolt elements in the model. The model is defined as a
        N2oFastenerAnalysis attribute and it is a N2PModelContent object.

        2. Filter and maintain only the bolts that are in the list of IDs.

        3. Sort the bolts, function "sort()".

        4. Check if there are any CBUSH or CBAR fasteners with no diameter and show a warning if it is the case as it is
        needed for later calculations.

        Comments:

        The list of IDs is defined as an attribute of the N2PFastenerAnalysis class. If this list is not defined, all
        the bolts will be analysed. There are several possible ways of doing the analysis:

            1. Using the attribute "Bolt_Ids_List": if the list of bolt IDs is provided, the analysis will be carried out only
            for the bolt with IDs in the list. It does not matter if the attribute "Element1D_Ids_List" is filled or not,
            as only the list of bolt IDs will be taken into consideration.

            2. Using the attribute "Element1D_Ids_List": if the list of element 1D IDs is provided, the analysis will be
            carried out only for the element 1D with IDs in the list. This list will only be taken into consideration if
            the attribute "Bolt_Ids_List" is not filled.

            3. Not filling either the attribute 'Bolt_Ids_List' or 'Element1D_Ids_List' will result in all bolts being analyzed.

        The diameter is not compulsory. It should be known by the user if the model needs to be completed with
        the fasteners diameter or if everything has been done before. Thus, the input value of the diameter is only used
        if the fastener has not a defined diameter via the property card. Moreover, the fasteners without a diameter will
        be ignored.

        """
        t1 = time()

        fasts_diameter_needed = ["CBUSH", "CBAR"]

        # Step 1: function "get_bolts(model)"

        list_bolts = get_bolts(self.Model)

        # Step 2: Filter and maintain only the bolts that are in the list of IDs.

        # Case 1: No list of IDs is provided neither of bolts nor of elements 1D. All bolts will be analysed.
        if self.Bolt_Ids_List == [] and self.Element1D_Ids_List == []:
            self.Bolt_Ids_List = [bolt.ID for bolt in list_bolts]
            N2PLog.Info.I501()
        # Case 2: Only list of IDs of bolts is provided.
        elif self.Element1D_Ids_List == [] and self.Bolt_Ids_List != []:
            list_bolts = [bolt for bolt in list_bolts if bolt.ID in self.Bolt_Ids_List]
        # Case 3: Only list of IDs of elements 1D is provided.
        elif self.Bolt_Ids_List == [] and self.Element1D_Ids_List != []:
            list_bolts = [bolt for bolt in list_bolts if
                                   any(element.ID in self.Element1D_Ids_List for element in bolt.Elements1D)]
        # Case 4: Both lists of IDs are provided. Use the one of bolts.
        else:
            list_bolts = [bolt for bolt in list_bolts if bolt.ID in self.Bolt_Ids_List]

        # Step 3: sort the bolts, function "sort()".

        list_bolts = [b.sort() for b in list_bolts]

        bolts_no_head_ids = [b.ID for b in list_bolts if b.HeadNode == {None: None}]
        if len(bolts_no_head_ids) > 0:
            N2PLog.Warning.W510(bolts_no_head_ids)

        # Step 4: Check if there are any CBUSH or CBAR bolts with no diameter.

        filtered_bolts_ids = [bolt.ID for bolt in list_bolts if bolt.TypeFasteners in fasts_diameter_needed and bolt.Diameter == None]
        N2PLog.Warning.W500(filtered_bolts_ids)

        # Fill the CBUSH and CBAR with diameter
        [setattr(b, 'Diameter', diameter) for b in list_bolts if (b.TypeFasteners in fasts_diameter_needed and b.Diameter == None)]

        # CFAST diameter is empty until bypass calculation, so do not take it into account.
        bolts_cfast = [bolt for bolt in list_bolts if bolt.Diameter == None]
        filtered_bolts_1 = [bolt for bolt in list_bolts if bolt.Diameter != None]
        filtered_bolts_ids_2 = [bolt.ID for bolt in filtered_bolts_1 if bolt.Diameter <= 0]
        if len(filtered_bolts_ids_2) > 0:
            N2PLog.Error.E517(filtered_bolts_ids_2)
        list_bolts = [bolt for bolt in list_bolts if bolt.Diameter != None and bolt.Diameter > 0] + bolts_cfast

        self.ListBolts = list_bolts

        # Show the time
        N2PLog.Debug.D601(time(), t1)

    def get_analysis_fasteners(self, analysis_name: str, export_location = 0):
        """
        Method of N2PFastenerAnalysis class which obtains the analysis of the fasteners in the model.

        Args:
            export_location: str
            analysis_name: str

        Returns:
            csv file with the results

        Calling example:

                        fastener.get_analysis_fasteners(export_location, analysis_name)

        The steps are the following:

        1. Get the distance to the edges of each fastener. Done using function "get_distance_to_edges()". This function
        has as input the model (defined as an attribute of the N2PFastenerAnalysis class)

        2. Get the forces of each fastener. Done using function "get_forces()". This function has as input the results
        dictionary (defined as a hidden attribute of the N2PFastenerAnalysis class)

        3. Get the bypass loads. Done using function "get_bypass_loads()". This function has as input the model, the
        results dictionary and the corner data (defined as attributes of the N2PFastenerAnalysis class).

        4. Export the results to a csv file. Done using function "export_forces_csv_fastpph()". This function has as
        input the export location and the analysis name (obtained as an argument of this method).

        Comments:

        Worthwhile to remind that results when using Corner Data = True will be slightly different and more precise than
        the ones obtained when Corner Data = False. However, the running time will be higher.

        The csv export will have the same format as the one Altair gives when running the analysis (with some small
        modifications).

        The "get_bypass_loads()" function has some other input parameters that can be modified. These parameters are saved
        as a hidden attribute of the N2PFastenerAnalysis class in the form: BypassParameters: [[2.5], [4.0, 4.5], [1e-3]].
        Where each of them represent: [area factor, material factor, box tolerance]. However, it is highly recommended not
        to change these values. If they are wanted to be changed, the function "get_analysis_fasteners()" should be
        modified accordingly.

        There is a default value for the export location = 0. This is done in order to have the possibility not to export
        any file when using this function. If the user does not specify an export location, no file will be exported.
        """

        t1 = time()

        # Step 1: Get the distance to the edges of each fastener.
        self.ListBolts = [b.get_distance_to_edges(model = self.Model) for b in self.ListBolts]

        # Step 2: Get the forces of each fastener.
        self.ListBolts = [b.get_forces(results = self.__Results) for b in self.ListBolts]

        # Step 3: Get the bypass loads. (Add a progress bar)
        total_bolts = len(self.ListBolts)
        for index, bolt in enumerate(self.ListBolts, start=1):
            updated_bolt = bolt.get_bypass_loads(model=self.Model, results=self.__Results, corner = self.CornerData)
            self.ListBolts[index - 1] = updated_bolt
            self.__progress(index, total_bolts, 'Processing Bypasses in Bolts')
            if index < total_bolts:
                sys.stdout.write('\r')
                sys.stdout.flush()

        # Step 4: Remove the None values from the list. As when some error has occurred, the bolt is added to the initial
        # list of bolts as None
        self.ListBolts = [bolt for bolt in self.ListBolts if not bolt is None]

        # Step 5: Export the results in csv file. Only if the user has specified an export location.
        if export_location != 0:
            [bolt.export_forces_csv_fastpph(path_file = export_location, analysis_name=analysis_name, results=self.__Results)
             for bolt in self.ListBolts]

        # Show the time
        N2PLog.Debug.D602(time(), t1)



    def get_attachments_fasteners(self):
        """
        Method of N2PFastenerAnalysis class which obtains the attachments of the fasteners in the model. An attachement
        is understood as the set of bolts that join the exact same plates.

        Calling example:

                        fastener.get_attachments_fasteners()

        The steps are the following:

        1. Get the attachments. Done using function "get_attachments()". This function has as input the model (defined
        as an attribute of the N2PFastenerAnalysis class) and the bolt list to analyse.

        2. Get the pitch of the attachments. Done using function "get_pitch()". This function is actually a method of the
        class ARAttachment. Obtains the minimum pitch.

        Comments:

        It is important to know that when obtaining the attachments, the list of bolts over the ones the analysis is
        carried out is not compulsory. If it is not provided, the function will use the function "get_bolts()" in order
        to obtain it. However, the default procedure is getting it from the N2PFastenerAnalysis attribute "ListBolts".

        All the results will be stored in the object used. The only export which is not an attribute of either of the
        classes is the csv file showing the forces results.
        """
        t1 = time()

        # Step 1: Get the attachments.
        self.ListAttachments = get_attachments(model=self.Model, bolt_list=self.ListBolts)

        # Step 2: Get the pitch of the attachments.
        self.ListAttachments = [attachment.get_pitch() for attachment in self.ListAttachments]

        N2PLog.Debug.D603(time(), t1)


    def calculate(self, analysis_name: str, export_location = 0, diameter = -1):
        """
        Method of N2PFastenerAnalysis class which carries out the analysis.

        Args:
            analysis_name: str
            export_location: int (Default value is 0)
            diameter: int (Default value is -1)

        Calling example:

                    fastener.calculate(analysis_name = 'Test', export_location = path, diameter = 4.8)

        The steps are the following:

        1. Get the results. Done using function "get_results_fasteners()".

        2. Get the fasteners. Done using function "get_model_fasteners()".

        3. Analyze the fasteners. Done using function "get_analysis_fasteners()".

        4. Get the attachments. Done using function "get_attachments_fasteners()".

        Comments:

        The export location is not compulsory. If it is not provided, no file will be exported. The diameter is not
        compulsory as well. It should be known by the user if the model needs to be completed with the fasteners diameter
        or if everything has been done before. Thus, the input value of the diameter is only used if the fastener has not
        a defined diameter. Moreover, the fasteners without a diameter will be ignored.

        When ysing this method, as the bolts and their IDs are created inside the method itself, it is recommended to
        use the N2PFastenerAnalysis attribute called "Element1D_Ids_List" to obtain the IDs of the elements 1d that are
        wanted to be analyzed. It is important to remember that the attribute "Bolt_Ids_List" should be empty then.

        """
        t1 = time()
        # Step 1: Get the results.
        self.get_results_fasteners()

        # Step 2: Get the fasteners.
        self.get_model_fasteners(diameter=diameter)

        # Step 3: Analyze the fasteners
        self.get_analysis_fasteners(analysis_name= analysis_name, export_location = export_location)

        # Step 4: Get the attachments
        self.get_attachments_fasteners()

        N2PLog.Debug.D604(time(), t1)


    ################################### AUXILIARY FUNCTIONS ##########################################

    def __progress(self,count, total, suffix=''):
        """
        A function to display a progress bar based on the count and total, with an optional suffix.
        Parameters:
            count (int): The current count or progress.
            total (int): The total count or total progress.
            suffix (str): An optional suffix to be displayed alongside the progress bar.
        Returns:
            None
        """
        bar_length = 60
        filled_length = int(round(bar_length * count / total))
        percents = round(100.0 * count / total, 1)
        bar = '■' * filled_length + '□' * (bar_length - filled_length)

        sys.stdout.write('\r[%s] %s%s ...%s' % (bar, percents, '%', suffix))
        sys.stdout.flush()








