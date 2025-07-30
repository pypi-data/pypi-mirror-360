#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from soup_files import File, ProgressBarAdapter
from convert_stream.models import ABCImageObject, ABCPagePdf
from convert_stream.progress.progress_bar import CreatePbar
from convert_stream.imagelib import ImageObject, LibraryImage
from convert_stream.pdf_document import DocumentPdf
from convert_stream.models.models_pdf import LibraryPDF, LibImageToPDF
from convert_stream.pdf_page import (
    PageDocumentPdf, MODULE_PYPDF2, MODULE_FITZ
)

if MODULE_PYPDF2:
    from PyPDF2 import PdfReader, PdfWriter, PageObject
if MODULE_FITZ:
    try:
        import fitz
    except:
        try:
            import pymupdf
        except Exception as e:
            print(e)


#########################################################################
# Converter IMAGEM para Arquivo ou página PDF.
#########################################################################


class ABCConvertImageToPdf(ABC):
    """
        Conveter imagem em página PDF.
    """

    def __init__(
            self,
            library_image: LibraryImage = LibraryImage.OPENCV,
            *,
            progress_bar: ProgressBarAdapter = CreatePbar().get(),
    ):
        super().__init__()
        self.library_image: LibraryImage = library_image
        self.lib_image_to_pdf: LibImageToPDF = LibImageToPDF.FITZ
        self.pbar: ProgressBarAdapter = progress_bar

    @abstractmethod
    def from_image_file(self, file: File) -> PageDocumentPdf:
        """
            Converte um arquivo de imagem em página PDF.
        """
        pass

    @abstractmethod
    def from_image(self, img: ImageObject) -> PageDocumentPdf:
        """Converte um objeto imagem em página PDF."""
        pass

    @abstractmethod
    def from_image_bytes(self, img_bytes: bytes) -> PageDocumentPdf:
        """Converte os bytes de uma imagem e uma página PDF."""
        pass


class IConvertConvertImageToPdfFitz(ABCConvertImageToPdf):
    """
        Implementação para converter imagens em PDF com fitz.
    """
    def __init__(
            self,
            library_image, *,
            progress_bar: ProgressBarAdapter = CreatePbar().get()
            ):
        """

        @param library_image: LibrayImage
        @param progress_bar: ProgressBarAdapter
        """
        super().__init__(library_image, progress_bar=progress_bar)
        self.lib_image_to_pdf = LibraryPDF.FITZ
        
    def from_image_file(self, file: File) -> PageDocumentPdf:
        # https://pymupdf.readthedocs.io/en/latest/recipes-images.html
        doc = fitz.Document()
        img_document: fitz.Document = fitz.Document(file.absolute())  # open pic as document
        rect = img_document[0].rect  # pic dimension
        pdfbytes = img_document.convert_to_pdf()  # make a PDF stream
        img_document.close()  # no longer needed
        image_doc_pdf = fitz.Document("pdf", pdfbytes)  # open stream as PDF
        
        page = doc.new_page(
                    width=rect.width,  # new page with ...
                    height=rect.height # pic dimension
            )  
        page.show_pdf_page(rect, image_doc_pdf, 0)  # image fills the page
        return PageDocumentPdf.create_from_page_fitz(page)
        
    def from_image(self, img: ImageObject) -> PageDocumentPdf:
        return self.from_image_bytes(img.to_bytes())
    
    def from_image_bytes(self, image_bytes: bytes) -> PageDocumentPdf:
        doc: fitz.Document = fitz.Document()
        
        # Criar um Pixmap diretamente dos bytes da imagem
        pix = fitz.Pixmap(BytesIO(image_bytes))

        # Criar uma nova página do tamanho da imagem
        page = doc.new_page(width=pix.width, height=pix.height)

        # Inserir a imagem na página
        page.insert_image(page.rect, pixmap=pix)
        _p = PageDocumentPdf.create_from_page_fitz(page)
        #doc.close()
        return _p


