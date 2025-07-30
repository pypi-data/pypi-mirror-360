#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List
from abc import ABC, abstractmethod
import pandas

from convert_stream.models import LibraryImage, LibraryPDF, LibImageToPDF, LibConvertPDF
from convert_stream.imagelib import ImageObject
from convert_stream.progress.progress_bar import CreatePbar
from convert_stream.pdf_page import PageDocumentPdf
from convert_stream.pdf_document import DocumentPdf
from convert_stream.pdf_to_images import ConvertPdfToImage
from convert_stream.image_to_pdf import ImageToPdf
from soup_files import File, Directory, ProgressBarAdapter, InputFiles, LibraryDocs


#==================================================================#
# PDF
#==================================================================#


class ABCDocumentStream(ABC):
    """
        Objeto para manipular a exportação de dados PDF    
    """

    def __init__(
            self, *,
            library_pdf: LibraryPDF = LibraryPDF.FITZ,
            library_image: LibraryImage = LibraryImage.OPENCV,
            progress_bar: ProgressBarAdapter = CreatePbar().get(),
    ):
        self.library_pdf: LibraryPDF = library_pdf
        self.liabrary_image: LibraryImage = library_image
        self.progress_bar: ProgressBarAdapter = progress_bar

    @abstractmethod
    def is_null(self) -> bool:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def to_file_pdf(self, f: File):
        """
            Exporta os dados para um arquivo PDF no disco.
        """
        pass

    @abstractmethod
    def to_files_pdf(self, outdir: Directory, *, prefix='pag'):
        """Exporta cada página para um novo arquivo PDF no disco"""
        pass

    @abstractmethod
    def to_files_image(self, d: Directory, *, prefix: str = 'página-para-imagem'):
        """
            Exporta cada página PDF como um arquivo de imagem.
        """
        pass

    @abstractmethod
    def to_images(self) -> List[ImageObject]:
        """Retorna uma lista de imagens, dos documentos adicionados."""
        pass

    @abstractmethod
    def to_document(self) -> DocumentPdf:
        """Converte os itens adicionados em documento"""
        pass

    def inner_images(self) -> List[ImageObject]:
        """
            Retorna uma lista com todas as imagens presentes em todas as páginas
        """
        pass

    @abstractmethod
    def inner_images_to_files(self, d: Directory, prefix: str = 'página-para-imagens') -> None:
        """
            Salva todas as imagens presentes nas páginas em arquivos de imagem.
        """
        pass

    @abstractmethod
    def add_page(self, p: PageDocumentPdf):
        """Adiciona uma página PDF"""
        pass

    @abstractmethod
    def add_pages(self, pages: List[PageDocumentPdf]):
        pass

    @abstractmethod
    def add_page_pdf_bytes(self, bt: bytes):
        """Adicona os bytes de uma página PDF."""
        pass

    @abstractmethod
    def add_file_pdf(self, f: File):
        pass

    @abstractmethod
    def add_files_pdf(self, files: List[File]):
        pass

    @abstractmethod
    def add_document(self, doc: DocumentPdf):
        pass

    @abstractmethod
    def add_image(self, image: ImageObject):
        pass

    @abstractmethod
    def set_paisagem(self):
        """Define todas as páginas como paisagem."""
        pass


