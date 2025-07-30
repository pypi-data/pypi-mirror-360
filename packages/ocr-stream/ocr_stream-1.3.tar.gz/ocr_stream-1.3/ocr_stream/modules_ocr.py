#!/usr/bin/env python3
from __future__ import annotations
from types import ModuleType
from typing import List, Dict
from pathlib import Path
from shutil import which
import re
import os
from pandas import DataFrame
from pytesseract import pytesseract, Output

from ocr_stream.models import (
    ABCModuleOcr, ABCTextRecognized, LibraryOCR,
)

from ocr_stream.utils import (
    PageDocumentPdf, DocumentPdf, LibraryImage, LibraryPDF,
    ImageObject, ArrayString, DataString, File, Directory,
    FileToTable, ColumnTable, KERNEL_TYPE,
)

try:
    import pyocr
except Exception as e:
    print(e)

class TextRecognizedToi(object):
    """
        Extração/Filtro de texto em documentos do tipo carta TOI.
    """

    def __init__(self, value: str = None, *, separator: str = '\n', column_text='TEXT', file: File):
        # Todas as linhas reconhecidas em imagem/página PDF.
        if not isinstance(value, str):
            raise ValueError(f'{__class__.__name__}Use: str, não {type(value)}')
        self.text_document: str = DataString(value).to_upper().value if value is not None else None
        self.separator: str = separator
        self.file: File = file
        self.column_text: str = column_text

        self.pattern_line_uc_toi = r'UC:\s*\d+\s*TOI:\s*\d+'
        self.pattern_uc = r'\b(?:UC:?|UC):?\s*(\d+)'
        self.pattern_toi = r'\b(?:TOI?|TO):?\s*(\d+)'
        self.pattern_localidade = r'LOCALIDADE:\s*(.*)'

        self.words_toi = (
            'TO]!', 'TO]', 'TOl', 'TOI', 'TOI:'
        )

        self.words_uc = (
            'UE', 'UE:' 'UC', 'UC:', 'JC;'
        )

    def __replace_chars(self, text, char, new_char) -> str:
        return re.sub(r'{}'.format(char), new_char, text)

    def __get_match_groups(self, pattern, text: str) -> object | None:
        i = re.search(pattern, text)
        if i is None:
            return None
        return i.groups()

    def __get_match_group(self, pattern, text: str) -> object | None:
        i = re.search(pattern, text)
        if i is None:
            return None
        return i.group()

    def is_null(self) -> bool:
        if self.text_document is None:
            return True
        if self.text_document == '':
            return True
        return False

    def to_string(self) -> str | None:
        return DataString(self.text_document).to_upper().value if not self.is_null() else None

    def to_list(self) -> List[str]:
        return self.text_document.split(self.separator)

    def to_array_string(self) -> ArrayString:
        values: List[str] = self.to_list()

    def to_upper(self) -> TextRecognizedToi:
        self.text_document = self.text_document.upper()
        return self

    def to_dataframe(self) -> DataFrame:
        uc = self.uc()
        toi = self.toi()
        if uc is None:
            uc = 'nan'
        else:
            uc = DataString(uc).replace_bad_chars().replace_all('- ', ' ').replace_all('_', ' ').value.strip()
        #
        if toi is None:
            toi = 'nan'
        else:
            toi = DataString(toi).replace_bad_chars()
            toi = toi.replace_all('- ', '-').replace_all('_', ' ').replace_all('-', ' ').replace_all('TOI',
                                                                                                     '').value.strip()

        df = DataFrame()
        df[self.column_text] = self.to_list()
        num = len(df)
        df['UC'] = [uc] * num
        df['TOI'] = [toi] * num
        df['LOCALIDADE'] = [self.localidade()] * num
        df['ARQUIVO'] = [self.file.absolute()] * num
        df['MD5'] = [self.file.md5()] * num
        return df

    def remove_bad_chars(self) -> TextRecognizedToi:
        values = []
        for item in self.to_list():
            values.append(
                DataString(item).replace_bad_chars(new_char='_').replace_all('/', '-').value
            )
        self.listText = values
        return self

    def uc(self) -> str:
        """
            Extrair o número da UC em forma de string, se a operação falhar, será retornado (nan)
        """
        line_uc_toi = self.line_uc_and_toi()
        uc_value: str = None
        if line_uc_toi is not None:
            uc_value = self.__get_match_group(self.pattern_uc, line_uc_toi)
        if uc_value is not None:
            return uc_value.replace('UC', '')

        arr = ArrayString(self.text_document.split(' '))
        for w in self.words_uc:
            out = arr.get_next(w).value
            try:
                int(out)
            except:
                pass
            else:
                return out
        return None

    def toi(self) -> str:
        line_uc_toi = self.line_uc_and_toi()
        toi_value: str = None
        if line_uc_toi is not None:
            toi_value = self.__get_match_group(self.pattern_toi, line_uc_toi)
        if toi_value is not None:
            return toi_value.replace('TOI', '')
        arr = ArrayString(self.text_document.split(' '))

        for w in self.words_toi:
            out = arr.get_next(w).value
            try:
                int(out)
            except:
                pass
            else:
                return out
        return None

    def roteiro(self) -> str:
        self.remove_bad_chars()
        pass

    def localidade(self) -> str:
        lines = self.to_list()
        loc = 'nan'
        for line in lines:
            out = re.search(self.pattern_localidade, line)
            if out:
                loc = out.group(1)
                break
        loc = DataString(loc).replace_all(' ').value
        # Remover "_" do final
        return re.sub(r"_$", "", loc)

    def line_postagem(self) -> str:
        pass

    def line_uc_and_toi(self) -> DataString | None:
        line_toi = None
        lines = self.to_list()
        for item in lines:
            out = self.__get_match_group(self.pattern_line_uc_toi, item)
            if out is None:
                continue
            line_toi = out
            break
        return line_toi

    def line_roteiro(self) -> DataString:
        return DataString(None)

    #======================================================================#


