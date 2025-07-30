import os
import sys
import logging
import time

if sys.platform.startswith('win'):
    import win32com
    import pythoncom

from . import Logger
from .DocxGen import DocxGen

class PdfGen(DocxGen):
    def __init__(self, title: str, new_version: str,  time: str, origin_version: str = "",
                        origin_dds_types_files: list = None,
                        new_dds_types_files: list = None,
                        origin_dds_topics_types_mapping: str = "",
                        new_dds_topics_types_mapping: str = "",
                        average_str_length: int = 1,
                        average_sequence_length: int = 1):
        """
        This class allows creating one of two documents; an ICD (created by docGen) and a comparison document (created
        by DocCompare). The difference is in the title page; the version in the ICD is added on its on, but in the
        comparison document both versions are displayed in a table along with the files/folders used by each version

        IMPORTANT:
        WHEN origin_version COMES EMPTY , WE KNOW IT'S AN ICD, and new_version IS USED AS THE VERSION.
        WHEN origin_version IS NOT EMPTY, WE KNOW IT'S A COMPARISON DOCUMENT.

        """
        super().__init__(title=title,
                         new_version=new_version,
                         time=time,
                         origin_version=origin_version,
                         origin_dds_types_files=origin_dds_types_files,
                         new_dds_types_files=new_dds_types_files,
                         origin_dds_topics_types_mapping=origin_dds_topics_types_mapping,
                         new_dds_topics_types_mapping=new_dds_topics_types_mapping,
                         average_str_length=average_str_length,
                         average_sequence_length=average_sequence_length)
        self.logger = Logger.add_logger(__name__)

    def generate_doc(self, output_file_name: str, temp_folder: str)->str:
        # TODO if there is an issue while using at UI then revert the following 2 lines
        logger = Logger.add_logger("__name__")
        sys.stderr = Logger.LoggerFakeWriter(logger.error)

        self.logger.debug(self.generate_doc.__name__)
        # Create the docx using DocxGen
        super().generate_doc(output_file_name, temp_folder)

        temp_docx_file_name = f'{output_file_name}.docx'
        temp_docx_path = os.path.abspath(os.path.join(temp_folder, temp_docx_file_name))
        temp_pdf_file_name = f'{output_file_name}.pdf'
        temp_pdf_path = os.path.abspath(os.path.join(temp_folder, temp_pdf_file_name))

        # Convert to PDF and save into the requested folder
        word = None
        try:
            self.logger.debug(f"saving {temp_pdf_file_name} into {temp_folder}")
            pythoncom.CoInitialize()

            word = win32com.client.DispatchEx("Word.Application")
            word.DisplayAlerts = False
            wdFormatPDF = 17
            doc = word.Documents.Open(str(temp_docx_path))
            doc.SaveAs(str(temp_pdf_path), FileFormat=wdFormatPDF)
            # let windows finish propagating the file to explorer (for big files)
            time.sleep(3)
            doc.Close(SaveChanges=False)
            self.logger.info(f"File saved successfully into '{temp_pdf_path}'")

        except Exception as err:
            self.logger.error(f"Could not save '{temp_pdf_path}'.", exc_info=True)
        finally:
            if word:
                word.Quit()
                del word
            pythoncom.CoUninitialize()

        # sys.stderr = Logger.LoggerWriter(logger.error)

