#!/usr/bin/env python3
#

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict
from soup_files import File, Directory, InputFiles, LibraryDocs, ProgressBarAdapter
import pandas as pd
from convert_stream import CreatePbar, DocumentPdf, PageDocumentPdf


class ColumnTable(Enum):

    NUMLINHA = 'NUM_LINHA'
    NUMPAGE = 'NUM_PÁGINA'
    TEXT = 'TEXTO'
    FILE = 'ARQUIVO'
    FILENAME = 'NOME_ARQUIVO'
    DIR = 'PASTA'
    FILETYPE = 'TIPO_ARQUIVO'

    @classmethod
    def to_list(cls) -> List[str]:
        return [
            cls.NUMLINHA.value,
            cls.NUMPAGE.value,
            cls.TEXT.value,
            cls.FILE.value,
            cls.FILENAME.value,
            cls.FILETYPE.value,
            cls.DIR.value,
        ]


class ABCTableFiles(ABC):

    def __init__(self, pbar: ProgressBarAdapter = CreatePbar().get()):
        self.pbar: ProgressBarAdapter = pbar
        self.files: List[File] = []

    @abstractmethod
    def add_file(self, file: File):
        pass

    @abstractmethod
    def to_data(self) -> pd.DataFrame:
        pass


def get_void_df() -> pd.DataFrame:
    """

    @rtype: pd.DataFrame
    """
    df = pd.DataFrame()
    df[ColumnTable.NUMPAGE.value] = []
    df[ColumnTable.NUMLINHA.value] = []
    df[ColumnTable.TEXT.value] = []
    df[ColumnTable.FILENAME.value] = []
    df[ColumnTable.FILETYPE.value] = []
    df[ColumnTable.FILE.value] = []
    df[ColumnTable.DIR.value] = []
    return df


def create_df_from_values(file: File, values: List[str]) -> pd.DataFrame:
    """

    @rtype: pd.DataFrame
    """
    df = get_void_df()
    if len(values) < 1:
        return df

    values_num_line = []
    values_text = []
    values_filename = []
    values_file_type = []
    values_filepath = []
    values_dir = []
    for num_line, line in enumerate(values):
        values_num_line.append(f'{num_line+1}')
        values_text.append(line)
        values_filename.append(file.basename())
        values_file_type.append(file.extension())
        values_filepath.append(file.absolute())
        values_dir.append(file.dirname())

    df[ColumnTable.NUMLINHA.value] = values_num_line
    df[ColumnTable.TEXT.value] = values_text
    df[ColumnTable.FILENAME.value] = values_filename
    df[ColumnTable.FILETYPE.value] = values_file_type
    df[ColumnTable.FILE.value] = values_filepath
    df[ColumnTable.DIR.value] = values_dir
    return df


def create_df_from_filepdf(file: File) -> pd.DataFrame:
    items: List[pd.DataFrame] = []
    doc = DocumentPdf()
    doc.add_file_pdf(file)
    for page in doc.pages:
        text_page: str = page.to_string()
        if (text_page is not None) and (text_page != ""):
            try:
                df = create_df_from_values(file, text_page.split('\n'))
            except Exception as e:
                print(e)
            else:
                df[ColumnTable.NUMPAGE.value] = [page.page_number] * len(df)
                items.append(df)

    doc.clear()
    del doc
    return pd.concat(items) if len(items) > 0 else get_void_df()


class TableFilesText(ABCTableFiles):

    def __init__(self, pbar: ProgressBarAdapter = CreatePbar().get()):
        super().__init__(pbar)

    def add_file(self, file: File) -> None:
        self.files.append(file)

    def __get_text(self, file: File) -> List[str]:
        try:
            with open(file.absolute(), 'rt') as f:
                lines = f.readlines()
        except Exception as e:
            print(e)
            return []
        else:
            return lines

    def __get_df(self, f: File) -> pd.DataFrame:
        text_file: List[str] = self.__get_text(f)
        if len(text_file) == 0:
            return get_void_df()
        return create_df_from_values(f, text_file)

    def to_data(self) -> pd.DataFrame:
        values: List[pd.DataFrame] = []

        for f in self.files:
            df = self.__get_df(f)
            if not df.empty:
                values.append(df)

        if len(values) == 0:
            return get_void_df()
        return pd.concat(values)


class TableFilesPdf(ABCTableFiles):

    def __init__(self, pbar: ProgressBarAdapter = CreatePbar().get()):
        super().__init__(pbar)

    def add_file(self, file: File) -> None:
        self.files.append(file)

    def add_files_pdf(self, files: List[File]):
        self.files.extend(files)

    def to_data(self) -> pd.DataFrame:
        values: List[pd.DataFrame] = []
        maxnum = len(self.files)
        self.pbar.start()
        print()
        for num, file in enumerate(self.files):
            self.pbar.update(
                ((num+1)/maxnum) * 100,
                f'Gerando tabela do arquivo [{num+1} de {maxnum}]'
            )

            df = create_df_from_filepdf(file)
            if not df.empty:
                values.append(df)
        print()
        self.pbar.stop()
        if len(values) < 1:
            return get_void_df()
        return pd.concat(values)


class FileToTable(object):
    def __init__(self, table: ABCTableFiles):
        self.table: ABCTableFiles = table

    def add_file(self, file: File):
        self.table.add_file(file)

    def add_files(self, files: List[File]):
        for f in files:
            self.add_file(f)

    def to_data(self) -> pd.DataFrame:
        return self.table.to_data()

    @classmethod
    def create_doc_txt(cls) -> FileToTable:
        return cls(TableFilesText())

    @classmethod
    def create_doc_pdf(cls) -> FileToTable:
        return cls(TableFilesPdf())