# Texto reconhecido de uma imagem.
#======================================================================#


class TextRecognized(ABCTextRecognized):
    """
        Recebe os bytes de uma página PDF reconhecida de imagem
    e exporta para vários tipos de dados.
    -> DataFrame()
    -> str
    -> PageDocumentPdf()
    """

    def __init__(self, bytes_recognized: bytes):
        super().__init__(bytes_recognized)

        self.list_bad_char: List[str] = [
            ':', ',', ';', '$', '=',
            '!', '}', '{', '(', ')',
            '|', '\\', '‘', '*'
                            '¢', '“', '\'', '¢', '"',
            '#', '.', '<', '?', '>',
            '»', '@', '+', '[', ']',
            '%', '~', '¥', '♀',
        ]

    def to_string(self) -> str | None:
        return self.to_page_pdf().to_string()

    def to_page_pdf(self) -> PageDocumentPdf:
        _page = PageDocumentPdf.create_from_page_bytes(
            self.bytes_recognized,
            library=LibraryPDF.FITZ
        )
        return _page

    def to_document(self) -> DocumentPdf:
        return DocumentPdf(pages=[self.to_page_pdf()])

    def to_dict(
                self,
                separator='\n',
                column_text: ColumnTable.TEXT = ColumnTable.TEXT
            ) -> Dict[str, List[str]]:
        #
        image_dict: Dict[str, List[str]] = {
            column_text.value: [],
            ColumnTable.NUMLINHA.value: [],
        }
        image_text: str = self.to_string()
        if (image_text is None) or (image_text == ''):
            return {
                column_text.value: ['nan'],
                ColumnTable.NUMLINHA.value: ['nan'],
            }

        image_lines: List[str] = image_text.split(separator)
        for num, line in enumerate(image_lines):
            image_dict[column_text.value].append(line)
            image_dict[ColumnTable.NUMLINHA.value].append(f'{num + 1}')
        return image_dict

    def to_dataframe(self, separator='\n', column_text: ColumnTable.TEXT = ColumnTable.TEXT) -> DataFrame:
        return DataFrame(self.to_dict(separator, column_text))


class BinaryTesseract(object):
    """
        Fornece o caminho absoluto do tesseract instalado no sistema, se
    disponível. Você pode usar um binário alternativo, basta informar
    o caminho do binário desejado no construtor.
    """
    def __init__(
                    self,
                    path: File = None, *,
                    lang: str = None,
                    tess_data_dir: Directory = None
            ):
        #
        self.tess_data_dir: Directory = tess_data_dir
        self.lang: str = lang
        self.path_tesseract: File = path
        if self.path_tesseract is None:
            if KERNEL_TYPE == 'Windows':
                name = 'tesseract.exe'
            else:
                name = 'tesseract'
            output = which(name)
            if output is not None:
                if os.path.isfile(output):
                    print(f'[binary]: {output}')
                    self.path_tesseract = File(output)

    def exists(self) -> bool:
        if self.path_tesseract is None:
            return False
        return True


#======================================================================#
# Modulo OCR pytesseract
#======================================================================#


