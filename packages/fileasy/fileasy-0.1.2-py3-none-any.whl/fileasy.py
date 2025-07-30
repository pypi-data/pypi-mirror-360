import sys
import argparse
from PIL import Image
from pathlib import Path
from PyPDF2 import PdfMerger 
import os
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

class FileEasy:

    def setup(self):
        self.parser.add_argument('-c', '--convert', action='store_true', help='Convert the input file')
        self.parser.add_argument('-m', '--merge', action='store_true', help='Merge the input files, can be combined with Convert command to merge resulting PDFs')
        self.parser.add_argument('-f', '--files', help='List of files to merge', nargs='+')
        self.parser.add_argument('-o', '--output', type=str, help='Output file for conversion', required=False)



        self.args = self.parser.parse_args()
        print(f'Args: {self.args}')

        if self.args.convert and self.args.merge:

            print('Convert & Merge')
            pdfs = self.images_to_pdf(self.args.files)
            self.merge_pdfs(pdfs, self.args.output)
            for pdf in pdfs:
                if os.path.exists(pdf):
                    os.remove(pdf)

        elif self.args.convert:
            
            print('Convert')
            if len(self.args.files) == 1:
                self.convert(self.args.files, self.args.output)
            else:
                self.images_to_pdf(self.args.files)

        elif self.args.merge:

            print('Merge')
            self.merge_pdfs(self.args.files, self.args.output)

    def merge_pdfs(self, files, output= 'result.pdf'):
        merger = PdfMerger() 
        for file in files:
            merger.append(file)
        merger.write(output)
        merger.close()
    
    def convert(self, input_file, output_file):
        
        extension = os.path.splitext(input_file[0])[1]

        match extension:
            case '.pdf':
                print("pdf to image")
                images = convert_from_path(input_file[0])
                for image in images:
                    image.save(output_file)

            case '.jpg' | '.png' | '.jpeg' | '.bmp' | '.tif' | '.tiff' | '.gif' | '.webp':
                print("image to pdf")
                img = Image.open(input_file[0])
                img.convert("RGB").save(output_file)

            case _:
                print("Unknown format")

    def images_to_pdf(self, images, output= None):
        output_files = []
        for image in images:
            img = Image.open(image)
            path = Path(image)

            output_file = output if output else f"{os.path.splitext(path)[0]}.pdf"

            img.convert("RGB").save(output_file)

            output_files.append(output_file)
        return output_files

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='fileasy',
            description='Fileasy is a simple CLI tool to convert images to PDFs and vice versa, and merge PDFs'
        )

        self.setup()

def main():
    FileEasy()

if __name__ == "__main__":
    main()
