#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from io import BytesIO
from convert_stream.progress.progress_bar import ProgressBarAdapter, ProgressBarSimple
from convert_stream.pdf_document import DocumentPdf, PageDocumentPdf, LibraryPDF
from convert_stream.pdf_to_images import ConvertPdfToImage, ImageObject
from convert_stream.image_to_pdf import ImageToPdf
from soup_files import File

try:
    import fitz
except:
    import PyMuPDF as fitz


class ABCCompressPdfAdaptative(ABC):
    """
        Compressão de documentos PDF.
    """
    def __init__(
                self, document: DocumentPdf,
                *,
                dpi: int = 72,
            ):
        super().__init__()
        self.dpi: int = dpi
        self.document: DocumentPdf = document

    @property
    def pbar(self) -> ProgressBarAdapter:
        return self.document.progress_bar

    @abstractmethod
    def to_file(self, file: File):
        pass

    @abstractmethod
    def set_compression(self):
        pass


class ImplementCompressFitz(ABCCompressPdfAdaptative):

    def __init__(self, document: DocumentPdf, *, dpi: int = 100):
        super().__init__(document, dpi=dpi)

    def set_compression(self):

        # Parâmetros para reduzir imagens incorporadas
        mat = fitz.Matrix(1, 1)  # Sem redimensionamento, apenas recompressão

        # Novo PDF
        compress_pdf = fitz.open()

        for page_pdf in self.document.pages:
            # Extrair a página como imagem
            pix = page_pdf.page.page.get_pixmap(matrix=mat, alpha=False, dpi=self.dpi)

            # Adicionar página nova no PDF final
            new_page = compress_pdf.new_page(
                width=page_pdf.page.page.rect.width,
                height=page_pdf.page.page.rect.height
            )

            # Inserir a imagem da página
            new_page.insert_image(page_pdf.page.page.rect, pixmap=pix)
        self.document.clear()
        for page in compress_pdf:
            p = PageDocumentPdf.create_from_page_fitz(page)
            self.document.add_page(p)

    def to_file(self, file: File):
        self.document.to_file_pdf(file)


class ImplementCompressPIL(ABCCompressPdfAdaptative):

    def __init__(self, document: DocumentPdf, *, dpi: int = 100):
        super().__init__(document, dpi=dpi)
        self.convert_pdf_to_image = ConvertPdfToImage(dpi=self.dpi)
        self.image_convert = ImageToPdf.create_from_pil()

    def set_compression(self):
        print()
        self.pbar.start()
        pages_document: List[PageDocumentPdf] = []
        maxnum = len(self.document.pages)
        for num, page in enumerate(self.document.pages):
            self.pbar.update(
                ((num+1)/self.document.num_pages) * 100,
                f'Covertendo página PDF em Imagem: [{num+1} de {maxnum}]'
            )
            image: ImageObject = self.convert_pdf_to_image.from_page_pdf(page, self.dpi)
            image.set_optimize()
            pages_document.append(self.image_convert.from_image(image))
        self.document.clear()
        self.document.add_pages(pages_document)

    def to_file(self, file: File):
        self.document.to_file_pdf(file)


class CompressDocument(object):
    def __init__(self, compress: ABCCompressPdfAdaptative):
        self.compress: ABCCompressPdfAdaptative = compress

    def to_file(self, file: File):
        self.compress.set_compression()
        self.compress.to_file(file)

    def to_document(self) -> DocumentPdf:
        self.compress.set_compression()
        return DocumentPdf(
            self.compress.document.library,
            progress_bar=self.compress.document.progress_bar,
            pages=self.compress.document.pages,
        )

    def to_pages(self) -> List[PageDocumentPdf]:
        return self.compress.document.pages

    @classmethod
    def create_from_document(cls, doc: DocumentPdf, dpi: int = 72) -> CompressDocument:
        return cls(ImplementCompressFitz(doc, dpi=dpi))

    @classmethod
    def create_from_file(cls, file: File, dpi: int = 72) -> CompressDocument:
        doc = DocumentPdf()
        doc.add_file_pdf(file)
        return cls(
                    ImplementCompressFitz(doc, dpi=dpi)
            )