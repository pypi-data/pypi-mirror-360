#!/usr/bin/env python3
from __future__ import annotations
from typing import List
from ocr_stream.utils import (
    File, Directory, ImageObject,
    DataFrame, PageDocumentPdf,
    DocumentPdf, PdfStream, LibraryPDF,
)
from ocr_stream.models import LibraryOCR
from ocr_stream.modules_ocr import ModuleOcr, TextRecognized, BinaryTesseract
from convert_stream import LibImageToPDF, ConvertPdfToImage, CreatePbar
from soup_files import ProgressBarAdapter


class RecognizeImage(object):
    """
        Reconhecer textos em imagens com pytesseract|pyocr usando o tesseract
    """

    def __init__(self, module_ocr):
        super().__init__()
        self.module_ocr: ModuleOcr = module_ocr

    def image_content_data(self, img: ImageObject | File) -> DataFrame:
        """
        Retorna uma tabela estruturada com os dados reconhecidos da imagem.

        Este método extrai as informações contidas em uma imagem e as organiza em
        um DataFrame com colunas como o texto detectado, coordenadas da caixa delimitadora,
        nível do OCR e confiabilidade, entre outras.

        Parâmetros:
        img (ImageObject | File): A imagem a ser processada, podendo ser um objeto
        `ImageObject` ou um arquivo `File`.

        Retorna:
        DataFrame: Uma tabela contendo os dados reconhecidos na imagem.

        Lança:
        ValueError: Se o tipo do parâmetro `img` não for `ImageObject` ou `File`.

        @param img: Imagem a ser processada, podendo ser uma instância de `ImageObject`
            ou um arquivo `File`.
        @type img: ImageObject | File

        @rtype: pandas.DataFrame
        @return: Um DataFrame com os dados reconhecidos na imagem.

        @raise ValueError: Caso o tipo de `img` não seja `ImageObject` nem `File`.
        """
        if isinstance(img, File):
            return self.module_ocr.image_content_data(ImageObject.create_from_file(img))
        elif isinstance(img, ImageObject):
            return self.module_ocr.image_content_data(img)
        else:
            raise ValueError(f'{__class__.__name__}\nUse: ImageObject() ou File(), não {type(img)}')

    def image_recognize(self, img: ImageObject | File) -> TextRecognized:
        if isinstance(img, File):
            return self.module_ocr.image_recognize(ImageObject.create_from_file(img))
        elif isinstance(img, ImageObject):
            return self.module_ocr.image_recognize(img)
        else:
            raise ValueError(f'{__class__.__name__}\nUse: ImageObject() ou File(), não {type(img)}')

    def image_to_string(self, img: ImageObject | File) -> str:
        if isinstance(img, File):
            return self.module_ocr.imag_to_string(ImageObject.create_from_file(img))
        elif isinstance(img, ImageObject):
            return self.module_ocr.imag_to_string(img)
        else:
            raise ValueError(f'{__class__.__name__}\nUse: ImageObject() ou File(), não {type(img)}')

    @classmethod
    def create(
            cls,
            library_ocr: LibraryOCR = LibraryOCR.PYTESSERACT,
            *,
            binary_tess: BinaryTesseract = BinaryTesseract(),
    ) -> RecognizeImage:
        #
        module_ocr = ModuleOcr.create(library_ocr, binary_tess=binary_tess)
        return cls(module_ocr)


class RecognizePdf(object):
    def __init__(
                self,
                recognize_image: RecognizeImage, *,
                pbar: ProgressBarAdapter = CreatePbar().get()
            ):
        self.recognize_image: RecognizeImage = recognize_image
        self.pdf_to_image: ConvertPdfToImage = ConvertPdfToImage.create()
        self.pbar: ProgressBarAdapter = pbar

    def recognize_page_pdf(self, page: PageDocumentPdf) -> PageDocumentPdf:
        """
            Converte a página em Imagem, reconhece o texto com OCR e
        retorna uma nova página com o texto reconhecido.
        """
        img: ImageObject = self.pdf_to_image.from_page_pdf(page)
        text_recognized: TextRecognized = self.recognize_image.image_recognize(img)
        return text_recognized.to_page_pdf()

    def recognize_document(self, doc: DocumentPdf) -> DocumentPdf:
        new_pages: List[PageDocumentPdf] = []

        for n, page in enumerate(doc.get_pages()):
            self.pbar.update(
                ((n+1)/doc.get_num_pages()) * 100,
                f'Reconhecendo página PDF [{n+1} de {doc.get_num_pages()}]',
            )
            recognized_page: PageDocumentPdf = self.recognize_page_pdf(page)
            new_pages.append(recognized_page)
        return DocumentPdf(pages=new_pages)

    @classmethod
    def create(
            cls,
            library_ocr=LibraryOCR.PYTESSERACT,
            *,
            binary_tess: BinaryTesseract = BinaryTesseract(),
            pbar: ProgressBarAdapter = CreatePbar().get(),
    ) -> RecognizePdf:
        #
        recognize_image = RecognizeImage.create(library_ocr, binary_tess=binary_tess)
        return cls(recognize_image, pbar=pbar)
