# ocrlib

# Uso simples


from ocr_stream import File, TextRecognized, RecognizeImage, RecognizePdf

# passo 1:
#   instânciar o objeto para reconhecer texto, utilizando o caminho do tesseract

tess: File = File('/usr/bin/tesseract') # Substitua pelo tesseract do seu sistema
ocr = RecognizeImage.create(path_tesseract=tess)

# passo 2:
#   instânciar um arquivo de imagem para extrair o texto.
image: File = File('path/to/file.png')

# passo 3:
#   extrair o texto
text: str = ocr.image_to_string(image)
print(text)

# passo 4 opcional:
#   você pode salvar um arquivo PDF com o texto extraido
output_file: File = File('path/to/save.pdf')
recognized: TextRecognized = ocr.image_recognize(image)
recognized.to_document().to_file_pdf(output_file)

# passo 5 opcional:
#   você pode salvar uma planilha com o texto da imagem
output_excel: File = File('path/to/file.xlsx')
recognized: TextRecognized = ocr.image_recognize(image)
recognized.to_document().to_excel(output_excel)