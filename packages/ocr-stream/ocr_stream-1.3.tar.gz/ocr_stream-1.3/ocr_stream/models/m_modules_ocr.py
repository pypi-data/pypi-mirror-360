#!/usr/bin/env python3
#
from __future__ import annotations
from typing import Dict, List
from abc import ABC, abstractmethod
from enum import Enum
from pandas import DataFrame
from soup_files import File, Directory
from convert_stream import ImageObject, DocumentPdf, PageDocumentPdf, LibraryImage


class LibraryOCR(Enum):
    PYTESSERACT = 'pytesseract'
    PYOCR = 'pyocr'


class ABCTextRecognized(ABC):
    def __init__(self, bytes_recognized: bytes):
        super().__init__()
        self.bytes_recognized: bytes = bytes_recognized

    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def to_page_pdf(self) -> PageDocumentPdf:
        pass

    @abstractmethod
    def to_document(self) -> DocumentPdf:
        pass

    @abstractmethod
    def to_dataframe(self, separator: str = '\n', column_text: str = 'TEXT') -> DataFrame:
        pass

    @abstractmethod
    def to_dict(self, separator: str = '\n', column_text: str = 'TEXT') -> Dict[str, List[str]]:
        pass


#======================================================================#
# Abstração para o módulo que extrai o texto das imagens (OCR)
# pode ser implementado com pytesseract ou outros.
#======================================================================#


class ABCModuleOcr(ABC):

    def __init__(self, *, cmd_executable: File, lang: str = None, tess_data_dir: Directory = None):
        self.cmd_executable: File = cmd_executable
        self.lang: str = lang
        self.tess_data_dir: Directory = tess_data_dir
        self.current_library_ocr: LibraryOCR = None

    @abstractmethod
    def image_recognize(self, img: ImageObject) -> ABCTextRecognized:
        pass

    @abstractmethod
    def image_content_data(self, img: ImageObject) -> DataFrame:
        pass

    @abstractmethod
    def imag_to_string(self, img: ImageObject) -> str:
        pass