class PdfStream(ABCDocumentStream):
    """
        Objeto para manipular a exportação de dados PDF    
    """

    def __init__(
                self, *,
                library_pdf: LibraryPDF = LibraryPDF.FITZ,
                library_image: LibraryImage = LibraryImage.OPENCV,
                lib_image_to_pdf: LibImageToPDF = LibImageToPDF.PILPDF,
                progress_bar: ProgressBarAdapter = CreatePbar().get(),
                maximum_pages: int = 3500
            ):
        super().__init__(library_pdf=library_pdf, library_image=library_image, progress_bar=progress_bar)
        self.library_pdf: LibraryPDF = library_pdf
        self.library_image: LibraryImage = library_image
        self.lib_image_to_pdf: LibImageToPDF = lib_image_to_pdf
        self.document: DocumentPdf = DocumentPdf(
            self.library_pdf, progress_bar=progress_bar,  maximum_pages=maximum_pages
        )
        #
        self.convert_pdf_to_images = ConvertPdfToImage.create(
            self.library_image,
            pbar=self.progress_bar,
            lib_convert_pdf=LibConvertPDF.FITZ
        )
        if self.lib_image_to_pdf == LibImageToPDF.CANVAS:
            self.convert_images_to_pdf: ImageToPdf = ImageToPdf.create_from_canvas(self.library_image)
        elif self.lib_image_to_pdf == LibImageToPDF.PILPDF:
            self.convert_images_to_pdf: ImageToPdf = ImageToPdf.create_from_pil(LibraryImage.PIL)
        elif self.lib_image_to_pdf == LibImageToPDF.FITZ:
            self.convert_images_to_pdf: ImageToPdf = ImageToPdf.create_from_fitz(LibraryImage.PIL)
        else:
            self.convert_images_to_pdf: ImageToPdf = ImageToPdf.create_from_pil(self.library_image)
        
    @property
    def num_pages(self) -> int:
        return self.document.get_num_pages()
    
    @num_pages.setter
    def num_pages(self, num: int):
        self.document.set_num_pages(num)
        
    @property
    def pages(self) -> List[PageDocumentPdf]:
        return self.document.get_pages()
    
    @pages.setter
    def pages(self, new: List[PageDocumentPdf]):
        if not isinstance(new, list):
            return
        self.document.clear()
        for pg in new:
            self.add_page(pg)
        
    def is_null(self) -> bool:
        return self.document.is_null()
    
    def clear(self):
        self.document.clear()
        
    def add_page(self, p: PageDocumentPdf):
        if not isinstance(p, PageDocumentPdf):
            return
        self.document.add_page(p)
            
    def add_pages(self, pages: List[PageDocumentPdf]):
        if not isinstance(pages, list):
            print(f'{__class__.__name__} Erro: Use lista de PageDocumentPdf, não {type(pages)}')
            return
        max_num: int = len(pages)
        self.progress_bar.start()
        for num, p in enumerate(pages):
            self.progress_bar.update(
                ((num+1)/max_num) * 100,
                f'Adicionando página: [{num+1} de {max_num}]'
            )
            self.add_page(p)
        self.progress_bar.stop()

    def add_folder(
                    self, d: Directory, *,
                    file_type: LibraryDocs = LibraryDocs.PDF,
                    max_files: int = 4000
            ):
        files = InputFiles(d, maxFiles=max_files).get_files(file_type=file_type)
        if file_type == LibraryDocs.PDF:
            self.add_files_pdf(files)
        elif file_type == LibraryDocs.IMAGE:
            self.add_images([ImageObject.create_from_file(f) for f in files])

    def add_page_pdf_bytes(self, bt: bytes):
        _page = PageDocumentPdf.create_from_page_bytes(bt, library=self.library_pdf)
        self.add_page(_page)
            
    def add_file_pdf(self, f: File):
        self.document.add_file_pdf(f)

    def add_files_pdf(self, files: List[File]):
        for f in files:
            self.add_file_pdf(f)
            
    def add_document(self, doc: DocumentPdf):
        self.add_pages(doc.get_pages())
        
    def add_image(self, image: ImageObject):
        pg: PageDocumentPdf = self.convert_images_to_pdf.from_image(image)
        self.add_page(pg)

    def add_images(self, images: List[ImageObject]):
        maxnum: int = len(images)
        self.progress_bar.start()
        for n, img in enumerate(images):
            self.progress_bar.update(
                ((n+1)/maxnum) * 100,
                f'Adicionando imagens ao documento: [{n+1}] de {maxnum}'
            )
            self.add_image(img)
        self.progress_bar.stop()
        
    def to_file_pdf(self, f: File):
        if self.is_null():
            print(
                f'{__class__.__name__} Nenhuma página foi adiconada, adicione páginas ao documento para prosseguir!'
            )
        docpdf: DocumentPdf = DocumentPdf(
            self.library_pdf, progress_bar=self.progress_bar, pages=self.pages
        )
        docpdf.to_file_pdf(f)
        
    def to_files_pdf(self, outdir: Directory, *, prefix='documento', replace: bool = False):
        if self.is_null():
            print(
                f'{__class__.__name__} Adicione páginas ao documento para prosseguir!'
            )
            return
        self.document.to_files_pdf(outdir, prefix, replace=replace)

    def to_files_image(self, d: Directory, *, prefix: str = 'pdf-para-imagem', replace: bool = False):
        """
            Exporta cada página PDF como um arquivo de imagem.
        """
        d.mkdir()
        self.progress_bar.start()
        for num, page in enumerate(self.pages):
            output_file: File = d.join_file(f'{prefix}_{page.page_number}.png')
            if not replace:
                if output_file.exists():
                    print(f'[A IMAGEM JÁ EXISTE]: {output_file.absolute()}')
                    continue
            img = self.convert_pdf_to_images.from_page_pdf(page)
            self.progress_bar.update_text(
                f'Exportando página PDF para imagem: [{num+1} de {self.num_pages}] {output_file.basename()}'
            )
            img.to_file(output_file)
        print()
        self.progress_bar.stop()
            
    def to_images(self) -> List[ImageObject]:
        images_obj: List[ImageObject] = []
        for page in self.pages:
            _image: ImageObject = self.convert_pdf_to_images.from_page_pdf(page)
            images_obj.append(_image)
        return images_obj
    
    def to_document(self) -> DocumentPdf:
        return DocumentPdf(
                    self.library_pdf,
                    progress_bar=self.progress_bar,
                    pages=self.pages,
                    maximum_pages=self.document.get_maximum_pages(),
                )
    
    def inner_images(self) -> List[ImageObject]:
        inner_images: List[ImageObject] = []
        for num, p in enumerate(self.pages):
            self.progress_bar.update(
                ((num+1)/self.num_pages) * 100,
                f'Convertendo página [{num+1} de {self.num_pages}]'
            )
            imgs: List[ImageObject] = self.convert_pdf_to_images.inner_images(p.to_bytes())
            inner_images.extend(imgs)
        return inner_images
    
    def inner_images_to_files(self, d: Directory, prefix: str = 'página-para-imagens') -> None:
        """
            Salva todas as imagens presentes nas páginas PDF, em arquivos de imagem.
        """
        d.mkdir()
        for num, page in enumerate(self.pages):
            images = self.convert_pdf_to_images.inner_images(page.to_bytes())
            if len(images) < 1:
                continue
            for n, img in enumerate(images):
                filename = f'{prefix}-{page.page_number}-img-{n+1}.png' 
                img.to_file(d.join_file(filename))
    
    def set_paisagem(self):
        for page in self.pages:
            page.set_paisagem()


