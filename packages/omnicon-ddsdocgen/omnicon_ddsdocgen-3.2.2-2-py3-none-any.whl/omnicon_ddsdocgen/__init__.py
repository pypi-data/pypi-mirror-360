# from .DocGenLogic import DocumentGenerator
import os
import sys
from .Omnicon_DDSDocGen import *

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from omnicon_ddsdocgen import Logger
from omnicon_ddsdocgen import Utils
from omnicon_ddsdocgen import DocGenLogic
from omnicon_ddsdocgen import GeneralFunctions
from omnicon_ddsdocgen import DocumentHandler
from omnicon_ddsdocgen import DocCompareLogic
from omnicon_ddsdocgen.DocGenInterface import DocGenInterface
from omnicon_ddsdocgen import SingleChapterGenerator
from omnicon_ddsdocgen import PdfGen
from omnicon_ddsdocgen import DocxGen
from omnicon_ddsdocgen import DocGenInterface
from omnicon_ddsdocgen import ErrorListHandler
from omnicon_ddsdocgen import SharedEnums
from omnicon_ddsdocgen import ComparisonModule
