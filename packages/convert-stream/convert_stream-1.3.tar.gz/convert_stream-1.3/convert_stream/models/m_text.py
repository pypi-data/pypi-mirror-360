#!/usr/bin/env python3
#
from __future__ import annotations
from typing import List, Dict
from datetime import datetime
from enum import Enum
from pandas import DataFrame, Timestamp
import re
import os

from soup_files import File

def print_line(char:str='='):
    """
        Imprime uma linha na tela.
    """
    try:
        num_size = os.get_terminal_size().columns
    except:
        num_size = 80
    print(char * num_size)


def print_title(title:str, char:str='='):
    """
        Imprime um título na tela.
    """
    try:
        num_size = os.get_terminal_size().columns
    except:
        num_size = 80

    #print_line(char)
    print(title.center(num_size, char))
    

class LibraryDates(Enum):
    D_M_Y = '%d-%m-%Y'
    DMY = '%d/%m/%Y'
    dmy = '%d/%m/%y'
    d_m_y = '%d-%m-%y'
    YMD = '%Y/%m/%d' 
    Y_M_D = '%Y-%m-%d'  
     
        
def save_data(df:DataFrame, file:File):
    try:
        df.to_excel(file.absolute(), index=False)
    except Exception as e:
        print(e)
    else:
        print('OK')


