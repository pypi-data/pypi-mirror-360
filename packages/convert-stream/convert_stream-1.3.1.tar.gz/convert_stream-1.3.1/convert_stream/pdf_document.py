#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Esté módulo contém classes e objetos para leitura e escrita de arquivos PDFs.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from io import BytesIO
from pandas import DataFrame, concat
from soup_files import File, ProgressBarAdapter, Directory
from convert_stream.models.models_pdf import LibraryPDF, LibImageToPDF
from convert_stream.progress.progress_bar import CreatePbar
from convert_stream.pdf_page import (
    PageDocumentPdf, PagePdfFitz, PagePyPdf2, MODULE_PYPDF2, MODULE_FITZ
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


#=======================================================================#
# Documento PDF
#=======================================================================#


class ABCDocumentPdf(ABC):
    def __init__(
            self,
            library: LibraryPDF = LibraryPDF.FITZ,
            *,
            progress_bar: ProgressBarAdapter = ProgressBarAdapter(),
            pages: List[PageDocumentPdf] = [],
    ):
        self._pages_list: List[PageDocumentPdf] = pages
        self._num_pages: int = 0
        self.library: LibraryPDF = library
        self.progress_bar: ProgressBarAdapter = progress_bar

    def get_num_pages(self) -> int:
        return self._num_pages

    def set_num_pages(self, num: int):
        self._num_pages = num

    def get_pages(self) -> List[PageDocumentPdf]:
        return self._pages_list

    def set_pages(self, pages: List[PageDocumentPdf]):
        self._pages_list = pages

    def clear(self):
        self._pages_list.clear()
        self.set_pages([])

    @abstractmethod
    def is_null(self) -> bool:
        pass

    @abstractmethod
    def add_file_pdf(self, file: File):
        pass

    @abstractmethod
    def add_page(self, page: PageDocumentPdf) -> bool:
        pass

    @abstractmethod
    def add_pages(self, pages: List[PageDocumentPdf]):
        pass

    @abstractmethod
    def add_bytes_page(self, page_bytes: bytes):
        pass

    @abstractmethod
    def add_bytes_file_pdf(self, file_bytes: BytesIO):
        pass

    @abstractmethod
    def add_file_url(self, url: str):
        pass

    @abstractmethod
    def remove_page(self, page_number: int) -> None:
        pass

    @abstractmethod
    def remove_pages(self, num_pages: List[int]):
        pass

    @abstractmethod
    def rotate_page(self, page_number: int, degrees: int):
        pass

    @abstractmethod
    def set_paisagem(self):
        pass

    @abstractmethod
    def to_file_pdf(
                    self, 
                    file: File,
                    prefix: str = 'pagina',
                    replace: bool = False,
                    clear: bool = False
            ):
        pass
    
    @abstractmethod
    def to_files_pdf(
                    self, d: Directory, *, 
                    prefix: str = 'pagina', 
                    replace: bool = False, 
                    clear: bool = False
            ):
        pass

    @abstractmethod
    def to_data(self, separator='\n') -> DataFrame:
        pass

    @abstractmethod
    def to_list(self, separator='\n') -> List[str]:
        pass

    @abstractmethod
    def to_excel(self, file: File, *, separator: str = '\n'):
        pass

    @abstractmethod
    def get_page_number(self, num: int) -> PageDocumentPdf:
        pass

    @abstractmethod
    def get_pages_numbers(self, numbers: List[int]) -> List[PageDocumentPdf]:
        pass

    @abstractmethod
    def get_document_with_text(self, text: str) -> DocumentPdf:
        pass


class DocumentPyPdf2(ABCDocumentPdf):

    def __init__(
                self, library: LibraryPDF = LibraryPDF.FITZ, *,
                progress_bar: ProgressBarAdapter = CreatePbar().get(), 
                pages: List[PageDocumentPdf] = []
            ):
        super().__init__(library, progress_bar=progress_bar, pages=pages)

    def is_null(self):
        if len(self.get_pages()) < 1:
            return True
        return False

    def add_page(self, page: PageDocumentPdf) -> bool:
        if not isinstance(page, PageDocumentPdf):
            raise ValueError(f'Use: PageDocumentPdf(), não {type(page)}')
        self._num_pages += 1
        page.page_number = self.get_num_pages()
        self._pages_list.append(page)
        return True

    def add_pages(self, pages: List[PageDocumentPdf]):
        max_num: int = len(pages)
        self.progress_bar.start()
        for n, p in enumerate(pages):
            self.progress_bar.update(
                ((n + 1) / max_num) * 100,
                f'Adicionando página: [{p.page_number} de {max_num}]'
            )
            self.add_page(p)
        print()
        self.progress_bar.stop()

    def add_file_pdf(self, file: File):
        self.progress_bar.update_text(f'Adicionando arquivo: {file.basename()}')
        pdf_reader = PdfReader(file.absolute())
        num: int = len(pdf_reader.pages)
        for n, page in enumerate(pdf_reader.pages):
            self.progress_bar.update(
                ((n + 1) / num) * 100,
                f'Adicionando página: [{n + 1} de {num}] arquivo: {file.basename()}'
            )
            self.add_page(PageDocumentPdf.create_from_page_pypdf2(page))
        print()

    def add_files_pdf(self, files: List[File]):
        for f in files:
            self.add_file_pdf(f)

    def add_bytes_page(self, page_bytes: bytes):
        self.add_page(PageDocumentPdf.create_from_page_bytes(page_bytes))

    def add_bytes_file_pdf(self, bytes_file_pdf: BytesIO):
        try:
            # Cria um objeto PdfReader a partir dos bytes
            pdf_reader = PdfReader(bytes_file_pdf)
        except Exception as e:
            print(f"Erro ao adicionar PDF a partir de bytes: {e}")
        else:
            # Itera pelas páginas do documento e adiciona ao objeto atual
            page: PageObject = None
            for num, page in enumerate(pdf_reader.pages):
                self.add_page(
                    PageDocumentPdf(PagePyPdf2(page, num + 1))
                )
        finally:
            pass

    def add_file_url(self, url):
        try:
            import requests
        except Exception as e:
            print(e)
            return

        try:
            response: requests.Response = requests.get(url)
        except Exception as e:
            print(e)
            return

        if not response.status_code == 200:
            return
        bt: BytesIO = BytesIO(response.content)
        self.add_bytes_file_pdf(bt)

    def remove_page(self, page_number: int) -> None:
        if (page_number > self.get_num_pages()) or (page_number < 1):
            return
        del self._pages_list[page_number - 1]
        for num, page in enumerate(self._pages_list):
            page.page_number = num + 1
        self.set_num_pages(len(self.get_pages()))

    def remove_pages(self, num_pages: List[int]):
        new: List[PageDocumentPdf] = []
        for idx, page in enumerate(self._pages_list):
            if (idx + 1) in num_pages:
                continue
            new.append(page)
        self.clear()
        self.add_pages(new)
        
    def rotate_page(self, page_number: int, degrees: int):
        if page_number > self.get_num_pages():
            return
        if page_number < 1:
            return
        self._pages_list[page_number - 1].rotate(degrees)

    def set_paisagem(self):
        for page in self._pages_list:
            page.set_paisagem()

    def to_file_pdf(
                    self, 
                    file: File,
                    prefix: str = 'pagina',
                    replace: bool = False,
                    clear: bool = False
            ):
        """
            Salva o documento no disco, usando PyPDF2.
        """
        writer = PdfWriter()
        for page in self._pages_list:
            if not isinstance(page.page, PagePyPdf2):  # Verifica se a página é do tipo PyPdf2
                raise TypeError("Todas as páginas devem ser do tipo PyPdf2PagePdf para salvar com PyPDF2.")
            writer.add_page(page.page.page)  # Adiciona a página ao writer
        with open(file.absolute(), "wb+") as f:
            writer.write(f)
        writer.close()
        if clear:
            self.clear()
            
    def to_files_pdf(
                    self, d: Directory, *, 
                    prefix: str = 'pagina', 
                    replace: bool = False, 
                    clear: bool = False
            ):
        
        for page in self._pages_list:
            if not isinstance(page.page, PagePyPdf2):  # Verifica se a página é do tipo PyPdf2
                raise TypeError("Todas as páginas devem ser do tipo PyPdf2PagePdf para salvar com PyPDF2.")
            
            output_file: File = d.join_file(f'{prefix}_{page.page_number}.pdf')
            if not replace:
                if output_file.exists():
                    print(f'[O ARQUIVO JÁ EXISTE]: {output_file.absolute()}')
                    continue
            writer = PdfWriter()
            writer.add_page(page.page.page)  # Adiciona a página ao writer
            with open(output_file.absolute(), "wb+") as f:
                writer.write(f)
            writer.close()
            del writer
        if clear:
            self.clear()

    def to_data(self, separator: str = '\n') -> DataFrame:
        data: List[DataFrame] = []
        for page in self._pages_list:
            current_df = page.to_table(separator)
            if current_df.empty:
                continue
            current_num = len(current_df)
            current_df['NUM_PÁGINA'] = [page.page_number] * current_num
            data.append(current_df)
        if len(data) == 0:
            return DataFrame()
        return concat(data)

    def to_excel(self, file, *, separator: str = '\n'):
        try:
            self.to_data(separator).to_excel(file.absolute(), index=False)
        except Exception as e:
            print(e)

    def to_list(self, separator='\n') -> List[str]:
        values: List[str] = []
        for p in self._pages_list:
            text = p.to_string()
            if text is not None:
                values.append(text)
        return values

    def get_page_number(self, num) -> PageDocumentPdf | None:
        """
            Retorna a página correspondente ao número fornecido.
            Se o número estiver fora do intervalo, retorna None.
        """
        if not isinstance(num, int):
            raise ValueError(f'{__class__.__name__} Use um número inteiro para referência de páginas, não {type(num)}')
        if (num > self.get_num_pages()) or (num < 1):
            return None
        if self.is_null():
            return None
        return self._pages_list[num - 1]

    def get_pages_numbers(self, numbers: List[int]) -> List[PageDocumentPdf]:
        """
            Retorna uma lista de páginas correspondentes aos números fornecidos.
            Se algum número estiver fora do intervalo, ele será ignorado.
        """
        if not isinstance(numbers, list):
            raise ValueError(
                f'{__class__.__name__} Use uma List[int], não {type(numbers)}'
            )
        if self.is_null():
            return []

        new_pages: List[PageDocumentPdf] = []
        for num in numbers:
            pg = self.get_page_number(num)
            if pg is not None:
                new_pages.append(pg)
        return new_pages

    def get_document_with_text(self, text) -> DocumentPdf:
        """
            Retorna uma lista de páginas que contêm o texto especificado.
            Se o texto não for encontrado, retorna uma lista vazia.
        """
        doc = DocumentPdf(self.library)
        for page in self._pages_list:
            current_text: str = page.to_string()
            if (current_text is not None) and (text in current_text):
                doc.add_page(page)
        return doc


class DocumentFitz(ABCDocumentPdf):

    def __init__(
                self, library: LibraryPDF = LibraryPDF.FITZ, *,
                progress_bar: ProgressBarAdapter = CreatePbar().get(), 
                pages: List[PageDocumentPdf] = []
            ):
        """

        @type pages: List[PageDocumentPdf]
        """
        super().__init__(library, progress_bar=progress_bar, pages=pages)

    def is_null(self):
        if len(self._pages_list) < 1:
            return True
        return False

    def add_page(self, page: PageDocumentPdf):
        if not isinstance(page, PageDocumentPdf):
            raise ValueError(f'Use: PageDocumentPdf(), não {type(page)}')
        self._num_pages += 1
        page.page_number = self.get_num_pages()
        self._pages_list.append(page)
        return True

    def add_pages(self, pages: List[PageDocumentPdf]):
        max_num: int = len(pages)
        for n, p in enumerate(pages):
            self.progress_bar.update(
                ((n + 1) / max_num) * 100,
                f'Adicionando página: [{p.page_number} de {max_num}]'
            )
            self.add_page(p)

    def add_file_pdf(self, file: File):
        doc: fitz.Document = fitz.Document(file.absolute())
        self.progress_bar.update_text(f'Adicionando arquivo: {file.basename()}')
        num: int = len(doc)
        for n, page in enumerate(doc):
            self.progress_bar.update(
                ((n + 1) / num) * 100,
                f'Adicionando página: [{n + 1} de {num}] arquivo: {file.basename()}'
            )
            self.add_page(PageDocumentPdf.create_from_page_fitz(page))
        print()

    def add_files_pdf(self, files: List[File]):
        for f in files:
            self.add_file_pdf(f)

    def add_bytes_page(self, page_bytes: bytes):
        self.add_page(PageDocumentPdf.create_from_page_bytes(page_bytes, library=LibraryPDF.FITZ))

    def add_bytes_file_pdf(self, bytes_file_pdf: BytesIO):
        try:
            # Cria um objeto fitz.Document a partir dos bytes
            pdf_document: fitz.Document = fitz.Document(stream=bytes_file_pdf, filetype="pdf")
            # Itera pelas páginas do documento e adiciona ao objeto atual
            for page in pdf_document:
                self.add_page(
                    PageDocumentPdf(PagePdfFitz(page, page.number))
                )
        except Exception as e:
            print(f"Erro ao adicionar PDF a partir de bytes: {e}")
        finally:
            pass
            #pdf_document.close()  # Fecha o documento após o uso

    def add_file_url(self, url):
        try:
            import requests
        except Exception as e:
            print(e)
            return

        try:
            response: requests.Response = requests.get(url)
        except Exception as e:
            print(e)
            return

        if not response.status_code == 200:
            return
        bt: BytesIO = BytesIO(response.content)
        self.add_bytes_file_pdf(bt)

    def remove_page(self, page_number: int) -> None:
        if not isinstance(page_number, int):
            raise ValueError(
                f'{__class__.__name__} Use um número inteiro para referência de páginas, não {type(page_number)}')

        if (page_number > self.get_num_pages()) or (page_number < 1):
            return
        del self._pages_list[page_number - 1]
        for num, page in enumerate(self._pages_list):
            page.page_number = num + 1
        self.set_num_pages(len(self._pages_list))

    def remove_pages(self, num_pages: List[int]):
        new: List[PageDocumentPdf] = []
        for idx, page in enumerate(self._pages_list):
            if (idx + 1) in num_pages:
                continue
            new.append(page)
        self.clear()
        self.add_pages(new)

    def rotate_page(self, page_number: int, degrees: int):
        if (page_number > self.get_num_pages()) or (page_number < 1):
            return
        self._pages_list[page_number - 1].rotate(degrees)

    def set_paisagem(self):
        for page in self._pages_list:
            page.set_paisagem()

    def to_file_pdf(
                    self, 
                    file: File,
                    prefix: str = 'pagina',
                    replace: bool = False,
                    clear: bool = False
            ):
        """
            Salva o documento no disco, incluíndo todas as páginas (atuais e adicionadas)
        com a lib fitz.
        """
        pdf_document = fitz.Document()  # Criar novo documento PDF.

        for page in self._pages_list:
            if not isinstance(page.page.page, fitz.Page):  # Verifica se a página é do tipo fitz.Page
                raise TypeError(f"Todas as páginas devem ser do tipo [fitz.Page], não {type(page.page.page)}.")
            # Insere as páginas no novo documento
            pdf_document.insert_pdf(
                page.page.page.parent,
                from_page=page.page.page.number,
                to_page=page.page.page.number
            )

        # Salva o documento final no disco
        print(f'{__class__.__name__} Salvando documento com {pdf_document.page_count} páginas')
        pdf_document.save(file.absolute())
        pdf_document.close()
        del pdf_document
        if clear:
            self.clear()
        
    def to_files_pdf(
                    self, d: Directory, *, 
                    prefix: str = 'pagina', 
                    replace: bool = False, 
                    clear: bool = False
            ):
        for page in self._pages_list:
            if not isinstance(page.page.page, fitz.Page):  # Verifica se a página é do tipo fitz.Page
                raise TypeError(f"Todas as páginas devem ser do tipo [fitz.Page], não {type(page.page.page)}.")
            
            output_file = d.join_file(f'{prefix}_{page.page_number}.pdf')
            if not replace:
                if output_file.exists():
                    print(f'[O ARQUIVO JÁ EXISTE]: {output_file.absolute()}')
                    continue
            pdf_document = fitz.Document()  # Criar novo documento PDF.
            # Insere as páginas no novo documento
            pdf_document.insert_pdf(
                page.page.page.parent,
                from_page=page.page.page.number,
                to_page=page.page.page.number
            )
            # Salva o documento final no disco
            print(f'{__class__.__name__} Salvando documento com {pdf_document.page_count} páginas')
            pdf_document.save(output_file.absolute())
            pdf_document.close()
            del pdf_document
        if clear:
            self.clear()

    def to_data(self, separator: str = '\n') -> DataFrame:
        data: List[DataFrame] = []
        for page in self._pages_list:
            current_df = page.to_table()
            if current_df.empty:
                continue
            current_num = len(current_df)
            current_df['NUM_PÁGINA'] = [page.page_number] * current_num
            data.append(current_df)
        if len(data) == 0:
            return DataFrame()
        return concat(data)

    def to_excel(self, file, *, separator: str = '\n'):
        try:
            self.to_data(separator).to_excel(file.absolute(), index=False)
        except Exception as e:
            print(e)

    def to_list(self, separator='\n') -> List[str]:
        values: List[str] = []
        for p in self._pages_list:
            text = p.to_string()
            if text is not None:
                values.append(text)
        return values

    def get_page_number(self, num) -> PageDocumentPdf | None:
        """
            Retorna a página correspondente ao número fornecido.
            Se o número estiver fora do intervalo, retorna None.
        """
        if not isinstance(num, int):
            raise ValueError(f'{__class__.__name__} Use um número inteiro para referência de páginas, não {type(num)}')
        if (num > self.get_num_pages()) or (num < 1):
            return None
        if self.is_null():
            return None
        return self._pages_list[num - 1]

    def get_pages_numbers(self, numbers: List[int]) -> List[PageDocumentPdf]:
        """
            Retorna uma lista de páginas correspondentes aos números fornecidos.
            Se algum número estiver fora do intervalo, ele será ignorado.
        """
        if not isinstance(numbers, list):
            raise ValueError(
                f'{__class__.__name__} Use List[int], não {type(numbers)}')
        if self.is_null():
            return []

        new_pages: List[PageDocumentPdf] = []
        for num in numbers:
            pg = self.get_page_number(num)
            if pg is not None:
                new_pages.append(pg)
        return new_pages

    def get_document_with_text(self, text) -> DocumentPdf:
        """
            Retorna uma lista de páginas que contêm o texto especificado.
            Se o texto não for encontrado, retorna uma lista vazia.
        """
        doc = DocumentPdf(self.library)
        for page in self._pages_list:
            current_text: str = page.to_string()
            if (current_text is not None) and (text in current_text):
                doc.add_page(page)
        return doc


class DocumentPdf(object):

    def __init__(
            self,
            library: LibraryPDF = LibraryPDF.FITZ,
            *,
            maximum_pages: int = 4500,
            progress_bar: ProgressBarAdapter = CreatePbar().get(),
            pages: List[PageDocumentPdf] = [],
    ):
        super().__init__()
        """

        @type pages: List[PageDocumentPdf]
        @type progress_bar: ProgressBarAdapter,
        @type library: LibraryPDF,
        """
        self._maximum_pages: int = maximum_pages
        self.library: LibraryPDF = library
        if self.library == LibraryPDF.PYPDF:
            self.document: ABCDocumentPdf = DocumentPyPdf2(progress_bar=progress_bar)
        elif self.library == LibraryPDF.FITZ:
            self.document: ABCDocumentPdf = DocumentFitz(progress_bar=progress_bar)
        else:
            raise NotImplementedError(f'{__class__.__name__}\nLibraryPDF não implementada: {type(library)}')
        self.document.pages = pages
        self.document.num_pages = len(pages)

    @property
    def progress_bar(self) -> ProgressBarAdapter:
        return self.document.progress_bar

    def get_maximum_pages(self) -> int:
        return self._maximum_pages
    
    def set_maximum_pages(self, num: int):
        self._maximum_pages = num

    def get_num_pages(self) -> int:
        return self.document.get_num_pages()
    
    def set_num_pages(self, num: int):
        self.document.set_num_pages(num)
    
    def get_pages(self) -> List[PageDocumentPdf]:
        return self.document.get_pages()
    
    def set_pages(self, pages: List[PageDocumentPdf]):
        self.document.clear()
        self.document.set_pages(pages)

    def is_null(self) -> bool:
        return self.document.is_null()

    def add_page(self, page: PageDocumentPdf):
        if self.library != page.current_library:
            if self.library == LibraryPDF.FITZ:
                page.set_page_fitz()
            elif self.library == LibraryPDF.PYPDF:
                page.set_page_pypdf2()
        self.document.add_page(page)

    def add_pages(self, pages: List[PageDocumentPdf]):
        max_num: int = len(pages)
        self.progress_bar.start()
        for n, p in enumerate(pages):
            self.progress_bar.update(
                ((n + 1) / max_num) * 100,
                f'Adicionando página: [{p.page_number} de {max_num}]'
            )
            self.add_page(p)
        print()
        self.progress_bar.stop()

    def add_file_pdf(self, file: File):
        print(f'Adicionando arquivo: {file.basename()}')
        self.document.add_file_pdf(file)

    def add_files_pdf(self, files: List[File]):
        for f in files:
            self.add_file_pdf(f)

    def add_bytes_page(self, page_bytes: bytes):
        self.document.add_bytes_page(page_bytes)

    def add_bytes_file_pdf(self, file_bytes: BytesIO):
        self.document.add_bytes_file_pdf(file_bytes)

    def add_file_url(self, url):
        print(f'Adicionando URL: {url}')
        self.document.add_file_url(url)

    def remove_page(self, page_number: int) -> None:
        self.document.remove_page(page_number)

    def remove_pages(self, num_pages: List[int]):
        self.document.remove_pages(num_pages)

    def rotate_page(self, page_number: int, degrees: int):
        self.document.rotate_page(page_number, degrees)

    def set_paisagem(self):
        self.document.set_paisagem()

    def to_file_pdf(self, file: File, clear: bool = False) -> bool:
        if self.is_null():
            print(f'O documento está vazio, adicione páginas ou arquivos para prosseguir!')
            return False
        self.document.to_file_pdf(file)
        if clear:
            self.clear()
        return True

    def to_files_pdf(self, d: Directory, prefix='pag', *, replace: bool = False, clear: bool = False):
        self.document.to_files_pdf(d, prefix=prefix, replace=replace, clear=clear)
        if clear:
            self.clear()

    def to_data(self, separator: str = '\n') -> DataFrame:
        return self.document.to_data(separator)

    def to_excel(self, file, *, separator='\n'):
        self.document.to_excel(file, separator=separator)

    def to_list(self, separator='\n') -> List[str]:
        return self.document.to_list(separator)

    def clear(self):
        self.document.clear()
        self.document.pages = []

    def get_page_number(self, num) -> PageDocumentPdf:
        return self.document.get_page_number(num)

    def get_pages_numbers(self, numbers) -> List[PageDocumentPdf]:
        return self.document.get_pages_numbers(numbers)

    def get_document_with_text(self, text) -> DocumentPdf:
        """
            Retorna um novo documento com as páginas que contém o texto informado no parâmetro,
        se o texto não for encontrado, retorna um documento vazio.
        """
        return self.document.get_document_with_text(text)
       
    @classmethod
    def create_from_file(cls, file: File, *, library: LibraryPDF = LibraryPDF.FITZ) -> DocumentPdf:
        doc = cls(library)
        doc.add_file_pdf(file)
        return doc


class FileDocumentPdf(DocumentPdf):

    def __init__(
            self,
            file_pdf: File,
            *,
            library: LibraryPDF = LibraryPDF.FITZ,
            progress_bar: ProgressBarAdapter = CreatePbar().get(),
    ):
        """

        :param library: Tipo de biblioteca PDF fitz/PyPDF2
        :param progress_bar: barra de progresso
        :param file_pdf: Arquivo PDF.
        """
        super().__init__(library, progress_bar=progress_bar, pages=[])
        self.file_pdf: File = file_pdf
        self.document.add_file_pdf(self.file_pdf)

    def to_data(self, separator: str = '\n') -> DataFrame:
        df: DataFrame = super().to_data(separator)
        maxnum: int = len(df)
        df['NOME_ARQUIVO'] = [self.file_pdf.name()] * maxnum
        df['TIPO_ARQUIVO'] = [self.file_pdf.extension()] * maxnum
        df['ARQUIVO'] = [self.file_pdf.absolute()] * maxnum
        return df

