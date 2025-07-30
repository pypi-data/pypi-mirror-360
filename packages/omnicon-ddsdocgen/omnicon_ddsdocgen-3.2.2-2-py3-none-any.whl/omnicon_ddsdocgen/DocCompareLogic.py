import math
import os
import tempfile
import time
from datetime import datetime
from typing import List, Dict

from . import Utils
from . import DocumentHandler
from . import DocxGen
from . import HtmlGen
from . import PdfGen
from .ComparisonModule import ComparisonModule
from .GeneralFunctions import PhaseEnum
from .comp import CompElement, ChangeStatusEnum
from . import GeneralFunctions
from . import Logger
from . import SingleChapterGenerator
from .ErrorListHandler import ErrorListHandler, LogLevel

from Omnicon_GenericDDSEngine_Py import Omnicon_GenericDDSEngine_Py as Omnicon

from .OmniconEngineHandler import OmniconEngineHandler


class DocCompareLogic:
    def __init__(self, progress_callback_function, logging_verbosity, license_file_path) -> None:

        self.license_file_path = license_file_path
        GeneralFunctions.check_progress_callback_function_signature(progress_callback_function)
        self.update_external_progress_callback_function = progress_callback_function

        self.single_chapter_generator = None

        self.logger = Logger.add_logger(__name__)
        self.logging_verbosity = logging_verbosity

        self.table_header_titles = \
            ["Hierarchy", "Field", "Type", "Description/Metadata", "Change Description"]
            # ["Hierarchy", "Field", "Type", "Description/Metadata", "Change Type", "Change Description"]

        GeneralFunctions.check_artifacts_integrity(self.logger)

        self.new_engine_handler = None
        self.origin_engine_handler = None

        self.is_ignore_id = False
        self.is_compare_by_name = True
        self.is_summary_report = False

        self.is_progress_bar_func_ok = True
        self.num_of_chapters = -1

    @staticmethod
    def VERSION():
        return "1.0"

    def calculate_total_work_for_progress_bar(
            self, origin_dds_topics_types_xml, new_dds_topics_types_xml, num_of_formats):
        """
        This function determines the numbers that would be used to calculate the progress (for the progress bar)
        :param num_of_chapters: The total number of chapters from the given XML
        :return:
        """

        origin_num_of_chapters: int
        new_num_of_chapters: int

        if origin_dds_topics_types_xml != "" and new_dds_topics_types_xml != "":
                origin_chapter_map = Omnicon.GenericDDSEngine.GetTopicNameToTypeNameMap(origin_dds_topics_types_xml)
                new_chapter_map = Omnicon.GenericDDSEngine.GetTopicNameToTypeNameMap(origin_dds_topics_types_xml)

                origin_num_of_chapters = len(origin_chapter_map.keys())
                new_num_of_chapters = len(new_chapter_map.keys())
        else:
            origin_chapter_list = self.origin_engine_handler.engine.GetTypesBasicInfo()
            new_chapter_list = self.new_engine_handler.engine.GetTypesBasicInfo()

            origin_num_of_chapters = len(origin_chapter_list)
            new_num_of_chapters = len(new_chapter_list)

        if not new_num_of_chapters:
            self.logger.error("New DDS type files are invalid")
            raise Exception("Error! Invalid New DDS type files!")
        if not origin_num_of_chapters:
            self.logger.error("New DDS type files are invalid")
            raise Exception("Error! Invalid New DDS type files!")

        else:
            self.origin_num_of_chapters = origin_num_of_chapters
            self.num_of_steps_per_phase = origin_num_of_chapters + new_num_of_chapters
            # 2 is for phases: parsing & comparing. Add a writing phase per format + one step per format saving
            steps_for_parsing_phase = self.num_of_steps_per_phase
            steps_for_comparing_phase = self.num_of_steps_per_phase
            # writing phase per format + one step per format saving. using 2 factor because worst case scenario is
            # that one name change is manifested as deleting of the old and adding the new.
            steps_for_writing_phase = num_of_formats * self.num_of_steps_per_phase * 2 + num_of_formats
            self.total_steps = steps_for_parsing_phase + steps_for_comparing_phase + steps_for_writing_phase
        self.logger.debug("Finished calculating total work for progress bar")

    def update_progress_bar_parse(self, iteration_number: int, DDS_type: str, phase: PhaseEnum):
        # NOTE: when phase == PARSE_ORIGIN_PHASE (0) phase.value * self.origin_num_of_chapters is 0. So
        # this part is for taking num of origin chapters into account when parsing the revised version
        current_step = iteration_number + phase.value * self.origin_num_of_chapters
        # At this stage ErrorListHandler.get_current_module().lower() is "parsing <version name>"
        info = f"{ErrorListHandler.get_current_module().lower()}: {DDS_type}"

        self.update_progress_bar(current_step, info)

    def update_progress_bar_compare(self, iteration_number: int, DDS_type: str):

        # adding self.num_of_steps_per_phase because that's how many steps were finished in previous phase
        current_step = iteration_number + self.num_of_steps_per_phase

        # At this stage ErrorListHandler.get_current_module().lower() is "comparing"
        info = f"{ErrorListHandler.get_current_module().lower()}: {DDS_type}"

        self.update_progress_bar(current_step, info)

    def update_progress_bar_write(self, iteration_number, DDS_type, progress_factor = 0, is_save = False):
        # adding 2 * self.num_of_steps_per_phase because that's how many steps were finished in previous phase
        current_step = iteration_number + (2 * self.num_of_steps_per_phase) + \
                       progress_factor * self.num_of_steps_per_phase
        if is_save:
            current_step = iteration_number + (2 * self.num_of_steps_per_phase) + \
                       progress_factor * 2 * self.num_of_steps_per_phase

        # At this stage ErrorListHandler.get_current_module().lower() is "generating <output format>"
        info = f"{ErrorListHandler.get_current_module().lower()}: {DDS_type}"

        self.update_progress_bar(current_step, info)
        self.latest_step = current_step

    def update_progress_bar(self, current_step: int, info: str):
        if self.update_external_progress_callback_function is not None:
            if self.is_progress_bar_func_ok:
                try:
                    self.update_external_progress_callback_function(self.total_steps, current_step, info)
                except Exception:
                    self.is_progress_bar_func_ok = False
                    warning_text = f"There seems to be a problem with the provided progress bar callback function. " \
                                   f"Please refer to README.md for the required progress bar function."
                    ErrorListHandler.add_entry(LogLevel.WARNING, warning_text)

    def update_progress_finalize(self):
        """
        This function is purely as user experience, so that users dont feel like something's wrong with the progress.
        So this function just runs the numbers all the way up to
        """
        last_progress = (self.latest_step / self.total_steps) * 100

        if last_progress < 95:
            # Calculate the number of steps needed to reach 100
            steps_needed = 99 - last_progress
            sleep_time = 1 / steps_needed  # Time to sleep between each step, to total ~1 second

            # Move the progress from where we left off to 99. (100 will be achieved later)
            for i in range(math.ceil(last_progress), 99):
                latest_step =  int(i * self.total_steps / 100)
                self.update_progress_bar(latest_step, "Finalizing")
                time.sleep(sleep_time)

    def update_progress_end(self):
        if self.update_external_progress_callback_function is not None:
            if self.is_progress_bar_func_ok:
                try:
                    state_txt = f"DocGen operation is completed."
                    self.update_external_progress_callback_function(1, 1, state_txt)
                except Exception:
                    self.is_progress_bar_func_ok = False
                    warning_text = f"There seems to be a problem with the provided progress bar callback function. " \
                                   f"Please refer to README.md for the required progress bar function."
                    ErrorListHandler.add_entry(LogLevel.WARNING, warning_text)

    def generate_type_based_comp_structure(self, order_alphabetically, engine, phase: PhaseEnum) -> Dict:
        """
        This function generates an ICD with non-nested types as chapters.
        :param order_alphabetically: a boolean that indicates whether to use an alphabetical order (true) or
                                     the xml order (false).
        :param engine:  a 'pointer' to the relevant Omnicon engine
        :param phase: (PhaseEnum) helps knowing which phase this is

        Return: list of errors
        """

        self.logger.debug("Topic-to-types XML file was not found. Using DDS type names as chapter headers.")
        # Use the engine's API to get a list of all available types:
        DDS_type_list = engine.GetTypesBasicInfo()

        if order_alphabetically:
            # When the user requested the chapters ordered alphabetically
            DDS_type_list.sort(key=GeneralFunctions.get_type_name)

        if not DDS_type_list:
            self.logger.error("DDS type files are invalid")
            raise Exception("Error! Invalid DDS type files!")
        # A flag that holds TRUE (when at least one chapter (type) was written. False when no chapter was written):
        is_at_least_one_type_ok: bool = False
        iteration_number: int = 1

        structured_doc_data = {}
        single_chapter_generator = \
            SingleChapterGenerator.SingleChapterGenerator(engine)

        for DDS_type in DDS_type_list:
            self.update_progress_bar_parse(iteration_number, DDS_type.fullName, phase)
            iteration_number += 1
            if DDS_type.isNested is False:
                # Add a chapter only when the type is not a nested one:
                try:
                    structured_doc_data[DDS_type.fullName] = \
                        single_chapter_generator.generate_single_chapter("", DDS_type.fullName)
                except Exception as err:
                    # Signal that there is an issue with one of the types.
                    ErrorListHandler.add_entry(LogLevel.ERROR, err)
                    self.is_all_types_ok = False
                else:
                    # When writing a chapter went well
                    is_at_least_one_type_ok = True
        if is_at_least_one_type_ok is False:
            raise Exception("Could not find any DDS-type in provided files/folders!")

        return structured_doc_data

    def generate_topic_based_comp_structure(self,
                                            topic_names_to_types_xml: str,
                                            order_alphabetically: int,
                                            single_chapter_generator,
                                            phase: PhaseEnum) -> Dict:
        """
        This function generates an ICD with topics as chapters.
        :param topic_names_to_types_xml:  The topic names to types xml file name.
        :param order_alphabetically: a boolean that indicates whether to use an alphabetical order (true) or
                                     the xml order (false).
        :param phase: Helps knowing where we're at in terms of progress
        :return: a list of all topics that had errors while processing

        """
        self.logger.debug("Using topics as chapter headers.")
        # Get the topic to type map:
        DDSTopicToTypeXMLMapping = Omnicon.GenericDDSEngine.GetTopicNameToTypeNameMap(topic_names_to_types_xml)

        if bool(DDSTopicToTypeXMLMapping) is False:
            self.logger.error("DDS topics-to-types XML mapping file is invalid: %s ", topic_names_to_types_xml)
            raise Exception("Invalid DDS topics-to-types XML mapping file!")

        if order_alphabetically == False:
            # When the user requested the topic order to be as it is in the xml file:
            DDSTopicToTypeXMLMapping = GeneralFunctions.order_topics_by_xml(
                topic_names_to_types_xml, DDSTopicToTypeXMLMapping)
        # A flag that holds TRUE (when at least one chapter (type) was written. False when no chapter was written):
        is_at_least_one_type_ok: bool = False
        # Run the introspection for each data type:
        iteration_number: int = 1

        structured_doc_data = {}

        for topic, DDS_type in DDSTopicToTypeXMLMapping.items():
            self.update_progress_bar_parse(iteration_number, DDS_type, phase)
            iteration_number += 1
            # Generate a new chapter for that topic / type:
            try:
                structured_doc_data[topic] = single_chapter_generator.generate_single_chapter(topic, DDS_type)
            except Exception as e:
                self.logger.error(Exception, e)
                # Signal that there is an issue with one of the types.
                error_message: str = 'Failed to parse topic ' + topic + ' . Error : ' + str(e)
                self.logger.error(error_message)
                ErrorListHandler.add_entry(LogLevel.ERROR, error_message)
                self.is_all_types_ok = False
            else:
                # When writing a chapter went well
                is_at_least_one_type_ok = True

        self.logger.debug("generate_topic_based_comp_structure has finished going over the topics")

        if is_at_least_one_type_ok is False:
            self.logger.error("No DDS-type was found in the provided files/folders.")
            raise Exception("Could not find any DDS-type in provided files/folders!")

        return structured_doc_data

    def shutdown_engines(self):
        if self.origin_engine_handler:
            self.origin_engine_handler.shutdown_engine()
            self.origin_engine_handler = None
        if self.new_engine_handler:
            self.new_engine_handler.shutdown_engine()
            self.new_engine_handler= None
        Omnicon.GenericDDSEngine.FinalizeFactory()

    @staticmethod
    def extract_file_or_folder_name(path):
        # Check if the path is a file
        if os.path.isfile(path):
            # Return the file name if it's a file
            return os.path.basename(path)
        elif os.path.isdir(path):
            # Return the folder name if it's a directory
            return f"Folder: {os.path.basename(path)}"

    @staticmethod
    def extract_base_names_from_list(full_path_files_list):
        base_files_list = []
        for full_path_file in full_path_files_list:
            base_files_list.append(DocCompareLogic.extract_file_or_folder_name(full_path_file))
        return base_files_list


    def get_appropriate_doc_handler(self, output_format, title, date_time_string,
                                           origin_version: str,
                                           new_version: str,
                                           origin_dds_types_files: list,
                                           new_dds_types_files: list,
                                           origin_dds_topics_types_xml: str = "",
                                           new_dds_topics_types_xml: str = ""):

        # Switch 'output format' to lower case:
        output_format = output_format.lower()

        base_origin_type_files = DocCompareLogic.extract_base_names_from_list(origin_dds_types_files)
        if bool(origin_dds_topics_types_xml):
            origin_dds_topics_types_xml = os.path.basename(origin_dds_topics_types_xml)
        if bool(new_dds_topics_types_xml):
            new_dds_topics_types_xml = os.path.basename(new_dds_topics_types_xml)
        base_new_type_files = DocCompareLogic.extract_base_names_from_list(new_dds_types_files)


        if output_format == 'docx':
            # Case where the requested type is docx
            return DocxGen.DocxGen(title=title,
                         new_version=new_version,
                         time=date_time_string,
                         origin_version=origin_version,
                         origin_dds_types_files=base_origin_type_files,
                         new_dds_types_files=base_new_type_files,
                         origin_dds_topics_types_mapping=origin_dds_topics_types_xml,
                         new_dds_topics_types_mapping=new_dds_topics_types_xml,
                         is_compare_by_name=self.is_compare_by_name,
                         is_ignore_id=self.is_ignore_id,
                         is_summary_report=self.is_summary_report)
        elif output_format == 'html':
            # Case where the requested type is html
            return HtmlGen.HtmlGen(title=title,
                         new_version=new_version,
                         time=date_time_string,
                         origin_version=origin_version,
                         origin_dds_types_files=base_origin_type_files,
                         new_dds_types_files=base_new_type_files,
                         origin_dds_topics_types_mapping=origin_dds_topics_types_xml,
                         new_dds_topics_types_mapping=new_dds_topics_types_xml,
                         is_compare_by_name=self.is_compare_by_name,
                         is_ignore_id=self.is_ignore_id,
                         is_summary_report=self.is_summary_report)
        elif output_format == 'pdf':
            # Case where the requested type is pdf
            return PdfGen.PdfGen(title=title,
                         new_version=new_version,
                         time=date_time_string,
                         origin_version=origin_version,
                         origin_dds_types_files=base_origin_type_files,
                         new_dds_types_files=base_new_type_files,
                         origin_dds_topics_types_mapping=origin_dds_topics_types_xml,
                         new_dds_topics_types_mapping=new_dds_topics_types_xml)

        else:
            # When an invalid type was requested, send warning and continue to the nextformat:
            warning_message = f"Requested output format '{output_format}' is unsupported at this point."
            self.logger.warning(warning_message)
            ErrorListHandler.add_entry(LogLevel.ERROR, warning_message)
            return None

    def run_engine_and_generate_comparison(self,
                                           origin_dds_types_files: list,
                                           new_dds_types_files: list,
                                           origin_dds_topics_types_xml: str = "",
                                           new_dds_topics_types_xml: str = "",
                                           output_file_name: str = "ICD",
                                           title: str = "ICD",
                                           origin_version = "v1",
                                           new_version = "v2",
                                           is_parse_ROS2_constants = False,
                                           order_alphabetically: bool = True,
                                           output_folder: str = "",
                                           output_formats=None) -> (bool, List[str]):

        self.is_all_types_ok = True  # An indicator that helps to know whether all types went well
        is_at_least_one_file_created = False

        try:
            # Two variables to know which status to give the user at the end.
            is_at_least_one_file_created = False
            is_at_least_one_file_error = False

            OmniconEngineHandler.set_engines_factory_verbosity(self.logging_verbosity)

            self.origin_engine_handler = OmniconEngineHandler(
                origin_dds_types_files, is_parse_ROS2_constants, self.license_file_path)
            self.new_engine_handler = OmniconEngineHandler(
                new_dds_types_files, is_parse_ROS2_constants, self.license_file_path)


            self.origin_single_chapter_generator = \
                SingleChapterGenerator.SingleChapterGenerator(self.origin_engine_handler.engine)
            self.new_single_chapter_generator = \
                SingleChapterGenerator.SingleChapterGenerator(self.new_engine_handler.engine)

            self.calculate_total_work_for_progress_bar(origin_dds_topics_types_xml, new_dds_topics_types_xml, len(output_formats))

            origin_comp_structure = {}
            new_comp_structure = {}
            # See whether the ICD is to be based on topics or on types:
            if origin_dds_topics_types_xml != "" and new_dds_topics_types_xml != "":
                # When the user provided a topic-to-types xml, a topic-based comp structure is to be created:
                ErrorListHandler.update_current_module_name(f"Parsing {origin_version}")
                origin_comp_structure = self.generate_topic_based_comp_structure(
                    origin_dds_topics_types_xml, order_alphabetically,self.origin_single_chapter_generator, PhaseEnum.PARSE_ORIGIN_PHASE)

                ErrorListHandler.update_current_module_name(f"Parsing {new_version}")
                new_comp_structure = self.generate_topic_based_comp_structure(
                    new_dds_topics_types_xml, order_alphabetically, self.new_single_chapter_generator, PhaseEnum.PARSE_REVISED_PHASE)
            else:
                # When the user did NOT provide a topic-to-type XML:
                ErrorListHandler.update_current_module_name(f"Parsing {origin_version}")
                origin_comp_structure = self.generate_type_based_comp_structure(
                        order_alphabetically,
                        self.origin_engine_handler.engine,
                        PhaseEnum.PARSE_ORIGIN_PHASE)
                ErrorListHandler.update_current_module_name(f"Parsing {new_version}")
                new_comp_structure = self.generate_type_based_comp_structure(
                        order_alphabetically,
                        self.new_engine_handler.engine,
                        PhaseEnum.PARSE_REVISED_PHASE)

            ErrorListHandler.update_current_module_name(f"Comparing")
            # Run comparison
            comparison_module = ComparisonModule(self.is_ignore_id, self.is_compare_by_name, self.update_progress_bar_compare)
            result_structure = comparison_module.compare_structures(origin_comp_structure, new_comp_structure)

            self.generate_documents_from_result_struct(
                result_structure=result_structure,
                changes_dict=comparison_module.changes_dict,
                output_file_name=output_file_name,
                title=title,
                origin_version=origin_version,
                new_version=new_version,
                origin_dds_types_files=origin_dds_types_files,
                new_dds_types_files=new_dds_types_files,
                new_dds_topics_types_xml=new_dds_topics_types_xml,
                origin_dds_topics_types_xml=origin_dds_topics_types_xml,
                output_folder=output_folder,
                output_formats=output_formats)

            is_at_least_one_file_created = True

        except Exception as err:
            ErrorListHandler.add_entry(LogLevel.ERROR, str(err))
            self.logger.error(str(err), exc_info=True)

        self.shutdown_engines()
        Omnicon.GenericDDSEngine.FinalizeFactory()
        if is_at_least_one_file_created:
            self.update_progress_end()
        time.sleep(0.5)

        ErrorListHandler.update_current_module_name("general")

        return is_at_least_one_file_created

        # if is_at_least_one_file_created == False:
        #     warning_message = "There was an issue creating the files. Please refer to the log for more information."
        #     self.logger.error(warning_message)
        #     ErrorListHandler.add_entry(LogLevel.ERROR, warning_message)
        #
        # elif is_at_least_one_file_error:
        #     msg = "There was an issue with some of the requested files. " \
        #           "Please refer to the log for more information."
        #     self.logger.warning(msg)
        #     ErrorListHandler.add_entry(LogLevel.WARNING, msg)

    def generate_documents_from_result_struct(self,
                                           result_structure: Dict[str,CompElement],
                                           changes_dict: dict,
                                           output_file_name: str,
                                           title: str ,
                                           origin_version: str,
                                           new_version: str,
                                           origin_dds_types_files: list,
                                           new_dds_types_files: list,
                                           origin_dds_topics_types_xml: str = "",
                                           new_dds_topics_types_xml: str = "",
                                           output_folder: str = "",
                                           output_formats=None) -> (bool, List[str]):
        # start with the time
        now: datetime = datetime.now()
        date_time_string: str = now.strftime("%d/%m/%Y %H:%M:%S")

        # Create a document for each format:
        for i, output_format in enumerate(output_formats):
            # Create a temporary directory to save some temporary files
            with tempfile.TemporaryDirectory() as temp_folder:
                try:
                    ErrorListHandler.update_current_module_name(f"Generating {output_format}")
                    # Check if the requested file is open
                    if Utils.is_output_file_open(output_file_name, output_folder, output_format):
                        # When the output file is open:
                        is_at_least_one_file_error = True
                        warning_message = f"Cannot save file while {output_file_name}.{output_format} is open. " \
                                          f"Please close the file and try again."
                        self.logger.warning(warning_message)
                        ErrorListHandler.add_entry(LogLevel.ERROR, warning_message)
                        continue

                    self.doc_generator = \
                        self.get_appropriate_doc_handler(
                            output_format=output_format,
                            title=title,
                            date_time_string=date_time_string,
                            origin_version=origin_version,
                            new_version=new_version,
                            origin_dds_types_files=origin_dds_types_files,
                            new_dds_types_files=new_dds_types_files,
                            new_dds_topics_types_xml=new_dds_topics_types_xml,
                            origin_dds_topics_types_xml=origin_dds_topics_types_xml)

                    document_handler = DocumentHandler.DocumentHandler(
                        self.doc_generator, self.table_header_titles,
                        is_comparison=True, update_progress_bar=self.update_progress_bar_write)

                    progress_position = document_handler.create_ICD_from_structured_doc_data(
                        structured_doc_data=result_structure,
                        changes_dict=changes_dict,
                        progress_factor=i,
                        is_summary_report=self.is_summary_report)

                    document_handler.finalize_doc(
                        output_file_name=output_file_name,
                        output_folder=output_folder,
                        temp_folder=temp_folder,
                        output_format=output_format, progress_position=progress_position,  progress_factor=i )

                    ErrorListHandler.update_current_module_name(f"Saving {output_format}")

                    # # Finalize and save doc
                    # self.doc_generator.finalize_doc()
                    # self.doc_generator.generate_doc(output_file_name, temp_folder)
                    # document_handler.save_file_to_requested_folder(
                    #     output_file_name, output_folder, temp_folder, output_format)

                except Exception as err:
                    ErrorListHandler.add_entry(LogLevel.ERROR, str(err))
                    self.logger.error(str(err), exc_info=True)

        self.update_progress_finalize()

    @staticmethod
    def check_mutual_topic_mapping(origin_topic_mapping, new_topic_mapping):
        # Expecting both parameters to be "" or both to be a topic xml
        # When all is ok return, and raise exception when not
        if not origin_topic_mapping and not new_topic_mapping:
            return
        elif origin_topic_mapping and new_topic_mapping:
            return

        error_message: str = f"Invalid input. Both topic mapping parameters should be empty or both should be a valid" \
                             f" XML file. Received values: Origin - {origin_topic_mapping}, New - {new_topic_mapping}"
        raise Exception(error_message)

    def run_doc_compare(self,
                        origin_dds_types_files: list,
                        new_dds_types_files: list,
                        origin_dds_topics_types_mapping: str = "",
                        new_dds_topics_types_mapping: str = "",
                        output_file_name: str = "ICD",
                        title: str = "ICD",
                        origin_version: str = "v1",
                        new_version: str = "v2",
                        order_alphabetically: bool = True,
                        output_folder: str = "",
                        output_formats=None,
                        is_ignore_id: bool = False,
                        is_parse_ROS2_constants: bool = False) -> (bool, List[str]):
        """
        Start the doc comparison process.
        :param origin_dds_types_files: A list of DDS XML type files or folders of the original date model.
        :param new_dds_types_files: A list of DDS XML type files or folders of the revised data model.
        :param origin_dds_topics_types_mapping: (string) An XML file that contains a DDS topic to type mapping of the
                                                original date model. NOTE: This parameter is optional; In case mapping
                                                is not provided, a type-based comparison will be generated.
        :param new_dds_topics_types_mapping: (string) An XML file that contains a DDS topic to type mapping of the
                                              revised date model. NOTE: This parameter is optional; In case mapping
                                              is not provided, a type-based comparison will be generated.
        :param output_file_name: (string) The user's file name of choice. NOTE: This parameter is optional.
                                  Default: "ICD".
        :param title: (string) The title/heading  of the document. This string will be added to the first page of the
                               document. NOTE: This parameter is optional; Default is "ICD"
        :param origin_version: The old data model's version number - This string will be added to a table at the top
                        page of the comparison doocument. NOTE: This parameter is optional; Default is "v1"
        :param new_version: The new data model's version number - This string will be added to a table at the top page
         of the comparison doocument. NOTE: This parameter is optional; Default is "v2"
        :param order_alphabetically: Whether to order to generated document topics/types alphabetically or according to
                                    the loaded files order
        :param output_folder: (string) The user's output folder of choice. NOTE: This parameter is optional;
                              Default is current working directory.
        :param output_formats: A list of desired output formats as strings. for example: ["docx", "pdf", "html"]
        :param progress_callback_function: A 'pointer' to the function that updates the progress bar.
        :param is_ignore_id: (bool) determines if the ID is to be compared AT ALL.
        :param document_type: (str) Either 'complete' (for a full document which includes all the fields in topics that
                                have changes in them) or 'summary' (for a report that show only the changes).
        :param is_parse_ROS2_Constants: (bool) determine if ROS2 constants are used to allow special parsing for
                                        that case
        :return: tuple of (bool, list). bool: True upon success. list: list of errors that happened along the way
        """
        is_document_generated: bool = False
        try:
            ErrorListHandler.clear_list()

            # if 'html' in output_formats:
            #     error_message: str = f"Invalid input. Within the list parameter <output_formats>: 'html' is not " \
            #                          f"available at this point"
            #     raise Exception(error_message)

            GeneralFunctions.check_input(
                is_compare=True,
                origin_input_files_and_dirs_list=origin_dds_types_files,
                origin_topic_names_to_types_xml_path=origin_dds_topics_types_mapping,
                output_file_name=output_file_name,
                title=title,
                origin_version=origin_version,
                new_version=new_version,
                output_folder=output_folder,
                order_alphabetically=order_alphabetically,
                output_formats=output_formats,
                new_input_files_and_dirs_list=new_dds_types_files,
                new_topic_names_to_types_xml_path=new_dds_topics_types_mapping,
                is_ignore_id=is_ignore_id,
                is_parse_ROS2_constants=is_parse_ROS2_constants
            )

            self.logger.info(f"origin_type_file_path_list: {origin_dds_types_files}")
            self.logger.info(f"new_type_file_path_list: {new_dds_types_files}")
            self.logger.info(f"origin_topic_names_to_types_xml_path: {origin_dds_topics_types_mapping}")
            self.logger.info(f"new_topic_names_to_types_xml_path: {new_dds_topics_types_mapping}")
            self.logger.info(f"output_folder: {output_folder}")
            self.logger.info(f"output_file_name: {output_file_name}")

            is_document_generated = self.run_engine_and_generate_comparison(origin_dds_types_files=origin_dds_types_files,
                                                    new_dds_types_files=new_dds_types_files,
                                                    origin_dds_topics_types_xml=origin_dds_topics_types_mapping,
                                                    new_dds_topics_types_xml=new_dds_topics_types_mapping,
                                                    output_file_name=output_file_name,
                                                    title=title,
                                                    is_parse_ROS2_constants=is_parse_ROS2_constants,
                                                    origin_version=origin_version,
                                                    new_version=new_version,
                                                    order_alphabetically=order_alphabetically,
                                                    output_folder=output_folder,
                                                    output_formats=output_formats)


        except Exception as err:
            # self.logger.error(err, exc_info=True)
            ErrorListHandler.add_entry(LogLevel.ERROR, err)

        return (is_document_generated, ErrorListHandler.get_error_list())
