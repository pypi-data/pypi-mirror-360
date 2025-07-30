import enum
import re
from typing import List

from Omnicon_GenericDDSEngine_Py import Element

from .SharedEnums import ChangeStatusEnum


class ColumnNumbersEnum(enum.IntEnum):
    HIERARCHY_COLUMN_NUM = 0
    FIELD_COLUMN_NUM = 1
    TYPE_COLUMN_NUM = 2
    DESCRIPTION_COLUMN_NUM = 3


STATUS_ENUM_VS_STR_DICT = {
    ChangeStatusEnum.NO_CHANGE: "",
    ChangeStatusEnum.DELETED: "Deleted",
    ChangeStatusEnum.ADDED: "Added",
    ChangeStatusEnum.CHANGED: "Modified"
}


class EnumCompElement:
    def __init__(self, name, val, user_comment, is_default):
        self.name = name
        self.val = val
        self.is_default = is_default
        self.user_comment = user_comment

    def __eq__(self, other):
        if isinstance(other, EnumCompElement):
            return self.name == other.name
        return False


class CompElement:
    field_name: str
    introspection_element: Element
    hierarchy: str
    type_kind_name: str
    user_comment: str
    full_description: str
    enum_options: List[EnumCompElement]
    sons_list: list  # OF
    change_type: str
    change_description: str
    change_status: ChangeStatusEnum
    is_discriminator: bool
    id: int
    content_id: int

    def __init__(self, introspection_element: Element = None, is_discriminator=False, id=None, content_id=None):
        self.field_name = ""  # Serves as the key for comparisons
        self.introspection_element = introspection_element
        self.hierarchy = ""
        self.type_kind_name = ""
        self.user_comment = ""  # WHEN USER COMMENT IS EMPTY - get it from full_description
        self.full_description = ""
        self.enum_options: List[EnumCompElement] = []
        self.sons_list: List[CompElement] = []
        self.is_discriminator = is_discriminator
        self.id = id
        self.content_id = content_id

        self.min_message_volume = 0
        self.max_message_volume = 0
        self.avg_message_volume = 0

        # For the result of comparison
        self.change_type = ""
        self.change_description = ""
        self.change_status = ChangeStatusEnum.NO_CHANGE

    def add_enum_element_to_list(self, name, val, user_comment, is_default=False):
        # When enum element has "" for a name, it's probably a union option that isn't an enum (it's just a number)
        self.enum_options.append(EnumCompElement(name, val, user_comment, is_default))

    def add_data_to_comp_element(self, row_data_list):
        # row_data_list structure is: [hierarchy, field, type_notation, description_and_metadata]
        self.hierarchy = row_data_list[ColumnNumbersEnum.HIERARCHY_COLUMN_NUM]
        self.field_name = row_data_list[ColumnNumbersEnum.FIELD_COLUMN_NUM]
        self.type_kind_name = row_data_list[ColumnNumbersEnum.TYPE_COLUMN_NUM]
        self.full_description = row_data_list[ColumnNumbersEnum.DESCRIPTION_COLUMN_NUM]

    def update_message_volume(self, volumes_list: list):
        # volumes_list = [min_volume, avg_volume, max_volume]
        self.min_message_volume = volumes_list[0]
        self.avg_message_volume = volumes_list[1]
        self.max_message_volume = volumes_list[2]

    def retrieve_row_data_list(self, is_comparison: bool = False):
        row_data_list = [self.hierarchy, self.field_name, self.type_kind_name, self.full_description]
        # A commented out version for testing:
        # row_data_list = [self.hierarchy, self.field_name, self.type_kind_name, f"{self.full_description}\n"
        #                                                                        f"min: {self.min_message_volume}\n"
        #                                                                        f"avg: {self.avg_message_volume}\n"
        #                                                                        f"max: {self.max_message_volume}\n"
        #                                                                        ]
        # See if it's a comparison doc or an ICD doc
        if is_comparison:
            # row_data_list.append(self.change_type)
            row_data_list.append(self.change_description)
        return row_data_list

    def extract_numbers_from_union_options(self):
        substring = "Union discriminator options: "
        position = self.full_description.find(substring)
        # isolate the list of descriminator options:
        discriminator_options_str = self.full_description[position + len(substring)]
        return set(map(int, discriminator_options_str.split(", ")))

    def add_differences_data(self, differences: str, change_status: ChangeStatusEnum = None):
        if change_status:
            # When change status is known:
            self.change_type = STATUS_ENUM_VS_STR_DICT[change_status]
        else:
            # When change status is unknown, see if there is any difference:
            if differences == "":
                change_status = ChangeStatusEnum.NO_CHANGE
            else:
                change_status = ChangeStatusEnum.CHANGED

        self.change_status = change_status
        self.change_type = STATUS_ENUM_VS_STR_DICT[change_status]
        # Remove trailing \n
        self.change_description = differences.rstrip('\n')
        # If the end is ',' - replace it to '.'
        if self.change_description.endswith(';'):
            self.change_description = self.change_description[:-1]