class IPytesseract(ABCModuleOcr):

    def __init__(
                    self, *,
                    cmd_executable: File,
                    lang: str = None,
                    tess_data_dir: Directory = None,
            ):
        #
        super().__init__(cmd_executable=cmd_executable, lang=lang, tess_data_dir=tess_data_dir)
        self.current_library: LibraryOCR = LibraryOCR.PYTESSERACT
        self._pyTesseract: pytesseract = pytesseract
        self._pyTesseract.tesseract_cmd = self.cmd_executable.absolute()

    def __get_tess_dir_config(self) -> str | None:
        """
        https://github.com/h/pytesseract
        
        Example config: r'--tessdata-dir "C:\Program Files (x86)\Tesseract-OCR\tessdata"'
        tessdata_dir_config = r'--tessdata-dir <replace_with_your_tessdata_dir_path>'
        It's important to add double quotes around the dir path.
        """
        #
        # Caminho para os dados de idioma, por, eng etc...
        # os.environ["TESSDATA_PREFIX"] = self.tess_data_dir.absolute()
        if self.tess_data_dir is None:
            return ''
        if not self.tess_data_dir.path.exists():
            return ''
        return r'--tessdata-dir "{}"'.format(self.tess_data_dir.absolute())

    def imag_to_string(self, img) -> str:
        if img.current_library == LibraryImage.OPENCV:
            text_img: str = self._pyTesseract.image_to_string(
                img.to_image_opencv(),
                lang=self.lang,
                config=self.__get_tess_dir_config()
            )
        else:
            text_img: str = self._pyTesseract.image_to_string(
                img.to_image_pil(),
                lang=self.lang,
                config=self.__get_tess_dir_config()
            )
        return text_img

    def image_recognize(self, img) -> TextRecognized:
        """

        @rtype: TextRecognized
        """
        if img.current_library == LibraryImage.OPENCV:
            pdf_bytes: bytes = self._pyTesseract.image_to_pdf_or_hocr(
                img.to_image_opencv(),
                lang=self.lang,
                config=self.__get_tess_dir_config()
            )
        else:
            pdf_bytes: bytes = self._pyTesseract.image_to_pdf_or_hocr(
                img.to_image_pil(),
                lang=self.lang,
                config=self.__get_tess_dir_config()
            )
        return TextRecognized(pdf_bytes)

    def image_content_data(self, img: ImageObject) -> DataFrame:
        """
            Retorna um dataframe gerado por pytesseract

        @rtype: DataFrame
        """
        if img.current_library == LibraryImage.OPENCV:
            text_data: DataFrame = self._pyTesseract.image_to_data(
                img.to_image_opencv(),
                lang=self.lang,
                config=self.__get_tess_dir_config(),
                output_type=Output.DATAFRAME,
            )
        else:
            text_data: DataFrame = self._pyTesseract.image_to_data(
                img.to_image_pil(),
                lang=self.lang,
                config=self.__get_tess_dir_config(),
                output_type=Output.DATAFRAME,
            )
        return text_data


#======================================================================#
# Modulo OCR pyocr
#======================================================================#


class IPyOcr(ABCModuleOcr):
    def __init__(self, *, cmd_executable, lang=None, tess_data_dir=None):
        super().__init__(cmd_executable=cmd_executable, lang=lang, tess_data_dir=tess_data_dir)
        self.current_library: LibraryOCR = LibraryOCR.PYOCR
        self.cmd_executable: File = cmd_executable
        self.tess_data_dir: Directory = tess_data_dir
        try:
            import pyocr
            import pyocr.tesseract
        except Exception as e:
            raise e

        pyocr_modules: List[ModuleType] = pyocr.get_available_tools()
        if len(pyocr_modules) == 0:
            raise ValueError(f"{__class__.__name__} No OCR tool found")
        # The tools are returned in the recommended order of usage
        self._pyOcr: pyocr.tesseract = pyocr_modules[0]
        langs: List[str] = self._pyOcr.get_available_languages()
        if lang in lang:
            self.lang = lang
        else:
            self.lang = langs[0]

        # Ex: Will use tool 'libtesseract'
        print(f"Will use tool {self._pyOcr.get_name()}")

    def imag_to_string(self, img) -> str:
        return self._pyOcr.image_to_string(
            img.to_image_pil(),
            lang=self.lang,
            builder=pyocr.builders.TextBuilder()
        )

    def image_recognize(self, img) -> TextRecognized:
        raise NotImplementedError(f'{__class__.__name__} método não implementado')

    def image_content_data(self, img) -> DataFrame:
        raise NotImplementedError(f'{__class__.__name__} método não implementado')


class ModuleOcr(object):
    def __init__(self, module_ocr: IPytesseract | IPyOcr):
        self.module_ocr: IPytesseract | IPyOcr = module_ocr

    def image_content_data(self, img: ImageObject) -> DataFrame:
        return self.module_ocr.image_content_data(img)

    def image_recognize(self, img: ImageObject) -> TextRecognized:
        return self.module_ocr.image_recognize(img)

    def imag_to_string(self, img) -> str:
        return self.module_ocr.imag_to_string(img)

    @classmethod
    def create(
            cls,
            library_ocr=LibraryOCR.PYTESSERACT,
            *,
            binary_tess: BinaryTesseract = BinaryTesseract(),
    ) -> ModuleOcr:
        #
        if library_ocr == LibraryOCR.PYTESSERACT:
            _module_ocr = IPytesseract(
                    cmd_executable=binary_tess.path_tesseract,
                    lang=binary_tess.lang,
                    tess_data_dir=binary_tess.tess_data_dir,
            )
        elif library_ocr == LibraryOCR.PYOCR:
            _module_ocr = IPyOcr(
                cmd_executable=binary_tess.path_tesseract,
                lang=binary_tess.lang,
                tess_data_dir=binary_tess.tess_data_dir,
            )
        else:
            raise NotImplementedError(f'{__class__.__name__}\nLibraryOcr não implementada: {library_ocr}')
        return cls(_module_ocr)
