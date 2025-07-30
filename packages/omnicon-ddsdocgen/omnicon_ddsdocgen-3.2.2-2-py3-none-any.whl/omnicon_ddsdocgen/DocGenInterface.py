# for abstract class
import os
from abc import ABC, abstractmethod

"""
Abstract Base class for defining mutual I/F to be implemented for Doc generation
in various platforms for various formats
"""


class DocGenInterface(ABC):
    def __init__(self, title: str, new_version: str,  time: str, origin_version: str,
                        origin_dds_types_files: list = None,
                        new_dds_types_files: list = None,
                        origin_dds_topics_types_mapping: str = "",
                        new_dds_topics_types_mapping: str = ""):
        """
        This class allows creating one of two documents; an ICD (created by docGen) and a comparison document (created
        by DocCompare). The difference is in the title page; the version in the ICD is added on its on, but in the
        comparison document both versions are displayed in a table along with the files/folders used by each version

        IMPORTANT:
        WHEN origin_version COMES EMPTY , WE KNOW IT'S AN ICD, and new_version IS USED AS THE VERSION.
        WHEN origin_version IS NOT EMPTY, WE KNOW IT'S A COMPARISON DOCUMENT.

        """

    """
     This function creates a single chapter in the ICD. When a topic-to-types XML was was given by the user,
     a chapter is created for each topic. When  the user did not provide such XML file, a chapter is created for
     each non-nested type.
     :param topic: A string that contains the topic name. NOTE: When the user doesn't provide the topic-to-type XML.
                   This parameter will contain an empty string ('').
     :param dds_type: A string that contains the type name.
     """

    @abstractmethod
    def add_doc_title_page(self):
        pass

    @abstractmethod
    def add_toc_page(self):
        pass

    @abstractmethod
    def add_chapter(self, title, sub_title=""):
        pass

    # NonAbstract
    def start_table_generation(self):
        tableGenProcess = True

    # NonAbstract
    def table_end(self):
        tableGenProcess = False

    @abstractmethod
    def add_table_header(self, listOfTitles, bLongHeader, color):
        pass

    @abstractmethod
    def add_table_row(self, theTable, cells_text, align='c'):  # align=centered
        pass

    @abstractmethod
    def add_new_page(self):
        pass

    @abstractmethod
    def add_section(self):
        pass

    @abstractmethod
    def add_description(self, descr):
        pass

    @abstractmethod
    def add_new_line(self):
        pass

    @abstractmethod
    def add_message_volumes(self, min_volume, avg_volume, max_volume):
        pass

    @abstractmethod
    def finalize_doc(self):
        # Intended post-processing prior to calling generate_doc
        pass

    @abstractmethod
    def generate_doc(self, output_file_name: str, temp_folder: str):
        pass
