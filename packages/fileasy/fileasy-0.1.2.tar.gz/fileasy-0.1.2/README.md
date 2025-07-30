# 📄 Fileasy

Fileasy is a simple, lightweight command-line interface (CLI) tool to convert between image files and PDFs, and to merge multiple PDF files. It supports common image formats like JPG, PNG, BMP, TIFF, and more.

## ✨ Features

✅ Convert images to PDF

✅ Convert PDFs to images

✅ Merge multiple PDF files

✅ Combine image conversion and merging in one step

# 📦 Installation

You can install Fileasy directly from PyPI:

```
pip install fileasy
```

# 🚀 Usage

```
fileasy [-h] [-c] [-m] [-f FILES [FILES ...]] [-o OUTPUT]

Fileasy is a simple CLI tool to convert images to PDFs and vice versa, and merge PDFs'

options :	
-h, --help            Show this help message and exit
-c, --convert         Convert the input file
-m, --merge           Merge the input files
-f, --files FILES [FILES ...] List of files to merge
-o, --output OUTPUT   Output file for conversion
```

# 🧪 Examples
Convert an image to PDF

```
fileasy -c -f image.jpg -o output.pdf
```

Convert a PDF to images

```
fileasy -c -f document.pdf -o image_output.jpg
```

Merge multiple PDF files

```
fileasy -m -f file1.pdf file2.pdf -o merged.pdf
```

Convert multiple images and merge into one PDF

```
fileasy -c -m -f img1.jpg img2.jpg -o merged.pdf
```

# 🔧 File Format Support

| Type        |                              Formats                              |
| :---------- | :---------------------------------------------------------------: |
| Image Input | `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tif`, `.tiff`, `.gif`, `.webp` |
| PDF Input   | `.pdf` |

# 📄 License

This project is licensed under the Apache License.