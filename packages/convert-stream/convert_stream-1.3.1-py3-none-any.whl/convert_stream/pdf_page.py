#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
from __future__ import annotations
from typing import List
from io import BytesIO

MODULE_PYPDF2: bool = False
MODULE_FITZ: bool = False

# Checar a lib fitz
try:
    import fitz
except:
    try:
        import pymupdf as fitz
    except:
        pass
    else:
        MODULE_FITZ = True
else:
    MODULE_FITZ = True

# Checar a lib PyPDF2
try:
    from PyPDF2 import PdfReader, PdfWriter, PageObject
except:
    pass
else:
    MODULE_PYPDF2 = True

from pandas import DataFrame
from convert_stream.models.models_pdf import LibraryPDF, ABCPagePdf


#======================================================================#
# Página PDF
#======================================================================#


class PagePyPdf2(ABCPagePdf):
    """Implementação para manipular páginas PDF com PyPDF2"""

    def __init__(self, page: PageObject, page_number: int):
        super().__init__()
        if not isinstance(page, PageObject):
            raise ValueError(f'{__class__.__name__} Use: PageObject(), não {type(page)}')
        self.page: PageObject = page
        self.page_number: int = page_number
        self.current_library = LibraryPDF.PYPDF
        self.width = self.page.mediabox.width
        self.height = self.page.mediabox.height

    def to_string(self) -> str:
        s = self.page.extract_text()
        if (s is None) or (s == ''):
            return None
        return s

    def to_list(self, separator: str = '\n') -> List[str]:
        s = self.to_string()
        return self.to_string().split(separator) if s is not None else []

    def to_table(self, separator: str = '\n') -> DataFrame:
        text_page: List[str] = self.to_list(separator)
        tb = {
            'TEXT': [],
            'NUM_LINHA': [],
            'NUM_PÁGINA': [],
        }
        for n, text in enumerate(text_page):
            tb['TEXT'].append(text)
            tb['NUM_LINHA'].append(n + 1)
            tb['NUM_PÁGINA'].append(self.page_number),
        return DataFrame(tb)

    def rotate(self, degrees: int):
        self.page.rotate(degrees)

    def to_bytes(self) -> bytes:
        pdf_writer = PdfWriter()
        pdf_writer.add_page(self.page)
        output_bytes = BytesIO()
        pdf_writer.write(output_bytes)
        pdf_bytes = output_bytes.getvalue()
        output_bytes.close()
        return pdf_bytes

    def set_paisagem(self):
        if not self.is_paisagem():
            self.rotate(-90)

    def is_paisagem(self):
        return False if self.page.mediabox.width < self.page.mediabox.height else True

    def set_page_fitz(self):
        pass

    def set_page_pypdf2(self):
        pass

    @classmethod
    def create_from_page_bytes(cls, page_bytes) -> PagePyPdf2:
        try:
            pdf_writer = PdfWriter()
            pdf_reader = PdfReader(BytesIO(page_bytes))  # Carrega o PDF a partir dos bytes
            pdf_writer.add_page(pdf_reader.pages[0])  # Adiciona cada página ao escritor
        except Exception as e:
            print(e)
            return None
        else:
            return cls(pdf_writer.pages[0], 1)

    @classmethod
    def create_from_page_pypdf2(cls, page: PageObject) -> PagePyPdf2:
        if not isinstance(page, PageObject):
            raise ValueError(f'{__class__.__name__}Use: PageObject(), não {type(page)}')
        return cls(page, 1)

    @classmethod
    def create_from_page_fitz(cls, page) -> None:
        pass