class IConvertConvertImageToPdfCavas(ABCConvertImageToPdf):
    """
        Implementação para converter uma imagem em página PDF (canvas).
    """
    def __init__(self, library_image):
        super().__init__(library_image)
        self.lib_image_to_pdf: LibImageToPDF = LibImageToPDF.CANVAS
        
    def from_image(self, img: ImageObject) -> PageDocumentPdf:
        """

        @param img: ImageObject
        @return: PageDocumentPdf
        """
        # Cria buffer de memória para o PDF
        buffer_pdf = BytesIO()

        # Cria o canvas associado ao buffer
        _canvas: Canvas = canvas.Canvas(buffer_pdf, pagesize=letter)
        # Adicionar a imagem.
        _canvas.drawImage(
                ImageReader(img.to_image_pil()), 
                0, 
                0, 
                width=letter[0], 
                height=letter[1], 
                preserveAspectRatio=True, 
                anchor='c'
            )
        _canvas.showPage()
    
        # Finaliza o PDF
        _canvas.save()

        # Move o ponteiro do buffer para o início
        buffer_pdf.seek(0)

        # Obtém os bytes do PDF
        pdf_bytes = buffer_pdf.getvalue()

        # Fecha o buffer (opcional, mas recomendado)
        buffer_pdf.close()
        
        # Gerar a página PDF
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=LibraryPDF.FITZ)
        
    def from_image_file(self, file: File) -> PageDocumentPdf:
        """
            Converter um arquivo de imagem em páginas PDF
        """
        img = ImageObject.create_from_file(file, library=self.library_image)
        return self.from_image(img)
    
    def from_image_bytes(self, img_bytes:bytes) -> PageDocumentPdf:
        return self.from_image(
                ImageObject.create_from_bytes(img_bytes, library=self.library_image)
            )


class IConvertConvertImageToPdfPIL(ABCConvertImageToPdf):
    """
        Implementação para converter uma imagem em página PDF (PIL).
    """
    def __init__(self, library_image):
        super().__init__(library_image)
        self.lib_image_to_pdf: LibImageToPDF = LibImageToPDF.PILPDF
        
    def from_image(self, img:ImageObject) -> PageDocumentPdf:
        img_pil = img.to_image_pil()
        buff = BytesIO()
        # Converter e salvar como PDF
        img_pil.save(buff, "PDF")
        pdf_bytes: bytes = buff.getvalue()
        buff.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=LibraryPDF.FITZ)
        
    def from_image_file(self, file: File) -> PageDocumentPdf:
        """
            Converter um arquivo de imagem em páginas PDF
        """
        # Carregar a imagem
        imagem:Image.Image = Image.open(file.absolute())
        buff = BytesIO()
        # Converter e salvar como PDF
        imagem.save(buff, "PDF")
        pdf_bytes: bytes = buff.getvalue()
        buff.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=LibraryPDF.FITZ)
    
    def from_image_bytes(self, img_bytes:bytes) -> PageDocumentPdf:
        img_pil = Image.open(BytesIO(img_bytes))
        buff_pdf = BytesIO()
        # Converter e salvar como PDF
        img_pil.save(buff_pdf, "PDF")
        pdf_bytes: bytes = buff_pdf.getvalue()
        buff_pdf.close()
        return PageDocumentPdf.create_from_page_bytes(pdf_bytes, library=LibraryPDF.FITZ)
         
         
class ImageToPdf(object):
    """
        Converter Imagem em páginas PDF.
    """
    def __init__(self, convert_image_to_pdf: ABCConvertImageToPdf):
        self.convert_image_to_pdf: ABCConvertImageToPdf = convert_image_to_pdf

    @property
    def lib_image_to_pdf(self) -> LibImageToPDF:
        return self.convert_image_to_pdf.lib_image_to_pdf
            
    def from_image_file(self, file: File) -> PageDocumentPdf:
        return self.convert_image_to_pdf.from_image_file(file)
    
    def from_image(self, img: ImageObject) -> PageDocumentPdf:
        if not isinstance(img, ImageObject):
            raise ValueError(f'{__class__.__name__}\nUser: ImageObject(), não {type(img)}')
        return self.convert_image_to_pdf.from_image(img)
    
    def from_image_bytes(self, img_bytes) -> PageDocumentPdf:
        return self.convert_image_to_pdf.from_image_bytes(img_bytes)
    
    @classmethod
    def create_from_pil(
                    cls, library_image: LibraryImage = LibraryImage.OPENCV,
            ) -> ImageToPdf:
        #
        img_convert: ABCConvertImageToPdf = IConvertConvertImageToPdfPIL(library_image)
        return cls(img_convert)
    
    @classmethod
    def create_from_canvas(
                cls,
                library_image: LibraryImage = LibraryImage.OPENCV
            ) -> ImageToPdf:
        img_convert = IConvertConvertImageToPdfCavas(library_image)
        return cls(img_convert)
    
    @classmethod
    def create_from_fitz(
                cls,
                library_image: LibraryImage = LibraryImage.OPENCV
            ) -> ImageToPdf:
        img_convert = IConvertConvertImageToPdfFitz(library_image)
        return cls(img_convert)


