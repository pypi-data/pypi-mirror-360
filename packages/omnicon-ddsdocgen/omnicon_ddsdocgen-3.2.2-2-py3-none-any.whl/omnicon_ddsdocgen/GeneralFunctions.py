import enum
import inspect
import os
import sys
import types
import hashlib
import traceback

from .DocxGen import DocxGen
import xml.etree.ElementTree as ET


def check_artifacts_integrity(logger):
    logger.debug("check_artifacts_integrity")
    # print(get_hash_of_template())
    if not get_hash_of_template() == '7d6d8c09b081bfe18fbae885f53967e5':
        logger.fatal("DocGen resource 'Template.Docx' was modified. Cannot start DocGen.")
        raise Exception("FATAL: DocGen resource 'Template.Docx' was modified. Cannot start DocGen.")


def get_hash_of_template(verbose=0):
    SHAhash = hashlib.md5()

    template_file = DocxGen.get_doc_template_path()
    if not os.path.exists(template_file):
        return -1

    try:
        if verbose == 1:
            print('Hashing file')
        # filepath = os.path.join(os.getcwd(), file_name)
        with open(template_file, 'rb') as f1:
            while 1:
                # Read file in as little chunks
                buf = f1.read()
                # remove carriage returns due to different file saving methods
                buf = buf.replace(b'\r', b'')
                if not buf:
                    break
                SHAhash.update(buf)

    except Exception:
        # Print the stack traceback
        raise (traceback.print_exc())
    return SHAhash.hexdigest()

def check_single_input_type(input, expected_type, parameter_name: str):
    if type(input) != type(expected_type):
        error_message: str = f"Invalid input. Parameter <{parameter_name}>: " \
                             f"'{input}' " \
                             f"is: {type(input)}. Should be {type(expected_type)}."
        raise Exception(error_message)

def check_input_list_content(list_input, parameter_name: str):
    # First check the list itself
    check_single_input_type(list_input, [], parameter_name)
    # Check the list content; Has to be str
    for i, input in enumerate(list_input):
        if type(input) != str:
            error_message: str = f"Invalid input. Within the list parameter <{parameter_name}>, entry #{i}: " \
                                 f"'{input}' " \
                                 f"is: {type(input)}. Should be a string."
            raise Exception(error_message)


def check_input_types(is_compare: bool,
                      origin_input_files_and_dirs_list: list,
                      origin_topic_names_to_types_xml_path: str,
                      output_file_name: str,
                      title: str,
                      origin_version: str,
                      new_version: str,
                      output_folder: str,
                      output_formats: list,
                      order_alphabetically: bool,
                      average_str_length: int,
                      average_sequence_length: int,
                      new_input_files_and_dirs_list: list,
                      new_topic_names_to_types_xml_path: str,
                      is_ignore_id: bool = False,
                      is_parse_ROS2_constants: bool = False,
                      comparison_method=""):
    origin_prefix = ""
    if is_compare:
        origin_prefix = "origin_"

    new_prefix = ""
    if is_compare:
        new_prefix = "new_"

    check_input_list_content(origin_input_files_and_dirs_list, f"{origin_prefix}input_files_and_dirs_list")
    check_input_list_content(new_input_files_and_dirs_list, f"{new_prefix}input_files_and_dirs_list")
    check_input_list_content(output_formats, f"output_formats")

    check_single_input_type(origin_topic_names_to_types_xml_path, "",
                                f"{origin_prefix}topic_names_to_types_xml_path")
    check_single_input_type(new_topic_names_to_types_xml_path, "", f"{new_prefix}topic_names_to_types_xml_path")
    check_single_input_type(output_file_name, "", f"output_file_name")
    check_single_input_type(title, "", f"title")
    check_single_input_type(origin_version, "", f"{origin_prefix}version")
    check_single_input_type(new_version, "", f"{new_prefix}version")
    check_single_input_type(output_folder, "", f"output_folder")
    check_single_input_type(is_ignore_id, True, f"ignore_id")
    check_single_input_type(is_parse_ROS2_constants, True, f"parse_ROS2_constants")
    check_single_input_type(order_alphabetically, True, f"order_alphabetically")
    check_single_input_type(average_str_length, 1, f"average_str_length")
    check_single_input_type(average_sequence_length, 1, f"average_sequence_length")
    check_single_input_type(average_sequence_length, 1, f"average_sequence_length")

