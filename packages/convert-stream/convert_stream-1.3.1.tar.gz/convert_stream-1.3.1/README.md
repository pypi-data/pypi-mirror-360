# Configuração instalação:
pip3 install -r requirements.txt


# Uso dividir páginas de um arquivo PDF:
    >>> from file import File, Directory
    >>> from pdflib import PdfStream
    # instâncie o caminho do arquivo PDF e o diretório para exportar os dados.
    f = File('path/to/file.pdf')
    d = Directory('path/to/save')

    pdf_stream = PdfStream()
    pdf_stream.add_file_pdf(f)
    pdf_stream.to_files_pdf(d) # isso irá converter cada página em um arquivo PDF

# Uso para unir vários arquivos PDF.
    >>> from file import File, Directory
    >>> from pdflib import PdfStream
    # instâncie o caminho dos arquivos PDF que deseja unir.
    f = File('path/to/file.pdf')
    f2 = File('path/to/file2.pdf)
    ...
    ... # Adicione quantos arquivos desejar.
    
    pdf_stream = PdfStream()
    pdf_stream.add_file_pdf(f)
    pdf_stream.add_file_pdf(f2)
    pdf_stream.to_file_pdf(File('path/to/new_file.pdf'))