#==================================================================#
# Imagens
#==================================================================#


class ImageStream(object):
    """
        Conversão de imagens.
    """
    def __init__(
                self, *,
                library_image: LibraryImage = LibraryImage.OPENCV,
                library_pdf: LibraryPDF = LibraryPDF.FITZ,
                lib_image_to_pdf: LibImageToPDF = LibImageToPDF.FITZ,
                progress_bar: ProgressBarAdapter = CreatePbar().get(),
            ):
        self._images: List[ImageObject] = []
        self.num_images: int = len(self._images)
        self.library_image: LibraryImage = library_image
        self.library_pdf: LibraryPDF = library_pdf
        self.lib_image_to_pdf: LibImageToPDF = lib_image_to_pdf

        self.convert_pdf_to_images = ConvertPdfToImage.create(
            self.library_image,
            pbar=progress_bar,
            lib_convert_pdf=LibConvertPDF.FITZ
        )

        # Objeto para converter PDF em imagem.
        if self.lib_image_to_pdf == LibImageToPDF.PILPDF:
            self.convert_image_to_pdf: ImageToPdf = ImageToPdf.create_from_pil(library_image)
        elif self.lib_image_to_pdf == LibImageToPDF.FITZ:
            self.convert_image_to_pdf: ImageToPdf = ImageToPdf.create_from_fitz(library_image)
        elif self.lib_image_to_pdf == LibImageToPDF.CANVAS:
            self.convert_image_to_pdf: ImageToPdf = ImageToPdf.create_from_canvas(library_image)
        else:
            raise NotImplementedError()

    @property
    def progress_bar(self) -> ProgressBarAdapter:
        return self.convert_pdf_to_images.pbar
        
    @property
    def images(self) -> List[ImageObject]:
        return self._images
    
    @images.setter
    def images(self, imgs: List[ImageObject]) -> None:
        if not isinstance(imgs, list):
            print(f'Erro: Use: list() não {type(imgs)}')
            return
        self.num_images = 0
        for img in imgs:
            self.add_image(img)
        
    def add_image(self, img: ImageObject) -> None:
        if not isinstance(img, ImageObject):
            return
        self._images.append(img)
        self.num_images += 1
        
    def add_images(self, images: List[ImageObject]):
        maxnum: int = len(images)
        self.progress_bar.start()
        for num, i in enumerate(images):
            self.add_image(i)
        self.progress_bar.stop()
    
    def add_file_image(self, f: File):
        img = ImageObject.create_from_file(f, library=self.library_image)
        self.add_image(img)
        
    def add_files_image(self, files: List[File]):
        maxnum: int = len(files)
        for num, f in enumerate(files):
            self.progress_bar.update(
                ((num + 1) / maxnum) * 100,
                f'Adicionando imagens: [{num + 1} de {maxnum}] {f.basename()}'
            )
            self.add_file_image(f)
            
    def is_null(self) -> bool:
        if self.num_images < 1:
            return True
        return False
        
    def clear(self):
        self._images.clear()
        self.num_images = 0
        
    def to_files_image(self, d: Directory, prefix: str = 'imagem', *, replace: bool = False):
        """
        @param replace: substituir arquivos existentes no destino.
        @param d: Diretório para exportar as imagens
        @param prefix: prefixo para o nome das imagens
        @return: None

        @type d: Directory
        @type prefix: str
        @rtype: None
        """
        d.mkdir()
        self.progress_bar.start()
        for num, image in enumerate(self.images):
            filename = f'{prefix}-{num+1}.png'
            output_file: File = d.join_file(filename)
            if not replace:
                if output_file.exists():
                    continue
            self.progress_bar.update(
                ((num+1)/self.num_images) * 100,
                f'Exportando imagem: {num+1} de {self.num_images} [{filename}]'
            )
            image.to_file(output_file)
        self.progress_bar.stop()
                
    def to_pages_pdf(self) -> List[PageDocumentPdf]:
        if self.is_null():
            print(f'{__class__.__name__} Adicione imagens para prosseguir!')
            return []
        new_pages: List[PageDocumentPdf] = []
        maxnum: int = len(self.images)
        self.progress_bar.start()
        for num, image in enumerate(self.images):
            self.progress_bar.update(
                ((num + 1) / maxnum) * 100,
                f'Criando páginas PDF: [{num + 1} de {maxnum}]'
            )
            im = self.convert_image_to_pdf.from_image(image)
            new_pages.append(im)
        self.progress_bar.stop()
        return new_pages

    def to_documet(self) -> DocumentPdf:
        return DocumentPdf(progress_bar=self.progress_bar, pages=self.to_pages_pdf())

    def set_paisagem(self):
        for num, img in enumerate(self.images):
            self.images[num].set_paisagem()
            
    def set_gaussian_blur(self):
        self.progress_bar.start()
        for num, img in enumerate(self.images):
            self.progress_bar.update(
                ((num+1) / self.num_images) * 100,
                f'Removendo o ruido [{num+1} de {self.num_images}]'
            )
            self.images[num].set_gaussian()
        self.progress_bar.stop()
            
    def set_backgroud_black(self):
        self.progress_bar.start()
        for num, img in enumerate(self.images):
            self.progress_bar.update(
                ((num + 1) / self.num_images) * 100,
                f'Removendo o ruido [{num + 1} de {self.num_images}]'
            )
            self.images[num].set_background_black()
        self.progress_bar.stop()

    def set_background_gray(self):
        self.progress_bar.start()
        for num, img in enumerate(self.images):
            self.progress_bar.update(
                ((num + 1) / self.num_images) * 100,
                f'Removendo o ruido [{num + 1} de {self.num_images}]'
            )
            self.images[num].set_background_gray()
        self.progress_bar.stop()
    
    def set_optimize(self):
        self.progress_bar.start()
        for num, img in enumerate(self.images):
            self.progress_bar.update(
                ((num + 1) / self.num_images) * 100,
                f'Otimizando imagem [{num + 1} de {self.num_images}]'
            )
            self.images[num].set_optimize()
        self.progress_bar.stop()
    

def get_data_from_pdfs(*, files_pdf: List[File]) -> pandas.DataFrame:
    """
        Recebe uma lista de arquivos PDF e retorna um DataFrame com os dados das cartas.
    """
    if not isinstance(files_pdf, list):
        raise ValueError(f'Erro: Use: list() não {type(files_pdf)}')
    
    data: List[pandas.DataFrame] = []
    values: List[str] = []
    doc = DocumentPdf()
    for file in files_pdf:
        doc.add_file_pdf(file)
        for page in doc.pages:
            text = page.to_string()
            if (text is not None) and (text != ''):
                values.extend(text.split('\n'))
                data.append(
                    pandas.DataFrame(
                        {
                            'TEXT': values,
                            'ARQUIVO': [file.absolute()] * len(values)
                        }
                    )
                )

        values.clear()
        doc.clear()
    if len(data) < 1:
        return pandas.DataFrame()
    return pandas.concat(data).astype('str')
    