def check_output_format_list(output_format_list):
    error_message: str
    example_message: str = "Please add a list of requested formats. For example: ['pdf'] or ['docx', 'pdf']."
    if output_format_list is None:
        error_message = f"Invalid input. Parameter <output_format> is 'None'. {example_message}"
        raise Exception(error_message)
    if len(output_format_list) == 0:
        error_message = f"Invalid input. Parameter <output_format> is an empty list. {example_message}"
        raise Exception(error_message)


def check_output_path(output_folder: str):
    # Check folder validity
    if not os.path.exists(os.path.join(os.getcwd(), output_folder)):
        error_message = f"Selected output folder '{os.path.join(os.getcwd(), output_folder)}' does not exist. " \
                        f"Please create the folder or choose an existing one."
        raise Exception(error_message)

    # Preparing an error message in advance
    error_message = f"Fatal: Cannot write into selected output folder '{os.path.join(os.getcwd(), output_folder)}'. " \
                    f"Please check writing permissions and try again."
    # Check writing permissions:
    if not os.access(os.path.join(os.getcwd(), output_folder), os.W_OK):
        raise Exception(error_message)

    # Sometimes os.access may return True even if the app does not have write permissions. So the following section
    # will try to create a temporary file into output_folder then immediately remove it.
    # If there are no write permissions then an exception will be raised.
    try:
        testfile = os.path.join(os.path.join(os.getcwd(), output_folder), 'temp.txt')
        with open(testfile, 'w') as f:
            f.write('test')
        os.remove(testfile)

    except OSError:
        raise Exception(error_message)


def check_type_files_not_empty(input_files_and_dirs_list: list):
    # Check if the list is empty
    if input_files_and_dirs_list is None:
        error_message = f"input_files_and_dirs_list is None. Cannot create an ICD without type file(s) or" \
                        f" a folder that contains at least one."
        raise Exception(error_message)



def check_progress_callback_function_signature(progress_callback_function):
    if progress_callback_function is not None:
        if not isinstance(progress_callback_function, types.FunctionType):
            error_message: str = f"Invalid input. Parameter <progress_callback_function> " \
                                 f"'{progress_callback_function}' is: " \
                                 f"{type(progress_callback_function)}. Should be of class 'function'."
            raise Exception(error_message)

    # define an allowed signature with 3 parameters
    if progress_callback_function is not None:

        # get the signature of OF
        signature = inspect.signature(progress_callback_function)
        num_params = len(signature.parameters)
        # compare the signatures
        if num_params != 3:
            raise Exception("The provided progress_bar_function has an invalid signature. "
                            "Please check README.md for progress bar function")

def check_user_avarage_inputs(average_str_length, average_sequence_length):
    check_avg_input(average_str_length, "average_str_length")
    check_avg_input(average_sequence_length, "average_sequence_length")

def check_avg_input(input: int, input_name: str):
    if input < 0:
        error_message: str = f"Invalid input. Parameter '{input_name}' Cannot be negative"
        raise Exception(error_message)

def check_list_input(user_list: list, list_name: str):
    if len(user_list) < 1:
        error_message: str = f"Invalid input. Parameter list '{list_name}' Cannot be empty"
        raise Exception(error_message)


def check_all_string_inputs(
                is_compare,
                output_file_name,
                title,
                origin_version,
                new_version):
    new_prefix = ""
    origin_prefix = ""
    if is_compare:
        new_prefix = "new_"
        origin_prefix = "origin_"
    params = {
        'output_file_name': output_file_name,
        'title': title,
        f"{origin_prefix}version": origin_version,
        f"{new_prefix}version": new_version
    }

    for parameter_name, param_value in params.items():
        if param_value == "":
            error_message: str = f"Invalid input. Parameter '{parameter_name}' is empty"
            raise Exception(error_message)

def check_linux(output_formats):
    if sys.platform.startswith('linux'):
        # Loop through each format in the list
        for frmt in output_formats:
            # Check if the current format is not 'html'
            if frmt != 'html':
                error_message: str = (
                    f"Invalid input in 'output_formats' parameter.  This application supports only 'html' reports on Linux.")
                raise Exception(error_message)

def check_output_formats_list(output_formats):
    # Verify that if this is running on linux the  only format allowed is html
    check_linux(output_formats)
    # Verify only valid formats are used
    valid_formats_list = ['html','pdf','docx']
    for output_format in output_formats:
        if output_format.lower() not in valid_formats_list:
            error_message: str = (f"Invalid input in 'output_formats'. Parameter '{output_format}' is invalid; Must be "
                                  f"one of the following: {valid_formats_list}")
            raise Exception(error_message)

