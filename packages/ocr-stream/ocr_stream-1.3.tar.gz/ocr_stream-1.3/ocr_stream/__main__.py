#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------
    Configuração instalação:
------------------------------------------------------------
 $ pip3 install -r requirements.txt
 
------------------------------------------------------------
    Referências:
------------------------------------------------------------

https://gist.github.com/endolith/334196bac1cac45a4893

Tesseract OCR
https://github.com/tesseract-ocr/tesseract

pytesseract
https://github.com/h/pytesseract

pyocr
https://gitlab.gnome.org/World/OpenPaperwork/pyocr
"""

import sys, os
this_file = os.path.abspath(os.path.relpath(__file__))
dir_of_project = os.path.dirname(this_file)
sys.path.insert(0, dir_of_project)

from convert_stream import print_title
from ocr_stream import __version__, __modify_data__


def test():
    # /usr/bin/tesseract
    # /usr/share/tesseract-ocr/5/tessdata
    pass
    
    
def main():
    print_title(f' ocrlib Versão: {__version__} | Atualização: {__modify_data__} ')
    test()


if __name__ == '__main__':
    main()