class ConvertStringDate(object):
    def __init__(self):
        """
            Converter vários formatos de datas.
        """
        self.valid_formats = (
            '%d-%m-%Y',  # Exemplo: 11-01-2025
            '%d/%m/%y',
            '%d-%m-%y',
            '%Y/%m/%d',  # Exemplo: 2025/01/11
            '%d/%m/%Y',  # Exemplo: 11/01/2025
            '%Y-%m-%d',  # Exemplo: 2025-01-11
            '%d %B %Y',  # Exemplo: 11 Janeiro 2025
            '%b %d, %Y', # Exemplo: Jan 11, 2025
            '%A, %d %B %Y', # Exemplo: Sábado, 11 Janeiro 2025
            '%H:%M:%S',  # Exemplo: 08:35:00
            '%H:%M',     # Exemplo: 08:35
            '%I:%M %p',  # Exemplo: 08:35 AM
            '%Y-%m-%d %H:%M:%S',  # Exemplo: 2025-01-11 08:35:00
            '%Y-%m-%dT%H:%M:%S',  # Exemplo: 2025-01-11T08:35:00 (Formato ISO 8601)
            '%Y%m%dT%H%M%S',      # Exemplo: 20250111T083500 (Formato compactado) 
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",  # ISO-like
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        self.valid_timestamp = (
            '%Y-%m-%d %H:%M:%S',  # Exemplo: 2025-01-11 08:35:00
            '%Y-%m-%dT%H:%M:%S',  # Exemplo: 2025-01-11T08:35:00 (Formato ISO 8601)
            '%Y%m%dT%H%M%S',      # Exemplo: 20250111T083500 (Formato compactado) 
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",  # ISO-like
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        #
        # Dicionário de mapeamento de nomes de meses em português para inglês
        self.meses_ptbr_para_ingles = {
            'Janeiro': 'January',
            'Fevereiro': 'February',
            'Março': 'March',
            'Abril': 'April',
            'Maio': 'May',
            'Junho': 'June',
            'Julho': 'July',
            'Agosto': 'August',
            'Setembro': 'September',
            'Outubro': 'October',
            'Novembro': 'November',
            'Dezembro': 'December',
        }

        # Mapeamento dos meses em português para números
        self.meses_ptbr_para_numeros = {
            "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
            "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
            "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
        }

    def is_valid_date(self, date_str:str) -> bool:
        """
            Verificar se uma string é uma data válida
        """
        # Tentar conversão com formatos tradicionais.
        date_str = date_str.strip()
        for fmt in self.valid_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except:
                pass
        
        if ('de' in date_str) and (',' in date_str):
            # Sexta-feira, 25 de abril de 2025
            date_str = date_str.split(',')[1].strip()
            date_str = date_str.replace(' ', '-').replace('de', '').replace('--', '-').strip()
            
        if '-' in date_str:
            for _key in self.meses_ptbr_para_numeros.keys():
                if _key in date_str:
                    new = self._long_date_ptbr_format(date_str)
                    if new is not None:
                        return True
        
        if self._long_date_ptbr_format(date_str) is not None:
            return True
        if self.is_timestamp(date_str):
            return True
        if ',' in date_str:
            try:
                # Sábado, 11 Janeiro 2025
                date_str = self._long_date_ptbr_to_eng(date_str)
            except:
                pass
            else:
                return True
        return False
    
    def is_timestamp(self, d:object) -> bool:
        """
            Verifica se o objeto atual é timestamp
        """
        if isinstance(d, Timestamp):
            return True
        for current_format in self.valid_timestamp:
            try:
                datetime.strptime(d, current_format)
                return True
            except:
                pass
        return False
    
    def _long_date_ptbr_to_eng(self, data_string:str, fmt:str='%A, %d %B %Y') -> str:
        # Exemplo de data em string com o dia da semana em português => 'Sábado, 11 Janeiro 2025'

        # Remover o dia da semana da string
        new_string_date = data_string.split(", ")[1]

        # Formato da data sem o dia da semana
        current_data_fmt = '%d %B %Y'

        # Substituir o nome do mês em português pelo nome em inglês
        for pt_mes, en_mes in self.meses_ptbr_para_ingles.items():
            new_string_date = new_string_date.replace(pt_mes, en_mes)

        # Converter a string para um objeto datetime
        to_datetime = datetime.strptime(new_string_date, current_data_fmt)

        # Formatando o objeto datetime para o formato desejado "dia/mês/ANO"
        return to_datetime.strftime(fmt)
    
    def _long_date_ptbr_format(self, data_str_ptbr:str, *, fmt:LibraryDates=LibraryDates.DMY) -> str | None:
            # Divide a string e substitui o mês pelo número correspondente
            try:
                dia, mes, ano = data_str_ptbr.split("-")
                mes_num = self.meses_ptbr_para_numeros[mes.lower()]  # Converte o mês para número
                data_formatada = f"{dia}/{mes_num}/{ano}"  # Formata para o padrão dd/mm/yyyy
                # Converte para um objeto datetime
                return datetime.strptime(data_formatada, fmt.value).strftime(fmt.value) # "%d/%m/%Y" ...
            except Exception as e:
                print(e)
                return None

    def convert_date(self, date_str:str, *, fmt:LibraryDates=LibraryDates.DMY) -> str | None:
        """
            Converter uma data em string para um formato qualquer.
        """
        if not self.is_valid_date(date_str):
            return None
        
        if ('de' in date_str) and (',' in date_str):
            # Sexta-feira, 25 de abril de 2025
            date_str = date_str.split(',')[1].strip()
            date_str = date_str.replace(' ', '-').replace('de', '').replace('--', '-').strip()
            new = self._long_date_ptbr_format(date_str, fmt=fmt)
            if new is not None:
                return new
            
        if '-' in date_str:
            for _key in self.meses_ptbr_para_numeros.keys():
                if _key in date_str:
                    new = self._long_date_ptbr_format(date_str)
                    if new is not None:
                        return new
                    
        if ',' in date_str:
            date_str = self._long_date_ptbr_to_eng(date_str)
        
        for current_format in self.valid_formats:
            try:
                date_obj = datetime.strptime(date_str, current_format)
            except:
                pass
            else:
                return date_obj.strftime('{}'.format(fmt.value))
        return None  
             
    def convert_timestamp(self, ts:str, *, fmt:LibraryDates=LibraryDates.DMY) -> str | None:
        """
            Converter uma data em string para um formato qualquer.
        """
        if not self.is_timestamp(ts):
            return None
        for current_format in self.valid_timestamp:
            try:
                date_timestamp:datetime = datetime.strptime(ts, current_format)
            except:
                pass
            else:
                # Converter datetime para string no formato recebido via parâmetro.
                return date_timestamp.strftime(fmt.value)
        return None



class ConvertDate(object):
    def __init__(self):
        """
         Converter vários formatos de datas.
        """
        print(
            f'''
            [!] INFO: Em versões futuras a classe {__class__.__name__} será excluída, para formatar data Use 
            a classe ConvertStringDate()
            '''
        )
        self.convert: ConvertStringDate = ConvertStringDate()
        self.valid_formats = self.convert.valid_formats
        self.valid_timestamp = self.convert.valid_timestamp
        self.meses_para_ingles = self.convert.meses_ptbr_para_ingles
        self.meses_ptbr_para_numeros = self.convert.meses_ptbr_para_numeros

    def is_valid_date(self, d:str) -> bool:
        return self.convert.is_valid_date(d)
    
    def is_timestamp(self, d:object) -> bool:
        """
            Verifica se o objeto atual é timestamp
        """
        return self.convert.is_timestamp(d)
    
    def _long_date_ptbr_to_eng(self, data_string:str, fmt:str='%A, %d %B %Y') -> str:
        return self.convert._long_date_ptbr_to_eng(data_string, fmt)
    
    def convert_string_date_ptbr(self, data_str_ptbr:str, *, fmt:LibraryDates=LibraryDates.DMY) -> str | None:
            return self.convert.convert_date(data_str_ptbr, fmt=fmt)

    def convert_date(self, date:str, *, fmt:LibraryDates=LibraryDates.DMY) -> str | None:
        """
            Converter uma data em string para um formato qualquer.
        """
        return self.convert.convert_date(date, fmt=fmt)  
             
    def convert_timestamp(self, ts:str, *, fmt:LibraryDates=LibraryDates.DMY) -> str | None:
        """
            Converter uma data em string para um formato qualquer.
        """
        return self.convert.convert_timestamp(ts, fmt=fmt)


        
class DataString(object):
    def __init__(self, value:str):
        self.value = value
        
    def is_null(self) -> bool:
        if (self.value is None) or (self.value == ''):
            return True
        return False

    def to_utf8(self) -> DataString:
        items_for_remove = [
                        '\xa0T\x04',
                    ]
        try:
            for i in items_for_remove:
                REG = re.compile(i)
                self.value = REG.sub("_", self.value)
        except:
            return self
        else:
            self.value = self.value.encode("utf-8", errors="replace").decode("utf-8")
        return self
    
    def to_upper(self) -> DataString:
        self.value = self.value.upper()
        return self
    
    def to_list(self, separator:str=' ') -> List[str]:
        """
            Transforma uma string em uma lista de strings.
        """
        try:
            return self.value.split(separator)
        except Exception as e:
            print(e)
            return []
        
    def to_array_string(self, separator:str=' ') -> ArrayString:
        """
            Transforma uma string em uma lista de strings.
        """
        try:
            return ArrayString(self.value.split(separator))
        except Exception as e:
            print(e)
            return ArrayString([])

    def replace_all(self, char:str, new_char:str='_') -> DataString:
        """
            Usar expressão regular para substituir caracteres.
        """
        # re.sub(r'{}'.format(char), new_char, text)
        self.value = re.sub(re.escape(char), new_char, self.value)
        return self

    def replace_bad_chars(self, *, new_char='-') -> DataString:
        char_for_remove = [
                            ':', ',', ';', '$', '=', 
                            '!', '}', '{', '(', ')', 
                            '|', '\\', '‘', '*'
                            '¢', '“', '\'', '¢', '"', 
                            '#', '<', '?', '>', 
                            '»', '@', '+', '[', ']',
                            '%', '%', '~', '¥', '«',
                            '°', '¢', '”', '&'
                ]

        for char in char_for_remove:
            self.replace_all(char, new_char)
        format_chars = [
            '-_', '_-', '--', '__',
        ]
        for c in format_chars:
            self.replace_all(c)
        return self
    
    
class ArrayString(object):
    def __init__(self, values: List[str]):
        self.values = values
        self.length = len(self.values)
        
    def add(self, item:str):
        if not isinstance(item, str):
            return
        self.values.append(item)
        self.length += 1
        
    def add_all(self, items: List[str]):
        for i in items:
            self.add(i)

    def for_each(self, cmd:callable):
        for i in self.values:
            cmd(i)
            
    def get_next(self, text:str, iqual:bool=False) -> DataString:
        """
            Retorna a próxima string depois da ocorrência text.
        """
        _next_value = None
        if iqual == True:
            for num, i in enumerate(self.values):
                if text == i:
                    if num+1 < self.length:
                        _next_value = self.values[num+1]
                        break
        else:
            for num, i in enumerate(self.values):
                if text in i:
                    if num+1 < self.length:
                        _next_value = self.values[num+1]
                        break
        if _next_value is None:
            return DataString('')
        return DataString(_next_value)
    
    def get_back(self, text:str, iqual:bool=False) -> str:
        new:List[str] = []
        if iqual == True:
            pass
        else:
            for item in self.values:
                if text in item:
                    break
                new.append(item)
        return ', '.join(new)
    
    def get_next_all(self, text:str, iqual:bool=False) -> ArrayString:
        """
            Retorna uma lista após a ocorrência text.
        """
        if iqual == True:
            for num, i in enumerate(self.values):
                if text == i:
                    if num+1 < self.length:
                        return ArrayString(self.values[num+1:])
        else:
            for num, i in enumerate(self.values):
                if text in i:
                    if num+1 < self.length:
                        return ArrayString(self.values[num+1:])
        return ArrayString([])
    
    def get_back_all(self, text) -> ArrayString:
        list_text:List[str] = []
        for item in self.values:
            if text in item:
                break
            list_text.append(item)
        return ArrayString(list_text)
                    
    def get_contains(self, text:str) -> ArrayString:
        """
            Retorna uma lista de ocorrências que contém text.
        """
        items = []
        for i in self.values:
            if text in i:
                items.append(i)
        return ArrayString(items)
    
    def contains(self, text:str) -> bool:
        _contains = False
        for item in self.values:
            if text in item:
                _contains = True
                break
        return _contains

    def to_string(self, separator:str=' ') -> str:
        try:
            return separator.join(self.values)
        except:
            return None
    
            