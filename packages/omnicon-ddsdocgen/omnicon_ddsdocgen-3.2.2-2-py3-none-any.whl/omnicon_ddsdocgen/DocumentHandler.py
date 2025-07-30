import os
import shutil
from typing import Any

from . import Logger
from .SharedEnums import ChangeStatusEnum
from .comp import CompElement


class DocumentHandler:
    def __init__(self, document, table_header_titles, is_comparison: bool=False,
                 update_progress_bar = None):

        self.current_table = None
        self.logger = Logger.add_logger(__name__)
        self.document = document
        self.table_header_titles = table_header_titles
        self.is_comparison = is_comparison      # Tells us if it's a comparison document (which has 2 extra columns)

        self.update_progress_bar = update_progress_bar

    def create_new_chapter_with_table(self, topic: str, dds_type: str, element: Any, topic_level_comment: str,
                                      min_message_volume: str = None,
                                      avg_message_volume: str = None,
                                      max_message_volume: str = None,
                                      parent_change_status=ChangeStatusEnum.NO_CHANGE) -> None:
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
            self.document.add_chapter(topic, parent_change_status=parent_change_status)
            self.document.add_type_to_chapter(dds_type, parent_change_status)


        else:

            self.document.add_chapter(dds_type, parent_change_status=parent_change_status)  # level for styling

        # Add message volumes

        if not self.is_comparison:
            self.document.add_message_volumes(min_message_volume, avg_message_volume, max_message_volume)

        self.document.add_description(topic_level_comment, parent_change_status=parent_change_status)

        #
        # if element.parentDataTypeName != "":
        #     self.document.add_new_line(self.modify_user_comment_to_icd_needs(element))

        # Create the table
        self.current_table = self.document.add_table_header(self.table_header_titles)
        return self.current_table


    def recursive_doc_reconstruction(self, element: CompElement, father_change_status=ChangeStatusEnum.NO_CHANGE):

        current_change_status = None

        for son_element in element.sons_list:
            row_data_list = son_element.retrieve_row_data_list(self.is_comparison)

            if father_change_status == ChangeStatusEnum.ADDED or father_change_status == ChangeStatusEnum.DELETED:
                current_change_status = father_change_status
            else:
                current_change_status = son_element.change_status

            # Finally - add the extra row to the document
            self.document.add_table_row(self.current_table, row_data_list, change_status=current_change_status)

            self.recursive_doc_reconstruction(son_element, current_change_status)

    def create_volume_appendix(self, structured_doc_data: dict):
        self.document.add_chapter('Appendix – Message Volumes Summary')
        appendix_volumes_table = self.document.add_table_header(
            ['#', 'Topic Name',	'Minimum (bytes)', 'Maximum (bytes)', 'Average (bytes)'])
        i = 1
        for topic_name, root_element in structured_doc_data.items():
            min_message_volume =  f"{root_element.min_message_volume:,}"
            avg_message_volume = f"{root_element.avg_message_volume:,}"
            max_message_volume = f"{root_element.max_message_volume:,}"
            if max_message_volume == "-1":
                max_message_volume = "-1 (Unbounded)"
            row_table_list = [str(i), topic_name, min_message_volume, max_message_volume, avg_message_volume]
            self.document.add_table_row(appendix_volumes_table, row_table_list)
            i += 1


    def reconstruct_chapter_header_from_structured_doc_data(self, chapter_name: str, root_element: CompElement):
        type_name = root_element.field_name
        element = root_element.introspection_element
        # type_kind_name = root_element.type_kind_name
        topic_level_comment = root_element.user_comment
        parent_change_status = root_element.change_status
        min_message_volume = root_element.min_message_volume
        avg_message_volume = root_element.avg_message_volume
        max_message_volume = root_element.max_message_volume

        self.current_table = self.create_new_chapter_with_table(
            topic=chapter_name,
            dds_type=type_name,
            element=element,
            topic_level_comment=topic_level_comment,
            min_message_volume=f"{min_message_volume:,}",
            avg_message_volume=f"{avg_message_volume:,}",
            max_message_volume=f"{max_message_volume:,}",
            parent_change_status=parent_change_status)
        # NOTE: f"{min_message_volume:,}" adds commas to large numbers. for example 1000 -> 1,000

    @staticmethod
    def calculate_how_many_topics_in_changes_dict(changes_dict):
        total_topics: int = 0
        for chapter_name, chapter_content_list in changes_dict.items():

            if not "Changed" in chapter_name:
                # When this is either Added or Deleted topic chapter - just add the topic name.
                # Go over the chapter's content list
                for chapter_content in chapter_content_list:
                    total_topics += 1
            else:
                latest_topic = ""
                for entry in chapter_content_list:
                    # See if we have a new topic:
                    if entry[4] != latest_topic:
                        latest_topic = entry[4]
                        total_topics += 1

        return total_topics

    def create_summary_report(self, changes_dict: dict, progress_factor: int):

        # Calculate total num of steps
        total_entries = self.calculate_how_many_topics_in_changes_dict(changes_dict)

        # Go over the dict which contains:  "Added Topics": self.added_topics_list,
        #                                   "Deleted Topics": self.deleted_topics_list,
        #                                   "Changed Topics": self.changes_list
        i = 0
        for chapter_name, chapter_content_list in changes_dict.items():
            # Add a new page
            self.document.add_new_page()
            # Determine the color:
            change_status = ChangeStatusEnum.CHANGED
            if "Added" in chapter_name:
                 change_status = ChangeStatusEnum.ADDED
            elif "Deleted" in chapter_name:
                 change_status = ChangeStatusEnum.DELETED
            # Add the main name ("Added Topics" / "Deleted Topics"/ "Changed Topics")
            self.document.add_chapter(chapter_name, change_status, 1)

            if not "Changed" in chapter_name:
                # When this is either Added or Deleted topic chapter - just add the topic name.
                # Go over the chapter's content list
                for chapter_content in chapter_content_list:
                    self.document.add_chapter(chapter_content, change_status, 2)
                    self.update_progress_bar(i +  total_entries * progress_factor, chapter_content, progress_factor)
                    i += 1
            else:
                # When this is the Changed chapter, tables are to be added
                new_table_header_titles = ["Full Field Name", "Type", "Change Description"]
                # Reminder: each entry in the list has the following tuple:
                # (full_field_name, type, differences, change_status, self.current_topic_name)
                change_status = ChangeStatusEnum.CHANGED
                latest_topic = ""
                current_table = None
                for entry in chapter_content_list:
                    # See if we have a new topic:
                    if entry[4] != latest_topic:
                        latest_topic = entry[4]
                        # Add topic name
                        paragraph = self.document.add_paragraph("")
                        self.document.add_chapter(entry[4],change_status, 2)
                        # Create the table
                        current_table = self.document.add_table_header(new_table_header_titles)
                        self.update_progress_bar(i + total_entries * progress_factor, latest_topic, progress_factor)
                        i += 1

                    # ORGANIZE THE TABLE DATA:
                    cells_text = [entry[0], entry[1], entry[2]]   # [full_field_name, differences]
                    change_status = entry[3]

                    self.document.add_table_row(current_table, cells_text, change_status=change_status)

        return i

    def create_complete_report(self, structured_doc_data, progress_factor):
        i = 0
        # When creating a complete report:
        for chapter_name, root_element in structured_doc_data.items():
            self.update_progress_bar(i , chapter_name, progress_factor)
            i += 1
            self.reconstruct_chapter_header_from_structured_doc_data(chapter_name, root_element)
            self.recursive_doc_reconstruction(root_element, root_element.change_status)

        return i

    def finalize_doc(self, output_file_name: str, output_folder: str, temp_folder: str,
                     output_format: str, progress_position: int,  progress_factor: int = 0 ):

        self.update_progress_bar(progress_position , "Saving", progress_factor, is_save=True)
        self.document.finalize_doc()
        self.document.generate_doc(output_file_name, temp_folder)
        self.save_file_to_requested_folder(output_file_name, output_folder, temp_folder, output_format)

    def create_ICD_from_structured_doc_data(self, structured_doc_data,
                                            changes_dict: dict = None, progress_factor: int = 0,
                                            is_summary_report: bool = False):
        i: int
        if is_summary_report:
            i = self.create_summary_report(changes_dict, progress_factor)
        else:
            i = self.create_complete_report(structured_doc_data, progress_factor)

        return i


    def save_file_to_requested_folder(self,
                                      output_file_name: str, output_folder: str, temp_folder: str, output_type: str):
        """
        This function copies the requested file from the temp location to the requested location.
        :param output_file_name: Requested file name
        :param output_folder: Requested output folder
        :param temp_folder: The temp folder where the requested file was created
        :param output_type: The requested file extension ('pdf'/'docx', 'html' /etc...)
        """
        output_file_name = f'{output_file_name}.{output_type}'
        temp_output_path = os.path.abspath(os.path.join(temp_folder, output_file_name))
        if output_folder == "":
            output_folder = os.getcwd()
        full_requested_path = os.path.abspath(os.path.join(output_folder, output_file_name))
        self.logger.info(f"Generating {output_file_name}")

        # Copy the file into the requested folder:
        try:
            self.logger.debug(f"saving {output_file_name} into {output_folder}")
            shutil.copyfile(temp_output_path, full_requested_path)
            info_text = f"File saved successfully into '{full_requested_path}'"
            self.logger.info(info_text)
            # ErrorListHandler.add_entry(LogLevel.INFO, info_text)

        except Exception as err:
            message = f"Could not save '{full_requested_path}'. " \
                      f"Please check you have writing permissions at requested target folder."
            self.logger.error(message, exc_info=True)
            raise Exception(message)