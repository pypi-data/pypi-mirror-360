#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
from __future__ import annotations
from abc import abstractmethod, ABC
from io import BytesIO
from typing import List
from enum import Enum
from pandas import DataFrame
from soup_files import File, Directory
from convert_stream.models.models_image import ABCImageObject, LibraryImage
from convert_stream.progress.progress_bar import ProgressBarAdapter, ProgressBarSimple
from PyPDF2 import PageObject

try:
    import fitz
except:
    import PyMuPDF as fitz


class LibraryPDF(Enum):
    """Enumerar as libs para manipulação de PDF"""
    PYPDF = 'pypdf2'
    FITZ = 'fitz'


class LibImageToPDF(Enum):
    CANVAS = 'canvas'
    PILPDF = 'pil'
    FITZ = 'fitz'


class LibConvertPDF(Enum):
    FITZ = 'fitz'


# Representação de uma página PDF.
class ABCPagePdf(ABC):
    """Abstração de uma página PDF"""

    def __init__(self):
        super().__init__()
        self.page: fitz.Page | PageObject = None
        self.current_library: LibraryPDF = None
        self.page_number: int = 0
        self.width: int = 0
        self.height: int = 0

    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def to_list(self, separator: str = '\n') -> List[str]:
        pass

    @abstractmethod
    def to_table(self, separator: str = '\n') -> DataFrame:
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

    @abstractmethod
    def is_paisagem(self) -> bool:
        pass

    @abstractmethod
    def set_paisagem(self):
        pass

    @abstractmethod
    def set_page_pypdf2(self):
        pass

    @abstractmethod
    def set_page_fitz(self):
        pass

    @abstractmethod
    def rotate(self, degrees: int):
        pass

    @classmethod
    def create_from_page_bytes(cls, page_bytes: bytes) -> ABCPagePdf:
        pass

    @classmethod
    def create_from_page_fitz(cls, page: object) -> ABCPagePdf:
        pass

    @classmethod
    def create_from_page_pypdf2(cls, page: object) -> ABCPagePdf:
        pass



