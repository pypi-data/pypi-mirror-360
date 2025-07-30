import os
import json
from typing import List
from bs4 import BeautifulSoup
import re

from .SharedEnums import ChangeStatusEnum
from . import DocGenInterface

from . import Logger


class HtmlGen(DocGenInterface.DocGenInterface):
    def __init__(self, title: str, new_version: str, time: str, origin_version: str = "",
                 origin_dds_types_files: list = None,
                 new_dds_types_files: list = None,
                 origin_dds_topics_types_mapping: str = "",
                 new_dds_topics_types_mapping: str = "",
                 is_compare_by_name: bool = False,
                 is_ignore_id: bool = False,
                 is_summary_report=False):

        super().__init__(title=title,
                         new_version=new_version,
                         time=time,
                         origin_version=origin_version,
                         origin_dds_types_files=origin_dds_types_files,
                         new_dds_types_files=new_dds_types_files,
                         origin_dds_topics_types_mapping=origin_dds_topics_types_mapping,
                         new_dds_topics_types_mapping=new_dds_topics_types_mapping)
        self.logger = Logger.add_logger(__name__)

        # Create a new '.html' file based on the styling info from the template
        self.html_template_path = HtmlGen.get_html_template_path()
        if not self.html_template_path:
            self.logger.fatal("Template.html wasn't found. Cannot create html file")
            raise Exception("Template.html wasn't found. Cannot create html")
        else:
            self.logger.debug("html template path at " + self.html_template_path)

        with open(self.html_template_path, 'r') as html_file:
            self.soup = BeautifulSoup(html_file, 'html.parser')

        self.add_doc_title_page(title=title,
                                new_version=new_version,
                                time=time,
                                origin_version=origin_version,
                                origin_dds_types_files=origin_dds_types_files,
                                new_dds_types_files=new_dds_types_files,
                                origin_dds_topics_types_mapping=origin_dds_topics_types_mapping,
                                new_dds_topics_types_mapping=new_dds_topics_types_mapping,
                                is_compare_by_name=is_compare_by_name,
                                is_ignore_id=is_ignore_id, is_summary_report=is_summary_report)

        self.json_dict = {}

        self.latest_chapter = False
        self.title = ''

    def add_doc_title_page(self, title: str, new_version: str, time: str, origin_version: str,
                           origin_dds_types_files: list = None,
                           new_dds_types_files: list = None,
                           origin_dds_topics_types_mapping: str = "",
                           new_dds_topics_types_mapping: str = "",
                           is_compare_by_name: bool = False,
                           is_ignore_id: bool = False,
                           is_summary_report=False):
        title_tag = self.soup.find('title')
        title_tag.string = title

        document_title_tag = self.soup.find('h2', {'id': 'document-title'})
        document_title_tag.string = title

        document_version = self.soup.find('h2', {'id': 'document-version'})
        document_version.string = new_version

        if origin_version != "":
            header_info_title = self.soup.find('div', {'id': 'header-info-title'})
            header_info_title['class'] = 'hidden'

            header_info_version = self.soup.find('div', {'id': 'header-info-version'})
            header_info_version['class'] = 'hidden'

            filter_icon = self.soup.find('svg', {'id': 'filter-icon'})
            filter_icon['class'].remove('hidden')

            header_info_comparison_origin = self.soup.find('div', {'id': 'header-info-comparison-origin'})
            header_info_comparison_origin['class'].remove('hidden')

            header_info_comparison_origin_version = self.soup.find('span', {'id': 'header-info-comparison-origin-version'})
            header_info_comparison_origin_version.string = origin_version

            header_info_comparison_origin_title = self.soup.find('h2', {'id': 'header-info-comparison-origin-title'}).find('span', {'class': 'origin-title'})
            header_info_comparison_origin_title.string = os.path.basename(origin_dds_topics_types_mapping)

            header_info_comparison_icon = self.soup.find('div', {'id': 'header-info-comparison-icon'})
            header_info_comparison_icon['class'].remove('hidden')
            
            header_info_comparison_new = self.soup.find('div', {'id': 'header-info-comparison-new'})
            header_info_comparison_new['class'].remove('hidden')

            header_info_comparison_new_version = self.soup.find('span', {'id': 'header-info-comparison-new-version'})
            header_info_comparison_new_version.string = new_version

            header_info_comparison_new_title = self.soup.find('h2', {'id': 'header-info-comparison-new-title'}).find('span', {'class': 'origin-title'})
            header_info_comparison_new_title.string = os.path.basename(new_dds_topics_types_mapping)

            logo = self.soup.find('svg', {'id': 'docgen-logo'})
        else:
            logo = self.soup.find('svg', {'id': 'doccompare-logo'})
            
        logo.decompose()

        document_timestamp = self.soup.find('h2', {'id': 'document-timestamp'})
        document_timestamp.string = time

        if origin_dds_types_files:
            document_source_type_files_list = self.soup.find('ul', {'id': 'source-type-files-list'})
            for filepath in origin_dds_types_files:
                new_li = self.soup.new_tag('li')
                new_li.string = filepath
                document_source_type_files_list.append(new_li)

        if new_dds_types_files:
            command_popup_header = self.soup.find('div', {'class': 'command-popup-header'})
            command_popup_header['class'].append('hidden')
            command_popup_body = self.soup.find('div', {'class': 'command-popup-body'})
            command_popup_body['class'].append('command-popup-body-compare')
            command_popup_origin_title = self.soup.find('span', {'id': 'command-popup-origin-title'})
            command_popup_origin_title.string = os.path.basename(origin_dds_topics_types_mapping)
            command_popup_new_title = self.soup.find('span', {'id': 'command-popup-new-title'})
            command_popup_new_title.string = os.path.basename(new_dds_topics_types_mapping)
            document_new_type_files_list = self.soup.find('ul', {'id': 'new-type-files-list'})
            for filepath in new_dds_types_files:
                new_li = self.soup.new_tag('li')
                new_li.string = filepath
                document_new_type_files_list.append(new_li)
        else:
            command_popup_body_new = self.soup.find('div', {'class': 'command-popup-body-new'})
            command_popup_body_new['class'].append('hidden')
            command_popup_body_details = self.soup.find('div', {'class': 'command-popup-body-details'})
            command_popup_body_details['class'].append('hidden')
            command_popup_body_h5 = self.soup.find('h5', {'id': 'command-popup-origin-h5'})
            command_popup_body_h5['class'].append('hidden')

        if origin_dds_topics_types_mapping:
            document_source_topic_mapping = self.soup.find('ul', {'id': 'source-topic-mapping-list'})
            new_li = self.soup.new_tag('li')
            new_li.string = origin_dds_topics_types_mapping
            document_source_topic_mapping.append(new_li)
        else:
            document_source_topic_mapping_div = self.soup.find('div', {'id': 'source-topic-mapping-div'})
            document_source_topic_mapping_div.clear()
        
        command_popup_body_details_comparison_type = self.soup.find('p', {'id': 'command-popup-body-details-comparison-type'})
        if is_summary_report:
            command_popup_body_details_comparison_type.string = "Summary Report"
        else:
            command_popup_body_details_comparison_type.string = "Complete Report"

        command_popup_body_details_document_type = self.soup.find('p', {'id': 'command-popup-body-details-document-type'})
        if is_compare_by_name:
            command_popup_body_details_document_type.string = "Name Base" + (' (Ignore ID)' if is_ignore_id else '')
        else:
            command_popup_body_details_document_type.string = "ID Base"

        if new_dds_topics_types_mapping:
            document_new_topic_mapping = self.soup.find('ul', {'id': 'new-topic-mapping-list'})
            new_li = self.soup.new_tag('li')
            new_li.string = new_dds_topics_types_mapping
            document_new_topic_mapping.append(new_li)
        else:
            document_new_topic_mapping_div = self.soup.find('div', {'id': 'new-topic-mapping-div'})
            document_new_topic_mapping_div.clear()

    def add_toc_page(self):
        pass

    def add_chapter(self, section_title, parent_change_status=ChangeStatusEnum.NO_CHANGE, level=1):
        self.latest_chapter = section_title
        self.json_dict[section_title] = {
            'name': section_title
        }

    def add_type_to_chapter(self, dds_type, parent_change_status=ChangeStatusEnum.NO_CHANGE):
        if self.latest_chapter:
            self.json_dict[self.latest_chapter]['type'] = dds_type

    def add_table_header(self, listOfTitles, bLongHeader=True, color="grey"):
        if self.latest_chapter:
            self.json_dict[self.latest_chapter]['table_header'] = listOfTitles
            
            self.json_dict[self.latest_chapter]['table_content'] = [
                ["", self.json_dict[self.latest_chapter].get('type', '').rsplit('::', 1)[-1]] + ["" for i in range(len(listOfTitles) - 2)]
            ]

    def add_table_row(self, theTable, cells_text, align='c', change_status=ChangeStatusEnum.NO_CHANGE):
        if self.latest_chapter:
            if len(cells_text) == 5:
                if self.latest_chapter.startswith("Appendix – "):
                    cells_text.insert(5, '')
                else:
                    change_status_cell = change_status.name if change_status else ''
                    cells_text.insert(4, change_status_cell)
            cells_text[0] = '[' + cells_text[0]
            self.json_dict[self.latest_chapter]['table_content'].append(cells_text)

    def add_new_page(self):
        pass

    def add_section(self):
        pass

    def add_description(self, descr, parent_change_status=ChangeStatusEnum.NO_CHANGE):
        if self.latest_chapter:
            self.json_dict[self.latest_chapter]['description'] = descr

    def add_message_volumes(self, min_volume, avg_volume, max_volume):
        if self.latest_chapter:
            self.json_dict[self.latest_chapter]['min_volume'] = min_volume
            self.json_dict[self.latest_chapter]['avg_volume'] = avg_volume
            self.json_dict[self.latest_chapter]['max_volume'] = max_volume if int(re.sub(r'[.,]', '', max_volume)) > 0 else "Unbounded"

    def add_new_line(self):
        pass

    @staticmethod
    def get_html_template_path() -> str:
        doc_name = "Template.html"
        local_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), doc_name)
        cwd_path = os.path.join(os.path.join(os.getcwd(), doc_name))
        if os.path.exists(local_path):
            return local_path
        elif os.path.exists(cwd_path):
            return cwd_path
        else:
            # https://importlib-resources.readthedocs.io/en/latest/using.html
            from importlib_resources import files
            whl_path = files('').joinpath(doc_name)
            if whl_path.is_file():
                return str(whl_path)
        return None

    def generate_doc(self, output_file_name: str, temp_folder: str):
        """
        This function invokes the generation of the html file then saves it in the requested folder.
        """
        self.logger.debug(self.generate_doc.__name__)
        output_file_name = f'{output_file_name}.html'
        temp_output_path = os.path.join(temp_folder, output_file_name)
        self.logger.info(f"Generating {output_file_name}")

        document_html_filename = self.soup.find('p', {'id': 'document-filepath'})
        document_html_filename.string = output_file_name

        try:
            with open(temp_output_path, 'w') as final_html_file:
                final_html_file.write(str(self.soup))
            self.logger.debug(f"Initial writing to temporary folder succeeded.")
        except Exception as err:
            self.logger.error(f"The operation of saving into temporary folder has FAILED", exc_info=True)
            return

    def finalize_doc(self):
        """
        This function is invoked after the generation of the html file.
        It is responsible for updating the json file with the new data.
        """
        script_tag = self.soup.find('script', {'id': 'types-data'})
        new_json_string = json.dumps(self.json_dict)
        script_tag.string = new_json_string