def check_input(is_compare: bool,
                origin_input_files_and_dirs_list: list,
                origin_topic_names_to_types_xml_path: str,
                output_file_name: str,
                title: str,
                origin_version: str,
                output_folder: str,
                output_formats: list,
                order_alphabetically: bool,
                average_str_length:int=1,
                average_sequence_length:int=1,
                new_version: str = "v2.0",
                new_input_files_and_dirs_list: list = None,
                new_topic_names_to_types_xml_path: str = os.getcwd(),
                is_ignore_id: bool = False,
                is_parse_ROS2_constants: bool = False,
                comparison_method=""):
    """
    This function checks several aspects of the input. IF there is an issue, an exception is thrown.
    """
    # Allow this function to work even when it is called by docgen (without the parameters that has the prefix 'new')
    if not new_input_files_and_dirs_list:
        new_input_files_and_dirs_list = [""]

    check_input_types(
        is_compare=is_compare,
        origin_input_files_and_dirs_list=origin_input_files_and_dirs_list,
        origin_topic_names_to_types_xml_path=origin_topic_names_to_types_xml_path,
        output_file_name=output_file_name,
        title=title,
        origin_version=origin_version,
        new_version=new_version,
        output_folder=output_folder,
        output_formats=output_formats,
        order_alphabetically=order_alphabetically,
        new_input_files_and_dirs_list=new_input_files_and_dirs_list,
        new_topic_names_to_types_xml_path=new_topic_names_to_types_xml_path,
        is_ignore_id=is_ignore_id,
        is_parse_ROS2_constants=is_parse_ROS2_constants,
        average_str_length=average_str_length,
        average_sequence_length=average_sequence_length,
        comparison_method=comparison_method)

    check_all_string_inputs(
        is_compare=is_compare,
        output_file_name=output_file_name,
        title=title,
        origin_version=origin_version,
        new_version=new_version
    )
    check_output_formats_list(output_formats)
    if is_compare:
        check_list_input(origin_input_files_and_dirs_list, "origin_dds_types_files")
        check_list_input(new_input_files_and_dirs_list, "new_dds_types_files")
    else:
        check_list_input(origin_input_files_and_dirs_list, "dds_types_files")
    check_list_input(output_formats, 'output_formats')



    check_user_avarage_inputs(average_str_length=average_str_length, average_sequence_length=average_sequence_length)

    check_output_format_list(output_formats)

    # check if output folder even exists
    check_output_path(output_folder)  # SEE NOTE BElOW
    # NOTE: Since there is a list of requested type files, we check (for each type file) if the output file
    # is open at a later stage, when calling that type file's docGen's init method (for example, in the case
    # of a PDF, the test happens in LatexDocGen.__init__)

    check_type_files_not_empty(origin_input_files_and_dirs_list)
    check_type_files_not_empty(new_input_files_and_dirs_list)
    if is_compare:
        check_topic_files_duality(origin_topic_names_to_types_xml_path, new_topic_names_to_types_xml_path)


def check_topic_files_duality(origin_topic_names_to_types_xml_path, new_topic_names_to_types_xml_path):
    is_origin_exists = bool(origin_topic_names_to_types_xml_path)
    is_new_exists = bool(new_topic_names_to_types_xml_path)

    if (is_origin_exists and not is_new_exists) or (not is_origin_exists and is_new_exists):
        error_message = f"Input mismatch detected. For a valid comparison, please provide topic files for both data " \
                        f"models or none at all."
        raise Exception(error_message)


def get_type_name(DDS_type):
    """
    This function is used by the sort() function; The returned value is used as a key for sorting alphabetically
    :param DDS_type: An element from the list received from GetTypesBasicInfo,
    :return:
    """
    return DDS_type.fullName


def order_topics_by_xml(topic_names_to_types_xml: str, alphabet_order_list: list):
    """
    This function returns a list of topic
    :param ET:
    :param topic_names_to_types_xml:
    :param alphabet_order_list:
    :return:
    """
    topic_mapping_dict: dict = {}
    tree = ET.parse(topic_names_to_types_xml)
    root = tree.getroot()
    for topic in root.findall('domain_library/domain/topic'):
        topic_name = topic.get('name')
        dds_type = topic.get('register_type_ref')
        if topic_name in alphabet_order_list:
            topic_mapping_dict[topic_name] = dds_type

    return topic_mapping_dict


class PhaseEnum(enum.IntEnum):
    PARSE_ORIGIN_PHASE = 0
    PARSE_REVISED_PHASE = 1
    COMPARE_PHASE = 2
    WRITE_RESULTS_PHASE = 3
    SAVE_RESULTS_PHASE = 4