class PagePdfFitz(ABCPagePdf):
    """Implementação para manipular páginas PDF com fitz"""

    def __init__(self, page: fitz.Page, page_number: int):
        super().__init__()
        self.page: fitz.Page = page
        self.page_number: int = page_number
        self.current_library = LibraryPDF.FITZ
        self.width = self.page.rect.width
        self.height = self.page.rect.height

    def to_string(self) -> str:
        s = self.page.get_text()
        if (s is None) or (s == ''):
            return None
        return s

    def to_list(self, separator: str = '\n') -> List[str]:
        s = self.to_string()
        return self.to_string().split(separator) if s is not None else []

    def to_table(self, separator: str = '\n') -> DataFrame:
        text_page: List[str] = self.to_list(separator)
        tb = {
            'TEXT': [],
            'NUM_LINHA': [],
        }
        for n, text in enumerate(text_page):
            tb['TEXT'].append(text)
            tb['NUM_LINHA'].append(n + 1)
        return DataFrame(tb)

    def rotate(self, degrees: int):
        # Ajuste para rotação anti-horária
        current_rotation = self.page.rotation  # Obter rotação atual da página
        new_rotation = (current_rotation + degrees) % 360  # Atualizar a rotação acumulativa
        self.page.set_rotation(new_rotation)  # Aplicar a nova rotação

    def to_bytes(self) -> bytes:
        temp_doc = fitz.Document()
        temp_doc.insert_pdf(self.page.parent, from_page=self.page.number, to_page=self.page.number)
        return temp_doc.write()

    def set_paisagem(self):
        if not self.is_paisagem():
            self.page.set_rotation(-90)  # Rotaciona 90 graus para paisagem

    def is_paisagem(self):
        return False if self.page.rect.height > self.page.rect.width else True

    def set_page_fitz(self):
        pass

    def set_page_pypdf2(self):
        pass

    @classmethod
    def create_from_page_bytes(cls, page_bytes) -> PagePdfFitz | None:
        try:
            merged_document = fitz.Document()
            temp_doc: fitz.Document = fitz.Document(stream=page_bytes, filetype="pdf")
            merged_document.insert_pdf(temp_doc)
            current_page: fitz.Page = merged_document[0]
        except Exception as e:
            print(e)
            return None
        else:
            return cls(current_page, current_page.number)

    @classmethod
    def create_from_page_pypdf2(cls, page: PageObject) -> None:
        pass

    @classmethod
    def create_from_page_fitz(cls, page: fitz.Page) -> PagePdfFitz:
        if not isinstance(page, fitz.Page):
            raise ValueError(f'{__class__.__name__}Use: Page(), não {type(page)}')
        return cls(page, 1)


#======================================================================#
# Adapter para trabalhar com uma página PDF.
#======================================================================#


class PageDocumentPdf(object):
    def __init__(self, page: PagePdfFitz | PagePyPdf2):
        self.__page: PagePdfFitz | PagePyPdf2 = page
        self.page_number: int = page.page_number
        self.current_library: LibraryPDF = page.current_library

    @property
    def width(self) -> int:
        return self.page.width

    @property
    def height(self) -> int:
        return self.page.height

    @property
    def page(self) -> ABCPagePdf:
        return self.__page

    @page.setter
    def page(self, new: ABCPagePdf):
        if isinstance(new, PagePyPdf2):
            self.__page = new
        elif isinstance(new, PagePdfFitz):
            self.__page = new
        elif isinstance(new, PageDocumentPdf):
            self.__page = new.page
        else:
            raise ValueError(f'{__class__.__name__} Use: ABCPagePdf(), não {type(new)}')
        self.page_number = self.__page.page_number
        self.current_library = self.__page.current_library

    def __eq__(self, value: ABCPagePdf):
        return (self.to_string() == value.to_string()) and (self.page_number == value.page_number)

    def __hash__(self) -> int:
        h1 = hash(self.page_number)
        h2 = hash(self.to_string())
        return hash(f'{h1}_{h2}')

    def to_string(self) -> str | None:
        return self.page.to_string()

    def to_list(self, separator: str = '\n') -> List[str]:
        return self.page.to_list(separator)

    def to_table(self, separator: str = '\n') -> DataFrame:
        return self.page.to_table(separator)

    def to_bytes(self) -> bytes:
        return self.page.to_bytes()

    def is_paisagem(self) -> bool:
        return self.page.is_paisagem()

    def set_paisagem(self):
        self.page.set_paisagem()

    def set_page_fitz(self):
        if self.page.current_library == LibraryPDF.FITZ:
            return
        pg = PagePdfFitz.create_from_page_bytes(self.to_bytes())
        self.page = pg

    def set_page_pypdf2(self):
        if self.page.current_library == LibraryPDF.PYPDF:
            return
        pg = PagePyPdf2.create_from_page_bytes(self.to_bytes())
        self.page = pg

    def rotate(self, degrees: int):
        self.page.rotate(degrees)

    @classmethod
    def create_from_page_bytes(
            cls,
            page_bytes: bytes,
            *,
            library: LibraryPDF = LibraryPDF.PYPDF
    ) -> PageDocumentPdf:
        if library == LibraryPDF.PYPDF:
            pg = PagePyPdf2.create_from_page_bytes(page_bytes)
        elif library == LibraryPDF.FITZ:
            pg = PagePdfFitz.create_from_page_bytes(page_bytes)
        else:
            raise ValueError("Biblioteca inválida: escolha 'fitz' ou 'pypdf2'.")
        #
        return cls(pg)

    @classmethod
    def create_from_page_pypdf2(cls, page: PageObject) -> PageDocumentPdf:
        if not MODULE_PYPDF2:
            raise ValueError(f'[!] Instale PyPDF2 para prosseguir')
        pg = PagePyPdf2.create_from_page_pypdf2(page)
        return cls(pg)

    @classmethod
    def create_from_page_fitz(cls, page: fitz.Page) -> PageDocumentPdf:
        if not MODULE_FITZ:
            raise ValueError(f'[!] Instale fitz para prosseguir')
        pg = PagePdfFitz.create_from_page_fitz(page)
        return cls(pg)
