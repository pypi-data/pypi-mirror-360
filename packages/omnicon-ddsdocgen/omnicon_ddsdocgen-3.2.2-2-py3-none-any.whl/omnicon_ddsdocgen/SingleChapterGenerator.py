from typing import Dict, Any

from Omnicon_GenericDDSEngine_Py import Element

from .comp import CompElement, ColumnNumbersEnum
from . import Logger


class SingleChapterGenerator:
    def __init__(self, engine, avg_seq_len=1, avg_str_len=1):
        self.current_table = None
        self.logger = Logger.add_logger(__name__)
        self.engine = engine
        self.avg_seq_len = avg_seq_len
        self.avg_str_len = avg_str_len

        self.header_titles = ("Hierarchy", "Field", "Type", "Description/Metadata")

        self.basic_types = [
            "ENUMERATION", "BOOLEAN", "UINT_8", "INT_16", "UINT_16", "INT_32", "UINT_32", "INT_64", "UINT_64",
            "FLOAT_32", "FLOAT_64", "FLOAT_128", "CHAR_8", "CHAR_16", "CHAR_32"]

        self.type_rename_dictionary = {
            "ENUMERATION": "enum", "ARRAY": "array", "SEQUENCE": "sequence", "STRING": "string", "WSTRING": "wstring",
            "STRUCTURE": "struct", "UNION": "union", "BOOLEAN": "boolean", "UINT_8": "uint8", "INT_16": "int16",
            "UINT_16": "uint16", "INT_32": "int32", "UINT_32": "uint32", "INT_64": "int64", "UINT_64": "uint64",
            "FLOAT_32": "float32", "FLOAT_64": "float64", "FLOAT_128": "float128", "CHAR_8": "char8",
            "CHAR_16": "char16", "CHAR_32": "char32"}

        # Define the numerical types
        self.numerical_types = ["UINT_8", "INT_16", "UINT_16", "INT_32", "UINT_32", "INT_64", "UINT_64",
                                "FLOAT_32", "FLOAT_64", "FLOAT_128"]

        self.char_types = ["CHAR_8", "CHAR_16", "CHAR_32"]

        self.string_types = ['WSTRING', 'STRING']

        self.union_label_to_userComment_dictionary: list[dict] = []
        self.current_union_enum_vectors_list = []

        self.sizes_dictionary = {"boolean": 1, "uint8": 1, "int16": 2, "int32": 4, "uint16": 2, "uint32": 4, "int64": 8,
                                 "uint64": 8,
                                 "float32": 4, "float64": 8, "float128": 16, "char8": 1, "char16": 2, "char32": 4,
                                 "enum": 4}
        self.mutability_overhead = 0

    @staticmethod
    def create_union_label_to_user_comment_dictionary(all_union_members_info):
        """
        This function receives the union members info vector and creates a dictionary of the union labels as keys and
        user comments as values.
        Parameter: unionMembersInfo: it is actually the "element.unionMembersInfo" vector.
        return: a dictionary of the union labels as keys and user comments as values.
        """
        dictionary = {}
        for union_member_info in all_union_members_info:
            dictionary[union_member_info.label] = union_member_info.userComment

        return dictionary

    @staticmethod
    def replace_special_xml_chars_in_user_comment(user_comment_to_replace: str) -> str:
        """"
        This function replaces the xml equivalents of '<' , '>' '<=' and '>=' to the normal chars.
        Parameter1 user_comment: The user comment (string)
        Return: the user comment
        """
        user_comment: str = user_comment_to_replace + ""
        user_comment = user_comment.replace("&lt;", "<")
        user_comment = user_comment.replace("&gt;", ">")
        user_comment = user_comment.replace("&le;", "<=")
        user_comment = user_comment.replace("&ge;", ">=")
        user_comment = user_comment.replace("&#38;", "&")
        user_comment = user_comment.replace('\r', '')
        return user_comment

    @staticmethod
    def generate_hierarchy_notation(real_level):
        hierarchy_text = ""
        # ( len(self.levels_skipped) is for taking into account the levels that were skipped):
        for i in range(2, real_level):
            hierarchy_text += "["

        return hierarchy_text

    @staticmethod
    def remove_comment_notation(user_comment_to_replace: str) -> str:
        """
        This function removes the comment notation (if exist) from a string.
         "/*" is removed from the beginning of the string, and "*/" from the end
        """
        if user_comment_to_replace != "":
            # If the beginning of the string has a "/*", remove it.
            if "/*" in user_comment_to_replace[:2]:
                user_comment_to_replace = user_comment_to_replace[2:]
            # If the end of the string has a "*/", remove it.
            if "*/" in user_comment_to_replace[len(user_comment_to_replace) - 2:]:
                user_comment_to_replace = user_comment_to_replace[:len(user_comment_to_replace) - 2]

        return user_comment_to_replace

    @staticmethod
    def remove_carriage_return_notation(user_comment_to_replace: str) -> str:
        """
        This function removes the carriage return ("\n") notation (if exist) from a string.
        """
        if user_comment_to_replace != "":
            user_comment_to_replace = user_comment_to_replace.replace('\r', '')

        return user_comment_to_replace

    @staticmethod
    def append_xml_metadata(user_comment_to_replace: str, element, is_key_allowed: bool) -> str:
        """
        This function adds min, max, default and unit XML notations to the user comment
        and Key + optional notation to the beginning of the comment
        """
        if element.isKey is True and is_key_allowed:
            # Add 'key' notation only when the elements above are defined as 'key'
            user_comment_to_replace = "*Key*" + (user_comment_to_replace if (
                    user_comment_to_replace == "") else ("\n" + user_comment_to_replace))
        if element.isOptional is True:
            user_comment_to_replace = "*Optional*" + (user_comment_to_replace if (
                    user_comment_to_replace == "") else ("\n" + user_comment_to_replace))

        xml_metadata = ""
        if element.unit != "":
            xml_metadata += "\n"
            xml_metadata += "Unit: " + element.unit
        if element.min != "":
            xml_metadata += "\n"
            xml_metadata += "Min: " + element.min
        if element.max != "":
            xml_metadata += "\n"
            xml_metadata += "Max: " + element.max
        if element.defaultValue != "":
            xml_metadata += "\n"
            xml_metadata += "Default: " + element.defaultValue

        # Avoid adding redundant "\n" to the beginning of description if xml_metadata exists
        if user_comment_to_replace == "" and xml_metadata != "":
            return xml_metadata[1:]
        else:
            return user_comment_to_replace + xml_metadata

    @staticmethod
    def get_sequence_or_string_length_value(length: int) -> int:
        """"
        This function return the string/sequence length notation.
        Parameter1: sequence/string actual length.
        Return: if "unbounded" length (2147483647) - returns "-1"; else return the actual length.
        """
        if length == 2147483647:
            return -1
        return length

    @staticmethod
    def write_special_data_of_enumeration(element: Element, row_data_list: list, comp_element: CompElement):
        """"
        This function Handles the Enumeration type elements and exports the appropriate data to the ICD document.
        :param element: The introspection element that represent the enum element.
        :Param element - The current element from the introspection
        :param row_data_list: the table row data that this function writes into
        :return: None
        """
        i = 0
        # See what description is already there:
        lineDescription = row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM]

        # Go over enum elements
        for enumElement in element.enumMembers:
            if i == 0:
                # When it's the first enum value:
                if lineDescription != "":
                    # When there's something else in the description, write a new empty line
                    lineDescription += "\n\n"
                lineDescription += "Enum values:"

            # Write the  new enum in a new line:
            lineDescription += f"\n{enumElement.name} = {str(enumElement.value)}"
            if enumElement.isDefault:
                lineDescription += " : Default "
            if enumElement.userComment != "":
                lineDescription += f" ({enumElement.userComment})"

            comp_element.add_enum_element_to_list(
                enumElement.name, enumElement.value, enumElement.userComment, enumElement.isDefault)

            i = i + 1

        row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] = lineDescription

    @staticmethod
    def write_union_enumeration_of_discriminator(element, row_data_list, comp_element):
        """"
        This function writes all Enumeration options of union elements and exports the appropriate data to
        the ICD document.
        Parameter1: element - The current element from the introspection
        Parameter2: row_cells - The row of the table this function writes into.
        """
        # First see if a new line is in order:
        if row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] != "":
            # When a new line IS needed:
            row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] += "\n"

        row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] += "Union discriminator options: "

        if element.typeKindName == "ENUMERATION":
            # Create a dictionary that holds the enum values as key and the enum names as the value.
            union_enum_dictionary = {}
            # Create a dictionary that holds the enum values as key and that enum's comment as the value.
            union_enum_comments_dictionary = {}
            # First, get only the enum values relevant to the union and put into both dictionaries:
            for item in element.unionMembersInfo:
                union_enum_dictionary[item.label] = ""
                union_enum_comments_dictionary[item.label] = ""
            # Then retrieve the enum names and comments from the enumMap:
            for enum_member in element.enumMembers:
                if enum_member.value in union_enum_dictionary:
                    union_enum_dictionary[enum_member.value] = enum_member.name
                    union_enum_comments_dictionary[enum_member.value] = enum_member.userComment

            # Now write the information we just gathered into the table:
            for key, value in union_enum_dictionary.items():

                row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] += f"\n{value} = {str(key)}"

                comp_element.add_enum_element_to_list(value, key, union_enum_comments_dictionary[key], False)

                if union_enum_comments_dictionary[key] != "":
                    row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] += \
                        f" ({union_enum_comments_dictionary[key]})"
        else:
            # When it is not an enum based union (when based on numbers)
            is_first_instance = True

            for item in element.unionMembersInfo:
                # Add a nameless enum element (which means it is not an enum, just a number)
                comp_element.add_enum_element_to_list("", item.label, "", False)
                if is_first_instance is True:
                    is_first_instance = False
                    row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] += str(item.label)
                else:
                    row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM] += ", " + str(item.label)
        comp_element.add_data_to_comp_element(row_data_list)

    def determine_topic_level_comment(self, element_list: list) -> str:
        """
        This function returns the only the topic's type comment. This operation is required when the topic's type
        inherits from other types, in which case the other type's comments override the topic's comment.
        :param element_list: list of elements that describe the introspection structure
        :return: A string.
        """
        self.logger.debug(self.determine_topic_level_comment.__name__)
        # The first element is the topic's type, so take only that into consideration.
        if element_list[0].userComment != "":
            return self.modify_topic_level_comment_to_icd_needs(element_list[0].userComment)
        return ""

    def calculate_root_comp_element_volumes(self, comp_element: CompElement):
        volumes_list = self.calculate_struct_volume(comp_element)
        comp_element.update_message_volume(volumes_list)

    def calculate_struct_volume(self, comp_element: CompElement):
        min_volume = self.mutability_overhead
        avg_volume = self.mutability_overhead
        max_volume = self.mutability_overhead

        for son in comp_element.sons_list:
            self.logger.debug(f"Calculating {son.type_kind_name} '{son.field_name}'")
            self.calculate_type_volume(son)

            min_volume += son.min_message_volume
            avg_volume += son.avg_message_volume

            if max_volume == -1 or son.max_message_volume == -1:
                max_volume = -1
            else:
                max_volume += son.max_message_volume

        return [min_volume, avg_volume, max_volume]

    def calculate_type_volume(self, comp_element: CompElement, name: str = ""):
        if name != "":
            type_kind_name = name
        else:
            type_kind_name = comp_element.type_kind_name
        if type_kind_name in self.sizes_dictionary.keys():
            volumes_list = self.calculate_primitive_volume(type_kind_name)

        elif type_kind_name == 'struct':
            volumes_list = self.calculate_struct_volume(comp_element)

        elif type_kind_name == 'union':
            volumes_list = self.calculate_union_volume(comp_element)

        elif type_kind_name.startswith("string<") or type_kind_name.startswith("wstring<"):
            volumes_list = self.calculate_string_volume(type_kind_name)

        elif ']' in type_kind_name or '>' in type_kind_name:
            volumes_list = self.calculate_collection_volume(comp_element)
        else:
            raise Exception(f"A case wasn't taken care of at calculate_type_volume: {comp_element.type_kind_name}")

        comp_element.update_message_volume(volumes_list)
        return volumes_list

    def calculate_average_seq_or_str_length(self, collection_length):
        if collection_length == -1:
            return self.avg_seq_len

        return min(self.avg_seq_len, collection_length)

    def calculate_string_volume(self, type_kind_name: str):
        size_factor = 1
        if type_kind_name.startswith("wstring"):
            size_factor = 2
        # Split the input string to extract the length
        string_len = int(type_kind_name.split('<')[1].split('>')[0])
        avg_len = self.calculate_average_seq_or_str_length(string_len)

        min_volume = self.mutability_overhead + 4
        avg_volume = self.mutability_overhead + 4 + size_factor * avg_len + 1
        if '-1' in type_kind_name:
            max_volume = -1
        else:
            max_volume = self.mutability_overhead + 4 + size_factor * string_len + 1

        return [min_volume, avg_volume, max_volume]

    def calculate_union_volume(self, union_comp_element: CompElement):
        min_volumes_list = []
        avg_volume_list = []
        max_volume_list = []

        for son in union_comp_element.sons_list:
            if "(D)" in son.hierarchy or son.field_name == 'discriminator':
                continue
            else:
                volumes_list = self.calculate_type_volume(son)
                son.update_message_volume(volumes_list)
                min_volumes_list.append(son.min_message_volume)
                avg_volume_list.append(son.avg_message_volume)
                max_volume_list.append(son.max_message_volume)

        min_volume = self.mutability_overhead + 4 + min(min_volumes_list)
        avg_volume = self.mutability_overhead + 4 + int(sum(avg_volume_list) / len(avg_volume_list))
        if -1 in max_volume_list:
            max_volume = -1
        else:
            max_volume = self.mutability_overhead + 4 + max(max_volume_list)

        return [min_volume, avg_volume, max_volume]

    def calculate_primitive_volume(self, type_kind_name: str):
        min_volume = self.mutability_overhead + self.sizes_dictionary[type_kind_name]
        avg_volume = self.mutability_overhead + self.sizes_dictionary[type_kind_name]
        max_volume = self.mutability_overhead + self.sizes_dictionary[type_kind_name]

        return [min_volume, avg_volume, max_volume]

    @staticmethod
    def split_collection_type_kind_name(input_string):
        # Split the input string by '<' or '['
        parts = input_string.split('<')
        if len(parts) < 2:
            parts = input_string.split('[')

        # Determine the data type based on the first part
        data_type = parts[0]

        # Extract data length using string slicing
        data_length = parts[1].split('>')[0] if '>' in parts[1] else parts[1].split(']')[0]

        # Extract string length if available, otherwise use ""
        if len(parts) > 2:
            str_len = parts[2].split('>')[0]
        else:
            str_len = ""

        if '>' in parts[1]:
            content_type = parts[1].split('>')[1]
        elif ']' in parts[1]:
            content_type = parts[1].split(']')[1]
        else:
            content_type = ""
        content_type = content_type.replace(' of ', '')
        return [data_type, int(data_length), content_type, str_len]

    def calculate_collection_volume(self, comp_element: CompElement):
        min_volume: int
        avg_volume: int
        max_volume: int

        # Extract the data type, data length, content type, and the length of the string-content (if applicable)
        [data_type, data_length, content_type, str_len] = \
            SingleChapterGenerator.split_collection_type_kind_name(comp_element.type_kind_name)

        if content_type == "":
            [content_min_volume, content_avg_volume, content_max_volume] = self.calculate_primitive_volume(data_type)
        elif content_type in ['string', 'wstring']:
            # When the content is string/wstring: calculate the content sizes
            [content_min_volume, content_avg_volume, content_max_volume] = \
                self.calculate_string_volume(f"{content_type}<{str_len}>")
        elif content_type == 'union':
            [content_min_volume, content_avg_volume, content_max_volume] = self.calculate_union_volume(comp_element)

        elif content_type == 'struct':
            [content_min_volume, content_avg_volume, content_max_volume] = self.calculate_type_volume(comp_element,
                                                                                                      content_type)
        else:
            # When content_type is either 'sequence' or 'array':
            if comp_element.sons_list[0].type_kind_name != '-':
                [content_min_volume, content_avg_volume, content_max_volume] = \
                    self.calculate_type_volume(comp_element.sons_list[0])
            else:
                # When the element within the collection is a union discriminator
                [content_min_volume, content_avg_volume, content_max_volume] = \
                    self.calculate_type_volume(comp_element.sons_list[1])

        if data_type == "array" or '[' in comp_element.type_kind_name:
            min_volume = self.mutability_overhead + data_length * content_min_volume
            avg_volume = self.mutability_overhead + data_length * content_avg_volume
            max_volume = self.mutability_overhead + data_length * content_max_volume

        elif data_type == "sequence" or '<' in comp_element.type_kind_name:
            avg_len = self.calculate_average_seq_or_str_length(data_length)

            min_volume = self.mutability_overhead + 4
            avg_volume = self.mutability_overhead + 4 + avg_len * content_avg_volume
            max_volume = self.mutability_overhead + 4 + data_length * content_max_volume
        else:
            raise Exception(
                f"A case wasn't taken care of at calculate_collection_volume: {comp_element.type_kind_name}")

        if content_max_volume == -1 or data_length == -1:
            max_volume = -1

        return [min_volume, avg_volume, max_volume]

    def generate_single_chapter(self, topic_name, type_name: str):
        """
        This function is called from the documentation_generator module for each chapter required for the ICD.
        This is where the top level introspection is handled. Next introspections related to this chapter will be
        take place in recursive_type_introspect function.
        :param topic_name: The name of the chapter.
        :param type_name: the type to introspect.
        :return:
        """
        self.logger.debug(self.generate_single_chapter.__name__)
        # Get the introspection product, a list of elements that hold information about every field  within a given type
        element_list: list = self.get_introspection_list(type_name)

        root_element = CompElement()

        is_ignore_next_element = False
        # Get the combined topic level comments:
        topic_level_comment = self.determine_topic_level_comment(element_list)
        # Go over the elements: ('enumerate' just puts the element_index of the iteration into i)
        for element_index, element in enumerate(element_list):
            if element.level == 1:
                # When a chapter has not yet been created - create one
                # self.create_new_chapter_with_table(topic_name, type_name, element, topic_level_comment)
                root_element.field_name = type_name
                root_element.introspection_element = element
                root_element.type_kind_name = self.type_rename_dictionary[element.typeKindName]
                root_element.user_comment = topic_level_comment

                # Nothing to do really in the first level, which is the level that holds the type itself.
                self.logger.debug(f"Passing level 1 of {element.name}")

            if element.level == 2:
                self.logger.debug(f"handling topic {topic_name}: {element.name}")

                if is_ignore_next_element:
                    # When the previous level-2 element inherited from parent - means this one is the parent
                    # and needs to be ignored
                    if element.parentDataTypeName == "":
                        # When his one has a parent as well - means the next one is to be ignored as well
                        is_ignore_next_element = False
                        continue
                    else:
                        continue
                # When this element is a direct son of the introspected type: see which type it is and act accordingly.
                self.handle_element_types(element_index, element_list, element.level, is_key_allowed=True,
                                          father_comp_element=root_element)
                # Check if has parent. if so, next level-2-element is what the current element inherited from.
                # In which case ignore next element (skip to next element that doesnt have a parent)
                if element.typeKindName == 'STRUCTURE':
                    if element.parentDataTypeName != "":
                        is_ignore_next_element = True

        self.logger.info(f"Finished introspecting topic {topic_name} with type {type_name}")
        return root_element

    def get_introspection_list(self, type_name: str) -> list:
        """
        This function does the actual introspection and returns the element list
        :param type_name: The type we want to introspect and inspect.
        :return: the introspection product: element list
        """
        self.logger.debug(self.get_introspection_list.__name__)
        # instrospect the type:
        introspected_type = self.engine.IntrospectType(type_name)

        # Check if the introspection went ok:
        if introspected_type is None:
            error_message: str = f"Could not find '{type_name}' in provided files!"
            self.logger.warning(error_message)
            raise Exception(error_message)

        return introspected_type.structure

    def recursive_type_introspect(
            self, type_name: str, real_level: int, is_key_allowed: bool, father_comp_element: CompElement):
        """
        This function introspects a given type and goes over its elements ONLY AT THE SECOND LEVEL, which is the level
        of the type's 'sons'.
        :param real_level: The true level of the type. Since we do recursive introspection, this is the parameter that
        maintains the true level trough out the recursive operation.
        :param type_name: The type we want to introspect and inspect.
        :param is_key_allowed: Specifies whether the elements at higher levels (directly above this one) have
                               'key' notation in them.
        :return: None
        """
        self.logger.debug(f"recursive_type_introspect: Introspecting: {type_name}")
        is_ignore_next_element = False
        # Get the introspection product, a list of elements that hold information about every field  within a given type
        element_list: list = self.get_introspection_list(type_name)
        # Go over the elements: ('enumerate' just puts the element_index of the iteration into i)
        for element_index, element in enumerate(element_list):
            # Update the real level- needed because we do an introspection to (for example) nested structs
            current_level = real_level + element.level
            if element.level == 1:
                # Nothing to do really in the first level, which is the level that holds the type itself.
                self.logger.debug(f"Passing level 1 of {element.name}")

            if element.level == 2:
                self.logger.debug(f"Handling {type_name}.{element.name}")

                if is_ignore_next_element:
                    # When the previous level-2 element inherited from parent - means this one is the parent
                    # and needs to be ignored
                    if element.parentDataTypeName == "":
                        # When his one has a parent as well - means the next one is to be ignored as well
                        is_ignore_next_element = False
                        continue
                    else:
                        continue

                # When this element is a direct son of the introspected type: see which type it is and act accordingly.
                self.handle_element_types(element_index, element_list, current_level, is_key_allowed,
                                          father_comp_element)

                # Check if has parent. if so, next level-2-element is what the current element inherited from.
                # In which case ignore next element (skip to next element that doesnt have a parent)
                if element.typeKindName == 'STRUCTURE':
                    if element.parentDataTypeName != "":
                        is_ignore_next_element = True

        self.logger.debug(f"Finished introspecting type: {type_name}")

    def create_new_chapter_with_table(self, topic: str, dds_type: str, element: Any, topic_level_comment: str) -> None:
        """
        This function adds a new heading (i.e. chapter) and a new table to the ICD.
        :param topic_level_comment: The comment to add to add above the table.
        :param topic: A string that contains the topic name. NOTE: When the user doesn't provide the topic-to-type XML.
                      This parameter will contain an empty string ('').
        :param dds_type: A string that contains the type name.
        :param element: the current element.
        """
        self.logger.debug(self.create_new_chapter_with_table.__name__)
        # Check if this is a duplicate type (happens when the type inherits from another type)
        if element.parentDataTypeName != "":
            # When it IS a duplicate, do not create a new chapter - otherwise the chapter will be created multiple times
            return

        self.document.add_new_page()

        # Write the topic as the heading:
        if topic != "":
            # When the user provided topic-to-types XML:
            self.document.add_chapter(topic, dds_type)

        else:
            self.document.add_chapter(dds_type, "")  # level for styling

        self.document.add_description(topic_level_comment)
        #
        # if element.parentDataTypeName != "":
        #     self.document.add_new_line(self.modify_user_comment_to_icd_needs(element))

        # Create the table
        self.current_table = self.document.add_table_header(self.header_titles)
        return self.current_table

    def create_row_data_list(self, element, real_level, is_key_allowed):
        self.logger.debug(self.create_row_data_list.__name__)
        hierarchy: str = self.generate_hierarchy_notation(real_level)
        field: str = element.name
        type_notation: str = self.generate_type_notation(element)
        description_and_metadata = self.modify_user_comment_to_icd_needs(element, is_key_allowed)

        return [hierarchy, field, type_notation, description_and_metadata]

    def handle_element_types(self, element_index, element_list, real_level, is_key_allowed, father_comp_element):
        """
        This function gets element list and an index (which gives a specific element, hence the 'handle element' part
        of this function's name) and adds takes action according to the element's type.
        :param real_level: The true level of the type. Since we do recursive introspection, this is the parameter that
                            maintains the true level trough out the recursive operation.
        :param element_list: The introspection product, a list of elements that hold information about every field
                             within a given type.
        :param element_index: The index of the element that needs handling
        :param is_key_allowed: Specifies whether the elements at higher levels (directly above this one) have
                               'key' notation in them.
        :return: None
        """
        self.logger.debug(self.handle_element_types.__name__)
        element = element_list[element_index]

        if element.name == 'discriminator' and len(element.unionMembersInfo) > 0:
            # When the element is a union discriminator, it' already in the table - so don't do a thing.
            return

        # See if we need to add an extra row that describes which union it is:
        if len(element.unionLabels) > 0:
            # When the current element is a part of a union - need to add the discriminator number row:
            self.add_extra_row_for_union_option_element(element, real_level, father_comp_element)

        self.handle_types(element_index, element_list, real_level, is_key_allowed, father_comp_element)

    def handle_types(self, element_index, element_list, real_level, is_key_allowed, father_comp_element):
        """
        This function gets element list and an index (which gives a specific element, hence the 'handle element' part
        of this function's name) and adds takes action according to the element's type.
        :param real_level: The true level of the type. Since we do recursive introspection, this is the parameter that
                            maintains the true level trough out the recursive operation.
        :param element_list: The introspection product, a list of elements that hold information about every field
                             within a given type.
        :param element_index: The index of the element that needs handling
        :param is_key_allowed: Specifies whether the elements at higher levels (directly above this one) have
                               'key' notation in them.
        :return: None
        """

        element = element_list[element_index]
        row_data_list = self.create_row_data_list(element, real_level, is_key_allowed)
        # Find out whether this element's descendants will be allowed to show the 'key' notation:
        is_key_allowed: bool = element.isKey

        # Then See if it's a number:
        if element.typeKindName in self.numerical_types:
            self.handle_regular_primitive_element(element, row_data_list, father_comp_element)

        # See if it's a char:
        elif element.typeKindName in self.char_types:
            self.handle_regular_primitive_element(element, row_data_list, father_comp_element)

        # See if it's a string:
        elif element.typeKindName in self.string_types:
            self.handle_string_element(element, row_data_list, father_comp_element)

        # See if it's a bool:
        elif element.typeKindName == 'BOOLEAN':
            self.handle_regular_primitive_element(element, row_data_list, father_comp_element)

        # See if it's an enum:
        elif element.typeKindName == 'ENUMERATION':
            self.handle_enum_element(element, row_data_list, father_comp_element)

        # See if it's a char:
        elif element.typeKindName == 'STRUCTURE':
            self.handle_struct_element(element, row_data_list, real_level, is_key_allowed, father_comp_element)

        # See if it's an array:
        elif element.typeKindName == 'ARRAY' or element.typeKindName == 'SEQUENCE':
            self.handle_collection_element(element_index, element_list, row_data_list, real_level, is_key_allowed,
                                           father_comp_element)
        #
        # See if it's a union:
        elif element.typeKindName == 'UNION':
            self.handle_union_element(element_index, element_list, row_data_list, real_level, is_key_allowed,
                                      father_comp_element)

        else:
            self.logger.debug(f"Unsorted: {element.name}")

    def modify_topic_level_comment_to_icd_needs(self, comment):
        """
        This function prepares the topic level comment for the ICD: replaces special chars and remove the comment
        notations.
        :param comment: the comment that needs modifications
        :return: A comment, ready to be added
        """
        self.logger.debug(self.modify_topic_level_comment_to_icd_needs.__name__)
        user_comment: str = self.replace_special_xml_chars_in_user_comment(comment)
        user_comment = self.remove_comment_notation(user_comment)
        return user_comment.rstrip()

    def modify_user_comment_to_icd_needs(self, element, is_key_allowed) -> str:
        """
        This function prepares the user comment for the ICD: replaces special chars, remove the comment notations and
        appends xml metadata.
        :param element: the current introspection element
        :param is_key_allowed: Specifies whether the elements at higher levels (directly above this one) have
                               'key' notation in them.
        :return: A comment, ready to be added
        """
        self.logger.debug(self.modify_user_comment_to_icd_needs.__name__)
        user_comment: str = self.replace_special_xml_chars_in_user_comment(element.userComment)
        user_comment = self.remove_comment_notation(user_comment)
        user_comment = self.remove_carriage_return_notation(user_comment)
        user_comment = self.append_xml_metadata(user_comment, element, is_key_allowed)
        return user_comment.rstrip()

    def generate_type_notation(self, element):
        self.logger.debug(self.generate_type_notation.__name__)
        type_text: str
        if (element.typeKindName == "ARRAY") or (element.typeKindName == "SEQUENCE"):
            # Check the content type of the array/sequence:
            content_name = element.contentTypeKindName
            if content_name in self.basic_types:
                # When it's a primitive type:
                type_text = self.type_rename_dictionary.get(content_name)
            else:
                type_text = \
                    self.type_rename_dictionary.get(element.typeKindName, element.typeKindName)
        # When current element type is NOT an array or a sequence:
        else:
            # Write into "Type" column (If the name is in the dictionary, use it. if not, use the original name):
            type_text = \
                self.type_rename_dictionary.get(element.typeKindName, element.typeKindName)

        return type_text

    def handle_regular_primitive_element(self, element, row_data_list, father_comp_element):
        """
        Adds a regular element row to the document
        :param row_data_list: the table row data that this function writes into
        :param element: The introspection element that represent the numerical element. This element holds a lot of
                        valuable information about the numerical element
        :return: None
        """
        self.logger.debug(f"Handling {element.name}")

        new_son_comp_element = CompElement(introspection_element=element, id=element.id)
        father_comp_element.sons_list.append(new_son_comp_element)
        new_son_comp_element.add_data_to_comp_element(row_data_list)

        # create_doc_from_structured_doc_data

    def handle_string_element(self, element, row_data_list, father_comp_element, collection_id=None):
        """
        Adds a string element to the table.
        :param row_data_list: the table row data that this function writes into
        :param element: The introspection element that represent the char element. This element holds a lot of valuable
                        information about the element
        :param collection_id: The id of the collection element that holds this element. When no collection is
                              holding this element, this parameter will be None
        :return: None
        """
        self.logger.debug(f"Handling {element.name}")
        row_data_list[ColumnNumbersEnum.TYPE_COLUMN_NUM] += \
            f"<{str((SingleChapterGenerator.get_sequence_or_string_length_value(element.length)))}>"

        # The following section helps keep track of the IDs in case this is the content of a collection element
        current_id = element.id
        content_id = None
        if collection_id is not None:
            current_id = collection_id
            content_id = element.id
        new_son_comp_element = CompElement(introspection_element=element, id=current_id, content_id=content_id)
        father_comp_element.sons_list.append(new_son_comp_element)
        new_son_comp_element.add_data_to_comp_element(row_data_list)

        # create_doc_from_structured_doc_data

    def handle_enum_element(self, element, row_data_list, father_comp_element, collection_id=None):
        """
        Adds A number (either 0 or a random number, depends on the 'is_random' parameter)
        into the given local_dict. A string is used because this is for the JSON form of injecting messages.
        :param element: The introspection element that represent the enum element.
        :param row_data_list: the table row data that this function writes into
        :param row_data_list: the table row data that this function writes into
        :param collection_id: The id of the collection element that holds this element. When no collection is
                              holding this element, this parameter will be None
        :return:
        """
        self.logger.debug(f"Handling {element.name}")

        # The following section helps keep track of the IDs in case this is the content of a collection element
        current_id = element.id
        content_id = None
        if collection_id is not None:
            current_id = collection_id
            content_id = element.id
        new_son_comp_element = CompElement(introspection_element=element, id=current_id, content_id=content_id)
        # Adding user comment BEFORE enum data is added
        new_son_comp_element.full_description = row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM]
        father_comp_element.sons_list.append(new_son_comp_element)

        self.write_special_data_of_enumeration(element, row_data_list, new_son_comp_element)
        new_son_comp_element.add_data_to_comp_element(row_data_list)
        # create_doc_from_structured_doc_data

    def write_special_data_of_collection(self, element, row_data_list):
        """"
        This function adds the data special to collection type elements (arrays and sequences) to the
        row_data_list which will be inserted to the ICD.
        Param: element - The current element from the introspection
        :param element: The introspection element that represent the enum element.
        :param row_data_list: the table row data that this function writes into
        :return: None
        """
        self.logger.debug(self.write_special_data_of_collection.__name__)
        # Make a short name for row_data_list[ColumnNumbersEnum.TYPE_COLUMN_NUM]
        type_column_text = row_data_list[ColumnNumbersEnum.TYPE_COLUMN_NUM]

        if element.typeKindName == "ARRAY":
            self.logger.debug(f"Adding array stuff. type_column_text: {type_column_text}")
            # Add data into "Type" column with "[" to arrays
            type_column_text += f"[{str(element.length)}]"
            self.logger.debug(f"type_column_text: {type_column_text}")

        elif element.typeKindName == "SEQUENCE":
            # Add data into "Type" column with "<" to sequences
            type_column_text += f"<{str(SingleChapterGenerator.get_sequence_or_string_length_value(element.length))}>"

        if element.contentTypeKindName not in self.basic_types:
            type_column_text += \
                f" of {self.type_rename_dictionary.get(element.contentTypeKindName, element.contentTypeKindName)}"

        row_data_list[ColumnNumbersEnum.TYPE_COLUMN_NUM] = type_column_text

    def handle_struct_element(self, element, row_data_list, real_level, is_key_allowed, father_comp_element,
                              collection_id=None):
        """

        :param real_level: The true level of the type. Since we do recursive introspection, this is the parameter that
                            maintains the true level trough out the recursive operation.
        :param element: The introspection element that represent the struct element.
        :param row_data_list: the table row data that this function writes into
        :param is_key_allowed: Specifies whether the elements at higher levels (directly above this one) have
                               'key' notation in them.
        :param collection_id: The id of the collection element that holds this element. When no collection is
                              holding this element, this parameter will be None
        :return: None
        """
        self.logger.debug(f"Handling {element.name}")

        # The following section helps keep track of the IDs in case this is the content of a collection element
        current_id = element.id
        content_id = None
        if collection_id is not None:
            current_id = collection_id
            content_id = element.id
        new_son_comp_element = CompElement(introspection_element=element, id=current_id, content_id=content_id)

        father_comp_element.sons_list.append(new_son_comp_element)
        new_son_comp_element.add_data_to_comp_element(row_data_list)

        # create_doc_from_structured_doc_data# See explanation below:
        # We're about to send rel_level-1 because levels start at 1 and  we calculate real_level + element.level.  Since
        # level 1 of the next introspection is the current real level, then the real level would be increased
        # for no  reason.
        self.recursive_type_introspect(type_name=element.dataTypeName, real_level=real_level - 1,
                                       is_key_allowed=is_key_allowed, father_comp_element=new_son_comp_element)

    def handle_collection_element(
            self, element_index, element_list, row_data_list, real_level, is_key_allowed, father_comp_element):
        """
        This function is called when the current element is a collection element, i.e. array/sequence.
        :param element_index: Index of current element
        :param element_list: The list of elements (the product of introspection structure)
        :param row_data_list: The table row data
        :param real_level: The true level of the type. Since we do recursive introspection, this is the parameter that
                            maintains the true level trough out the recursive operation.
        :param is_key_allowed: Specifies whether the elements at higher levels (directly above this one) have
                               'key' notation in them.
        :return: None
        """
        self.logger.debug(self.handle_collection_element.__name__)
        element = element_list[element_index]
        self.write_special_data_of_collection(element, row_data_list)

        if element.contentTypeKindName in self.string_types:
            self.handle_string_element(element_list[element_index + 1], row_data_list, father_comp_element, element.id)
        #
        elif element.contentTypeKindName == 'ENUMERATION':
            self.handle_enum_element(element_list[element_index + 1], row_data_list, father_comp_element, element.id)

        elif element.contentTypeKindName == 'UNION':
            self.handle_union_element(element_index + 1, element_list, row_data_list, real_level, is_key_allowed,
                                      father_comp_element, element.id)

        elif element.contentTypeKindName == 'STRUCTURE':
            self.handle_struct_element(element_list[element_index + 1], row_data_list, real_level, is_key_allowed,
                                       father_comp_element, element.id)

        # If the element's content is none of the above, it is either a primitive or a collection;
        # In both cases the table row need to be added here
        else:
            new_son_comp_element = CompElement(
                introspection_element=element, id=element.id, content_id=element_list[element_index + 1].id)
            new_son_comp_element.add_data_to_comp_element(row_data_list)
            father_comp_element.sons_list.append(new_son_comp_element)

            # create_doc_from_structured_doc_data
            # Make
            father_comp_element = new_son_comp_element

        if element.contentTypeKindName == 'ARRAY' or element.contentTypeKindName == 'SEQUENCE':
            self.handle_types(element_index + 1, element_list, real_level + 1, is_key_allowed, father_comp_element)

        # else:
        #     self.logger.debug(f"Unsorted ARR: {element.name}")

    def create_row_data_list_for_union_option_row(self, real_level):
        """
        This function is called whenever the current element is a union option, and the extra row (that describes which
        union option it is) needs to be added. This function creates the relevant row data
        :param real_level: The true level of the element. Since we do recursive introspection, this is the parameter
                           that maintains the true level trough out the recursive operation.
        :return:
        """
        self.logger.debug(self.create_row_data_list_for_union_option_row.__name__)
        hierarchy: str = self.generate_hierarchy_notation(real_level) + "(D)"
        field: str = "discriminator = "
        type_notation: str = "-"
        description_and_metadata = ""

        return [hierarchy, field, type_notation, description_and_metadata]

    def map_enum_members_vector_to_enum_value_vs_index(self) -> Dict[int, str]:
        """
        This function receives a vector of the enum elements and returns a dictionary that holds the enum value as the
        key and the vector index as a value.
        :return: Either a dictionary that holds the enum value as the key and the enum name as a value,
                 OR None if the vector is empty
        """
        self.logger.debug("map_enum_members_vector_to_enum_value_vs_index")
        names_vs_index_of_enumMembers_vector: Dict[int, str] = {}
        if self.current_union_enum_vectors_list[-1] is not None:
            for i in range(len(self.current_union_enum_vectors_list[-1])):
                names_vs_index_of_enumMembers_vector[self.current_union_enum_vectors_list[-1][i].value] = \
                    self.current_union_enum_vectors_list[-1][i].name

        return names_vs_index_of_enumMembers_vector

    def add_extra_row_for_union_option_element(self, element, real_level, father_comp_element):
        """
        The current ICD format does not describe which union option the current element belongs to. For that reason,
        this function creates an additional table row to display the union option this element belongs to.
        :param real_level: The true level of the type. Since we do recursive introspection, this is the parameter that
                            maintains the true level trough out the recursive operation.
        :param element: The introspection element that represent the struct element.
        :return:
        """
        self.logger.debug(self.add_extra_row_for_union_option_element.__name__)

        # Not adding an element here: this is a ghost table row created for the user to understand more about the union.
        new_son = CompElement()
        father_comp_element.sons_list.append(new_son)

        # Creating custom row_data for this row
        row_data_list = self.create_row_data_list_for_union_option_row(real_level)

        # Create a list to help us make sure there are no duplicate descriptions.
        description_list = []
        # Map the current_union_enum_vector to name vs index
        enum_member_map = self.map_enum_members_vector_to_enum_value_vs_index()
        # Add the union labels to the "field" column:
        i = 0
        for union_label in element.unionLabels:
            if i > 0:
                # When this is not the first label for the same union option, add : " || "
                row_data_list[ColumnNumbersEnum.FIELD_COLUMN_NUM] += " || "

            if self.current_union_enum_vectors_list[-1] is not None:
                # When the union doesnt use enums, just write the label:
                if union_label in enum_member_map:
                    row_data_list[ColumnNumbersEnum.FIELD_COLUMN_NUM] += enum_member_map.get(union_label)
            else:
                row_data_list[ColumnNumbersEnum.FIELD_COLUMN_NUM] += str(union_label)

            i = i + 1

        new_son.add_data_to_comp_element(row_data_list)

        # Finally - add the extra row to the document
        # create_doc_from_structured_doc_data

    def handle_discriminator_element(self, element, real_level, father_comp_element):
        """
        This function creates and adds the discriminator table row.
        :param element: The introspection element that represent the discriminator element.
        :param real_level: The true level of the discriminator. Since we do recursive introspection, this is the
                            parameter that maintains the true level trough out the recursive operation.
        :return: None
        """
        self.logger.debug("handle_discriminator_element")
        row_data_list = self.create_row_data_list(element, real_level, False)

        new_son_comp_element = CompElement(element, is_discriminator=True)
        father_comp_element.sons_list.append(new_son_comp_element)

        self.write_union_enumeration_of_discriminator(element, row_data_list, new_son_comp_element)

        self.union_label_to_userComment_dictionary.append(
            self.create_union_label_to_user_comment_dictionary(element.unionMembersInfo))

        if element.typeKindName == "ENUMERATION":
            self.current_union_enum_vectors_list.append(element.enumMembers)
        else:
            self.current_union_enum_vectors_list.append(None)

        # create_doc_from_structured_doc_data

    def handle_union_element(
            self, element_index, element_list, row_data_list, real_level, is_key_allowed, father_comp_element,
            collection_id=None):
        """
        This function handles the case wherer the current element is a union element.
        :param element_index: Index of current element
        :param element_list: The list of elements (the product of introspection structure)
        :param row_data_list: The table row data
        :param real_level: The true level of the type. Since we do recursive introspection, this is the parameter that
                            maintains the true level trough out the recursive operation.
        :param is_key_allowed: Specifies whether the elements at higher levels (directly above this one) have
                               'key' notation in them.
        :param collection_id: The id of the collection element that holds this element. When no collection is
                              holding this element, this parameter will be None
        :return: None
        """
        self.logger.debug(self.handle_union_element.__name__)
        element = element_list[element_index]
        self.logger.debug(f"Handling {element.name}")

        # The following section helps keep track of the IDs in case this is the content of a collection element
        current_id = element.id
        content_id = None
        if collection_id is not None:
            current_id = collection_id
            content_id = element.id
        new_son_comp_element = CompElement(introspection_element=element, id=current_id, content_id=content_id)

        father_comp_element.sons_list.append(new_son_comp_element)
        new_son_comp_element.add_data_to_comp_element(row_data_list)

        # create_doc_from_structured_doc_data
        # Handle the discriminator row:
        self.handle_discriminator_element(element_list[element_index + 1], real_level + 1, new_son_comp_element)

        self.recursive_type_introspect(element.dataTypeName, real_level - 1, is_key_allowed,
                                       new_son_comp_element)  # See explanation below:
        # we send rel_level-1 because levels start at 1 and  we calculate real_level + element.level.  Since
        # level 1 of the next introspection is the current real level, then the real level would be increased
        # for no  reason.
        self.current_union_enum_vectors_list.pop(-1)
        self.union_label_to_userComment_dictionary.pop(-1)
