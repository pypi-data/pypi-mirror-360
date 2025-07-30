import os
from typing import Any, Callable, List

from . import DocCompareLogic, Logger
from . import DocGenLogic
from . import GeneralFunctions


class DDSDocGen():
    def __init__(self, logging_verbosity: str = "WARNING", progress_callback_function: Callable[[], Any] = None,
                 license_file_path: str = "") -> None:
        """
        :param logging_verbosity: The requested level of logging. Could be either 'FATAL','ERROR','WARNING',
                                'INFO' or 'DEBUG'. NOTE: This parameter is optional; Default is 'INFO'.
        """
        verbosity_upper = logging_verbosity.upper()
        self.check_logging_verbosity(verbosity_upper)
        if bool(license_file_path):
            self.check_license_file_path(license_file_path)

        self.logger = Logger.init_logger("omnicon_ddsdocgen", verbosity_upper)
        progress_function = progress_callback_function
        if progress_callback_function is None:
           progress_function = self.__default_progress_callback_function

        self.__document_generator = DocGenLogic.DocumentGenerator(progress_function, verbosity_upper,license_file_path)
        self.__document_comparator = DocCompareLogic.DocCompareLogic(progress_function, verbosity_upper, license_file_path)

    @staticmethod
    def check_license_file_path(file_path):
        # Name of the license file
        license_file_name = "OmniCon-LicenseFile.xml"

        # Check if the input is a string
        if not isinstance(file_path, str):
            raise ValueError("The license file path must be a string.")

        # Resolve the provided path to an absolute path
        resolved_path = os.path.abspath(file_path)

        # Check if the resolved path points to an existing directory
        if not os.path.isdir(resolved_path):
            raise NotADirectoryError(
                f"Invalid input: The specified license_file_path '{resolved_path}' is not a directory.")

        # Check if the license file exists in the specified directory
        full_license_file_path = os.path.join(resolved_path, license_file_name)
        if not os.path.isfile(full_license_file_path):
            raise FileNotFoundError(
                f"Invalid input: The license file '{license_file_name}' does not exist in the specified "
                f"license_file_path '{resolved_path}'.")

    @staticmethod
    def check_logging_verbosity(logging_verbosity):
        # Check it is a string
        GeneralFunctions.check_single_input_type(logging_verbosity, "", f"logging_verbosity")

    @staticmethod
    def __default_progress_callback_function(total_steps: int, current_step: int, info: str):
        percentage = (current_step / total_steps) * 100
        percentage_to_print = "{:.1f}".format(percentage)
        print(f"{percentage_to_print}% complete, {info}")

    def generate_document(self,
                          dds_types_files: list,
                          dds_topics_types_mapping: str = "",
                          output_file_name: str = "ICD",
                          title: str = "ICD",
                          version: str = "1.0",
                          order_alphabetically: bool = True,
                          output_folder: str = "",
                          output_formats=None,
                          average_str_length=1,
                          average_sequence_length=1,
                          parse_ROS2_Constants=False
                          ) -> (bool, List[str]):
        """
        Start the doc generation process.
        :param dds_types_files: A list of DDS XML type files or folders.
            :param dds_topics_types_mapping: (string) An XML file that contains a DDS topic to type mapping. NOTE: This
                                              parameter is optional; In case the mapping is not provided, a type-based
                                              ICD will be generated.
        :param output_file_name: (string) The user's file name of choice. NOTE: This parameter is optional.
                                  Default: "ICD".
        :param title: (string) The title/heading  of the document. This string will be added to the first page of the
                               document. NOTE: This parameter is optional; Default is "ICD"
        :param version: The document's version number - This string will be added to the top page of the ICD.
                        NOTE: This parameter is optional; Default is "1.0"
        :param order_alphabetically: Whether to order to generated document topics/types alphabetically or according to
                                    the loaded files order
        :param output_folder: (string) The user's output folder of choice. NOTE: This parameter is optional;
                              Default is current working directory.
        :param output_formats: A list of desired output formats as strings. for example: ["docx", "pdf", "html"]
        :param average_str_length: The average length of strings. Used for calculating the average size of
                               a given message.
        :param average_sequence_length: The average length of sequences. Used for calculating the average size of
                               a given message.
        :param is_parse_ROS2_Constants: (bool) Whenever ROS2 constants are used in the data model, this parameter can
                                be enabled to initiate an appropriate parsing mechanism.
        :return: tuple of (bool, list). bool: True upon success. list: list of errors that happened along the way
        """

        return self.__document_generator.run_doc_gen(
            dds_types_files=dds_types_files,
            dds_topics_types_mapping=dds_topics_types_mapping,
            output_file_name=output_file_name,
            title=title,
            version=version,
            order_alphabetically=order_alphabetically,
            output_folder=output_folder,
            output_formats=output_formats,
            average_str_length=average_str_length,
            average_sequence_length=average_sequence_length,
            is_parse_ROS2_constants=parse_ROS2_Constants
        )

    def determine_comparison_method(self, comparison_method: str)-> bool:
        # First verify the type is str:
        GeneralFunctions.check_single_input_type(comparison_method, "", "comparison_method")

        # Returning True if comparing by name, False if comparing by id
        if comparison_method.lower() == "id":
            return False
        elif comparison_method.lower() == "name":
            return True

        else:
            raise Exception("Comparison method parameter is invalid. Please use either 'name' or 'id'")

    def determine_document_type(self, document_type: str, output_formats: list)-> bool:

        GeneralFunctions.check_single_input_type(document_type, "", f"document_type")
        GeneralFunctions.check_single_input_type(output_formats, [], f"output_formats")

        # Returning True if comparing by name, False if comapring by id
        if document_type.lower() == "summary":
            # First make sure there is no html-summary combination:
            if "HTML" in output_formats or "html" in output_formats:
                raise Exception("Error: The requested operation is not supported. Summary documents cannot be generated "
                                "in HTML format.\nPlease choose a different document type or format and try again.")
            # Now that we know this is not an html summary, we can return True without throwing an exception:
            return True
        elif document_type.lower() == "complete" or document_type.lower() == "full":
            return False

        else:
            raise Exception("Document type parameter is invalid. Please use either 'complete' or 'summary'")

    def generate_comparison_document(self,
                          origin_dds_types_files: list,
                          new_dds_types_files: list,
                          origin_dds_topics_types_mapping: str = "",
                          new_dds_topics_types_mapping: str = "",
                          output_file_name: str = "Comparison",
                          title: str = "Comparison",
                          origin_version: str = "v1",
                          new_version: str = "v2",
                          order_alphabetically: bool = True,
                          output_folder: str = "",
                          output_formats=None,
                          parse_ROS2_Constants=False,
                          ignore_id: bool = False,
                          comparison_method: str = "name",
                          document_type: str = "complete") -> (bool, List[str]):
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
        :param origin_version: The origin document's version number - This string will be added to a table at the top
                        page of the comparison document.
                        NOTE: This parameter is optional; Default is "v1".
        :param new_version: The new document's version number - This string will be added to a table at the top
                        page of the comparison document.
                        NOTE: This parameter is optional; Default is "v2".
        :param order_alphabetically: Whether to order to generated document topics/types alphabetically or according to
                                    the loaded files order
        :param output_folder: (string) The user's output folder of choice. NOTE: This parameter is optional;
                              Default is current working directory.
        :param output_formats: A list of desired output formats as strings. for example: ["docx", "pdf", "html"]
        :param ignore_id: (bool) determines if the ID is to be compared AT ALL.
        :param parse_ROS2_Constants: (bool) determine if ROS2 constants are used to allow special parsing for that case
        :param comparison_method: (str) Either 'name' (for name based comparison) or 'id' (for id based comparison).
        :param document_type: (str) Either 'complete' (for a full document which includes all the fields in topics that
                                have changes in them) or 'summary' (for a report that show only the changes).


        :return: tuple of (bool, list). bool: True upon success. list: list of errors that happened along the way
        """
        self.__document_comparator.is_ignore_id = ignore_id
        self.__document_comparator.is_compare_by_name = self.determine_comparison_method(comparison_method)
        self.__document_comparator.is_summary_report = self.determine_document_type(document_type, output_formats)

        return self.__document_comparator.run_doc_compare(
            origin_dds_types_files=origin_dds_types_files,
            new_dds_types_files=new_dds_types_files,
            origin_dds_topics_types_mapping=origin_dds_topics_types_mapping,
            new_dds_topics_types_mapping=new_dds_topics_types_mapping,
            output_file_name=output_file_name,
            title=title,
            origin_version=origin_version,
            new_version=new_version,
            order_alphabetically=order_alphabetically,
            output_folder=output_folder,
            output_formats=output_formats,
            is_parse_ROS2_constants=parse_ROS2_Constants,
            is_ignore_id=ignore_id
        )
