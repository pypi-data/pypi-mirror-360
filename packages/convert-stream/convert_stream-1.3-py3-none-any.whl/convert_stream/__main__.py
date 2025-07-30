#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Configuração instalação:
 $ pip3 install -r requirements.txt
 
 
------------------[versão 1.1]------------------
+ Incluir funcionalidade para adicionar imagens ao PdfStream()
+ Incluir os métodos __eq__() e __hash__() em PageDocumentPdf()
+ Incluir o método set_rotation() em ImageObject()
 
"""
import os
import sys

this_file = os.path.abspath(os.path.relpath(__file__))
dir_of_project = os.path.dirname(this_file)
sys.path.insert(0, dir_of_project)


from convert_stream import (
    version, __module_name__, __modify_date__, print_title
)


def test():
    pass


def main():
    print_title(f'{__module_name__} versão {version} - {__modify_date__}', char='-')
    test()


if __name__ == '__main__':
    main()
