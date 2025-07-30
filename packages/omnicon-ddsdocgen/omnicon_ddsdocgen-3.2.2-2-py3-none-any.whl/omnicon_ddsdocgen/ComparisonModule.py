import re
from typing import Dict
from Omnicon_GenericDDSEngine_Py import Element

from .comp import CompElement, ChangeStatusEnum, STATUS_ENUM_VS_STR_DICT, EnumCompElement


class ComparisonModule:
    def __init__(self, is_ignore_id: bool, is_compare_by_name: bool, update_progress_bar):
        self.is_ignore_id = is_ignore_id
        self.is_compare_by_name = is_compare_by_name
        self.update_progress_bar = update_progress_bar
        self.added_topics_list = []
        self.deleted_topics_list = []
        self.changes_list = []      # this list will hold tuples of (full_field_name, differences, change_status)
        self.changes_dict = {"Added Topics": self.added_topics_list,
                             "Deleted Topics": self.deleted_topics_list,
                             "Changed Topics": self.changes_list}
        self.current_topic_name = "" # used at the changes list

    @staticmethod
    def compare_str_members(new_member, origin_member, field_name):
        if new_member != origin_member:
            if not bool(new_member):
                # When new member was changed to empty
                return f"{field_name} '{origin_member}' removed ;\n"
            elif not bool(origin_member):
                # When member is no longer empty
                return f"{field_name} '{new_member}' added ;\n"
            else:
                new_member_normalized = "".join(new_member.split())
                origin_member_normalized = "".join(origin_member.split())
                if new_member_normalized == origin_member_normalized:
                    return ""
                # when the member was just changed
                return f"{field_name} changed from '{origin_member}' to '{new_member}' ;\n"
        else:
            # When nothing was changed
            return ""

    @staticmethod
    def compare_bool_members(new_member, origin_member, field_name, prefix="Field"):
        # field_name can either be "key", "metadata" or "optional"
        if new_member != origin_member:
            if not new_member:
                return f"{prefix} changed from {field_name} to non-{field_name} ;\n"
            else:
                # When the field was changed to True
                return f"{prefix} changed from non-{field_name} to {field_name} ;\n"
        else:
            return ""

    @staticmethod
    def compare_union_options(new_element: CompElement, origin_element: CompElement):
        origin_numbers = new_element.extract_numbers_from_union_options()
        new_numbers = origin_element.extract_numbers_from_union_options()

        added = new_numbers - origin_numbers
        deleted = origin_numbers - new_numbers

        change_str = "Union options list changed: "
        changes = []
        for num in sorted(deleted):
            changes.append(f"option {num} deleted")
        for num in sorted(added):
            changes.append(f"option {num} added")

        if bool(changes):
            return change_str + ", ".join(changes) + "."
        else:
            return ""

    @staticmethod
    def isolate_sequence_notation_from_type_kind_name(type_kind_name):
        """
        This function extracts the sequence notation and the rest of the given string `type_kind_name`.
        Parameters:
        type_kind_name (str): A string that may contain a sequence notation.

        Returns: tuple - (the sequence notation's number,type_kind_name but without the sequence notation)
        """
        sizes = re.search(r"[\[<](-?\d+)[\]>]", type_kind_name)
        if sizes is None:
            return None, type_kind_name
        sizes = int(sizes.group(1))  # group(1) gets the first group, i.e., the number.
        the_rest = re.sub(r"[\[<](-?\d+)[\]>]", "", type_kind_name)
        return sizes, the_rest

    def compare_type_kind_name(self, new_element: CompElement, origin_element: CompElement):
        if new_element.type_kind_name != origin_element.type_kind_name:
            # compare tkn (stands for type kind name) which Holds a tuple - (sequence notation's number,type_kind_name
            # but without the sequence notation)
            new_tkn_info = self.isolate_sequence_notation_from_type_kind_name(new_element.type_kind_name)
            origin_tkn_info = self.isolate_sequence_notation_from_type_kind_name(origin_element.type_kind_name)

            # if ' of ' in self.type_kind_name and ' of ' in other.type_kind_name:
            # Compare the kind
            if new_tkn_info[1] != origin_tkn_info[1]:
                return f"Type changed from {origin_element.type_kind_name} to {new_element.type_kind_name} ;\n"
            # Compare the length
            elif new_tkn_info[0] != origin_tkn_info[0]:
                if "<" in new_element.type_kind_name:
                    return f"Length changed from <{origin_tkn_info[0]}> to <{new_tkn_info[0]}> ;\n"
                else:
                    return f"Length changed from [{origin_tkn_info[0]}] to [{new_tkn_info[0]}] ;\n"

        return ""

    @staticmethod
    def check_id(new_element: CompElement, origin_element: CompElement):
        if new_element.id is not None and origin_element.id is not None:
            if new_element.id != origin_element.id:
                return f"Id changed from {origin_element.id} to {new_element.id} ;\n"
        return ""

    @staticmethod
    def check_content_id(new_element: CompElement, origin_element: CompElement):
        if new_element.content_id is not None and origin_element.content_id is not None:
            if new_element.content_id != origin_element.content_id:
                return f"Id changed from {origin_element.id} to {new_element.id} ;\n"
        return ""

    def compare_enum_comp_elements(self,
                                   new_enum_comp_element: EnumCompElement, origin_enum_comp_element: EnumCompElement):
        differences = ""
        if new_enum_comp_element.val != origin_enum_comp_element.val:
            differences += f"Enum '{new_enum_comp_element.name}' value changed from " \
                           f"{origin_enum_comp_element.val} to {new_enum_comp_element.val} ;\n"

        differences += self.compare_bool_members(
            new_enum_comp_element.is_default,
            origin_enum_comp_element.is_default,
            "default",
            prefix=f"Enum value '{new_enum_comp_element.name}'")

        comment_diff = self.compare_str_members(
            new_enum_comp_element.user_comment, origin_enum_comp_element.user_comment, "comment")
        if bool(comment_diff):
            differences += f"Enum value '{new_enum_comp_element.name}' {comment_diff}"
        if differences.endswith(" ;\n"):
            differences = differences[:-3]  # + "\n"
        return differences

    def compare_enum_list(self, new_element: CompElement, origin_element: CompElement):
        new_enum_list = new_element.enum_options
        origin_enum_list = origin_element.enum_options

        differences = ""

        for new_enum in new_enum_list:
            is_enum_found = False
            for origin_enum in origin_enum_list:
                # Using the implementation of "__eq__" in EnumCompElement to compare enum elements
                if new_enum == origin_enum:
                    is_enum_found = True
                    new_diff = self.compare_enum_comp_elements(new_enum, origin_enum)
                    if new_diff != "":
                        # Add \n at the end of each difference
                        new_diff += " ;\n"
                    differences += new_diff
                    break

            if not is_enum_found:
                # When the enum in the new list isnt in the old list:
                differences += f"Enum '{new_enum.name} = {new_enum.val}' added ;\n"

        for origin_enum in origin_enum_list:
            # Using the implementation of "__eq__" in EnumCompElement to compare enum elements
            if origin_enum not in new_enum_list:
                differences += f"Enum '{origin_enum.name} = {origin_enum.val}' deleted ;\n"

        if differences.endswith(" ;\n"):
            differences = differences[:-3] + "\n"
        return differences

    def compare_introspection_elements(self, new_element: CompElement, origin_element: CompElement):
        new_element: Element = new_element.introspection_element
        origin_element: Element = origin_element.introspection_element

        if new_element is None or origin_element is None:
            return ""

        differences = ""
        differences += self.compare_str_members(new_element.min, origin_element.min, 'Minimum value')
        differences += self.compare_str_members(new_element.max, origin_element.max, 'Maximum value')
        differences += self.compare_str_members(new_element.defaultValue, origin_element.defaultValue, 'Default value')

        differences += self.compare_bool_members(new_element.isKey, origin_element.isKey, "key")
        differences += self.compare_bool_members(new_element.isOptional, origin_element.isOptional, "optional")
        # differences += self.compare_bool_members(new_element.isMetadata, origin_element.isMetadata, "metadata")
        differences += self.compare_str_members(new_element.userComment, origin_element.userComment, 'Comment')

        return differences

    def handle_main_descriminator(self, new_element: CompElement, origin_element: CompElement):
        differences = ""
        if "enum" in new_element.type_kind_name and "enum" in origin_element.type_kind_name:
            differences += self.compare_enum_list(new_element, origin_element)
            if differences != "":
                differences = "Union option enums changed:\n" + differences
        else:
            # Reminder: main descriminator was added artificially to the ICD byt the single chapter generator, so there
            # is no chance for other information in the full description
            differences = self.compare_union_options(new_element, origin_element)
        return differences

    def compare_comp_elements(self, new_element: CompElement, origin_element: CompElement):
        differences = ""

        if not self.is_compare_by_name:
            # When the ID is the key, need to
            differences += self.check_id(new_element, origin_element)
        differences += self.check_content_id(new_element, origin_element)
        # Start by checking the field_name - useful when comparing by ID
        differences += self.compare_str_members(new_element.field_name, origin_element.field_name, 'Field name')
        # When this is a main discriminator
        if differences == "" and new_element.is_discriminator:
            differences = self.handle_main_descriminator(new_element, origin_element)
        else:
            differences += self.compare_str_members(new_element.hierarchy, origin_element.hierarchy, 'Hierarchy')
            differences += self.compare_type_kind_name(new_element, origin_element)
            # Check USER comment
            differences += self.compare_str_members(new_element.user_comment, origin_element.user_comment, 'Comment')
            # See if need to check introspection element by checking FULL DESCRIPTION ( != user comment)
            if self.compare_str_members(new_element.full_description, origin_element.full_description, '') != "":
                differences += self.compare_introspection_elements(new_element, origin_element)

            if not self.is_ignore_id:
                differences += self.check_id(new_element, origin_element)

            # Compare enum lists only if both elements are enums
            if "enum" in new_element.type_kind_name and "enum" in origin_element.type_kind_name:
                differences += self.compare_enum_list(new_element, origin_element)

        return differences

    def compare_son_list_element_keys(self, new_son, origin_son):
        # compare by name when this is a discriminator discription - even if this is a compare by id type
        if self.is_compare_by_name or "(D)" in origin_son.hierarchy:
            return new_son.field_name == origin_son.field_name
        else:
            # When comparing by ID:
            if new_son.id is None or origin_son.id is None:
                if new_son.field_name == 'discriminator' and origin_son.field_name == 'discriminator':
                    return True
                else:
                    # Not all elements have introspection elements. in which case, answer is False
                    return False
            return new_son.id == origin_son.id

    def find_son_in_list(self, son_list, other_son):
        # Return the index if son exists or None if doesnt.
        for i, son in enumerate(son_list):
            if self.compare_son_list_element_keys(son, other_son):
                return i
        return None

    def compare_union_elements(
            self, new_element: CompElement, origin_element: CompElement, full_type_name: str) -> bool:
        """
        this function is called when 'self' is a union element; the call is made after the union element itself was
        compared and all, with all thats left is to go over the sons list, which contains the main descriminator as
        the first index, followed by a 'local' descriminator, which in turn followed by its corresponding data; if
        there is another descriminator, it will be followed by its corresponding data, and so on.
        """
        is_changes_found = False

        combined_list = []

        # Start with the descriminator:
        main_descriminator = new_element.sons_list[0]
        main_descriminator_full_name = self.update_full_type_name(full_type_name, main_descriminator.field_name)
        combined_list.append(main_descriminator)
        # Compare descriminators
        self.compare_sons(main_descriminator, origin_element.sons_list[0], main_descriminator_full_name)

        new_sons_list = new_element.sons_list
        origin_sons_list = origin_element.sons_list

        for i in range(1, len(new_sons_list)):
            if "(D)" in new_sons_list[i].hierarchy:
                # Go over the indexes of descriminators ONLY. The other indexes are handled here as well.
                new_descriminator = new_sons_list[i]
                new_content = new_sons_list[i + 1]  # The content always follows the selector descriminator
                new_descriminator_full_name = self.update_full_type_name(full_type_name, new_descriminator.field_name)
                new_content_full_name = self.update_full_type_name(full_type_name, new_content.field_name)

                other_son_index: int
                if self.is_compare_by_name:
                    other_son_index = self.find_son_in_list(origin_sons_list, new_descriminator)
                else:
                    # When comparing by id, we cannot compare using new_descriminator (new_sons_list[i]), so we'll
                    # compare the new_content (new_sons_list[i + 1])
                    other_son_index = self.find_son_in_list(origin_sons_list, new_content)

                if other_son_index is not None:
                    # When there is an equivalent
                    combined_list.append(new_descriminator)  # No need to compare; descriminators are added by docgen
                    combined_list.append(new_content)

                    if self.is_compare_by_name:
                        is_found_another_diff = self.compare_sons(
                            new_content, origin_sons_list[other_son_index + 1], new_content_full_name)
                        is_changes_found = is_changes_found or is_found_another_diff
                    else:
                        # When comparing by ID, other_son_index is the actual son, unlike when comparing by name where
                        # the other_son_index is the artificailly added discriminator
                        is_found_another_diff = self.compare_sons(
                            new_content, origin_sons_list[other_son_index], new_content_full_name)
                        is_changes_found = is_changes_found or is_found_another_diff
                else:
                    # When could not find the other descriminator, means both new_descriminator and new_content *ADDED*
                    is_changes_found = True
                    combined_list.append(new_descriminator)
                    new_descriminator.add_differences_data("", ChangeStatusEnum.ADDED)
                    self.add_changes_to_changes_list(
                        new_descriminator_full_name, new_descriminator.type_kind_name, "", ChangeStatusEnum.ADDED)

                    combined_list.append(new_content)
                    new_content.add_differences_data("", ChangeStatusEnum.ADDED)
                    self.add_changes_to_changes_list(
                        new_content_full_name, new_content.type_kind_name, "", ChangeStatusEnum.ADDED)

        # Search for deleted items
        position_offset = 0
        for i in range(1, len(origin_sons_list)):
            if "(D)" in origin_sons_list[i].hierarchy:
                other_son_index: int
                if self.is_compare_by_name:
                    other_son_index = self.find_son_in_list(new_sons_list, origin_sons_list[i])
                else:
                    # When comparing by id, we cannot compare using origin_sons_list[i], so we'll
                    # compare the origin_sons_list[i + 1]
                    other_son_index = self.find_son_in_list(new_sons_list, origin_sons_list[i + 1])

                if other_son_index is None:
                    is_changes_found = True
                    # When origin son is not found on the new
                    combined_list.insert(i + position_offset, origin_sons_list[i])
                    position_offset += 1
                    origin_sons_list[i].add_differences_data("", ChangeStatusEnum.DELETED)
                    # Add
                    combined_list.insert(i + position_offset, origin_sons_list[i + 1])
                    position_offset += 1
                    origin_sons_list[i + 1].add_differences_data("", ChangeStatusEnum.DELETED)

        new_element.sons_list = combined_list
        return is_changes_found

    def compare_sons(self, new_son: CompElement, origin_son: CompElement, full_type_name: str)-> bool:
        is_changes_found = False
        is_changes_found_2 = False
        differences = self.compare_comp_elements(new_son, origin_son)
        if differences != "":
            is_changes_found = True
            self.add_changes_to_changes_list(
                full_type_name,new_son.type_kind_name, differences, ChangeStatusEnum.CHANGED)
        new_son.add_differences_data(differences)
        if new_son.type_kind_name == "union" and origin_son.type_kind_name == "union":
            is_changes_found_2 = self.compare_union_elements(new_son, origin_son, full_type_name)
        else:
            is_changes_found_2 = self.compare_sons_lists(new_son, origin_son, full_type_name)

        # If there was ANY change - return True
        return is_changes_found or is_changes_found_2
    @staticmethod
    def update_full_type_name(old_name, addition):
        if old_name == "":
            return addition
        else:
            return f"{old_name}.{addition}"

    def compare_sons_lists(self, new_element: CompElement, origin_element: CompElement, full_type_name: str):
        new_sons_list = new_element.sons_list
        origin_sons_list = origin_element.sons_list
        combined_list = []
        is_changes_found = False
        # Go over the new sons list
        for new_son in new_sons_list:
            new_son_full_name = self.update_full_type_name(full_type_name, new_son.field_name)

            other_son_index = self.find_son_in_list(origin_sons_list, new_son)
            # See if the son existed in the origin:
            if other_son_index is not None:
                combined_list.append(new_son)
                if self.compare_sons(new_son, origin_sons_list[other_son_index], new_son_full_name):
                    is_changes_found = True
            else:
                # When the son doesn't exist in the origin list (means this is a new son):
                combined_list.append(new_son)
                new_son.add_differences_data("", ChangeStatusEnum.ADDED)
                self.add_changes_to_changes_list(new_son_full_name, new_son.type_kind_name, "", ChangeStatusEnum.ADDED)
                is_changes_found = True

        # Checking what was deleted
        position_offset = 0
        for i, origin_son in enumerate(origin_sons_list):
            # See if the son exists in the new:
            if self.find_son_in_list(new_sons_list, origin_son) is None:
                deleted_son_full_name = self.update_full_type_name(full_type_name, origin_son.field_name)
                # When origin son is not found on the new
                combined_list.insert(i + position_offset, origin_son)
                position_offset += 1
                origin_son.add_differences_data("", ChangeStatusEnum.DELETED)
                self.add_changes_to_changes_list(
                    deleted_son_full_name, origin_son.type_kind_name,"", ChangeStatusEnum.DELETED)
                is_changes_found = True

        new_element.sons_list = combined_list
        return is_changes_found

    def compare_root_comp_elements(self, new_element: CompElement, origin_element: CompElement) -> (
            'CompElement', bool):

        is_changes_found = False

        # Check the type
        if new_element.field_name != origin_element.field_name:
            # When type name was changed: Mark as changed and return the new one AS IS
            new_element.change_type = STATUS_ENUM_VS_STR_DICT[ChangeStatusEnum.CHANGED]
            change_description = f"Type name changed from {origin_element.field_name} to {new_element.field_name}"
            new_element.change_description = change_description
            new_element.add_differences_data("", ChangeStatusEnum.CHANGED)

            self.add_changes_to_changes_list(
                new_element.field_name, new_element.type_kind_name, change_description, ChangeStatusEnum.CHANGED)
            is_changes_found = True

        topic_description_comment_change = self.compare_str_members(new_element.user_comment, origin_element.user_comment, "Topic level user comment")
        if topic_description_comment_change != "":
            new_element.user_comment = topic_description_comment_change
            new_element.change_type = STATUS_ENUM_VS_STR_DICT[ChangeStatusEnum.CHANGED]
            # TODO change description required??
            # new_element.change_description = f"Type name changed from {origin_element.field_name} to
            # {new_element.field_name}"

            new_element.add_differences_data("", ChangeStatusEnum.CHANGED)
            self.add_changes_to_changes_list(
                new_element.field_name,
                "",
                new_element.user_comment,
                ChangeStatusEnum.CHANGED)
            is_changes_found = True

        # compare_sons_lists returns True when changes were found
        if self.compare_sons_lists(new_element, origin_element, ""):
            is_changes_found = True

        return new_element, is_changes_found

    def add_changes_to_changes_list(
            self, full_field_name: str, field_type: str,  differences: str, change_status: ChangeStatusEnum = None):

        # Remove trailing \n
        change_description = differences.rstrip('\n')
        # If the end is ',' - remove it
        if change_description.endswith(';'):
            change_description = change_description[:-1]
        self.changes_list.append((full_field_name, field_type, change_description, change_status, self.current_topic_name))

    def compare_structures(self, origin_structure: Dict[str, CompElement], new_structure: Dict[str, CompElement]) -> \
            Dict[str, CompElement]:
        result_structure = {}
        i = 0
        for topic_name in new_structure:
            self.current_topic_name = topic_name
            self.update_progress_bar(i, topic_name)
            if topic_name in origin_structure:
                # When both topics are present:
                result, change_detected = \
                    self.compare_root_comp_elements(new_structure[topic_name], origin_structure[topic_name])
                # Do not add structure if no changes were detected
                if change_detected:
                    result_structure[topic_name] = result
            else:
                # When a topic has been added:
                result_structure[f"{topic_name} - ADDED"] = new_structure[topic_name]
                result_structure[f"{topic_name} - ADDED"].add_differences_data("", ChangeStatusEnum.ADDED)
                self.added_topics_list.append(topic_name)
            i += 1

        # Checking if a topic was deleted (Note: i is used for progress update)
        for topic_name in origin_structure:
            if topic_name not in new_structure:
                self.update_progress_bar(i, topic_name)
                i += 1
                self.current_topic_name = topic_name
                # When a topic has been deleted:
                result_structure[f"{topic_name} - DELETED"] = origin_structure[topic_name]
                result_structure[f"{topic_name} - DELETED"].add_differences_data("", ChangeStatusEnum.DELETED)
                self.deleted_topics_list.append(topic_name)

        return result_structure
