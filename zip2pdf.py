#!/usr/bin/env python3.7
"""
MIT License

Copyright (c) 2021 agustinuslaw

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import io
import os
import pathlib
import traceback
from typing import List
import PIL
import zipfile
from pathlib import Path

import img2pdf
from reportlab.lib import pagesizes
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import argparse
import sys


def change_file_name_ext(original_file_name: str, new_ext: str) -> str:
    """
    Converts the extension of the filename.
    :param original_file_name: whose base will be used e.g. 'foo.zip'
    :param new_ext: to append to the base name e.g. 'pdf'
    :return: modified file name e.g. 'foo.pdf'
    """
    base_name: str = Path(original_file_name).stem
    if new_ext.startswith("."):
        modified_file_name: str = base_name + new_ext
    else:
        modified_file_name: str = base_name + "." + new_ext
    return modified_file_name


def convert_reportlab(zip_file_name: str, out_folder: Path) -> None:
    """
    Converts the entire Zip images as a single PDF. Individual IOError from each image is ignored.
    Uses ReportLab PDF Canvas.
    :param zip_file_name: zip file whose image content will be converted
    :param out_folder: Path of output PDF file
    :return: None
    """
    print(f"Process zip: '{zip_file_name}' using reportlab")
    pdf_file_name: str = change_file_name_ext(zip_file_name, "pdf")
    pdf_file_path: str = str(out_folder.joinpath(pdf_file_name).resolve())

    with zipfile.ZipFile(zip_file_name, "r") as zip_input:
        rl_canvas = canvas.Canvas(pdf_file_path, pagesize=pagesizes.A4)
        rl_canvas.setPageCompression(1)

        for image_name in zip_input.namelist():
            print(f"Process image: '{image_name}' for zip '{zip_file_name}'")

            # the file bytes
            file_bytes: bytes = zip_input.read(image_name)
            buffer: io.BytesIO = io.BytesIO(file_bytes)

            # assume the file is actually an image of some sort e.g. PNG
            try:
                pil_image: PIL.Image = PIL.Image.open(buffer)
            except IOError as iox:
                print(f"IOError! Image '{image_name}' for zip '{zip_file_name}' failed to convert to PIL Image. File is skipped.")
                tb = traceback.print_exc()
                continue

            # stretch image to A4 size, while preserving aspect
            rl_image_reader = ImageReader(pil_image)
            rl_canvas.drawImage(image=rl_image_reader, x=0, y=0, width=pagesizes.A4[0], height=pagesizes.A4[1], preserveAspectRatio=True)

            # page in canvas is finished
            rl_canvas.showPage()

        # create pdf file
        print(f"Try to save as '{pdf_file_path}'")
        rl_canvas.save()


def convert_img2pdf(zip_file_name: str, out_folder: Path) -> None:
    """
    Converts the entire Zip images as a single PDF. Individual IOError from each image is ignored.
    Uses IMG2PDF lossless algorithm, but can't handle certain images, e.g. ICC + P and RGBA
    :param zip_file_name: zip file whose image content will be converted
    :param out_folder: Path of output PDF file
    :return: None
    """
    print(f"Process zip: '{zip_file_name}' in bulk using image2pdf")
    pdf_file_name: str = change_file_name_ext(zip_file_name, "pdf")
    pdf_file_path: str = str(out_folder.joinpath(pdf_file_name).resolve())

    with zipfile.ZipFile(zip_file_name, "r") as zip_input, open(pdf_file_path, "wb") as pdf_output:
        image_buffers = [io.BytesIO(zip_input.read(image_name)) for image_name in zip_input.namelist()]
        img2pdf.convert(image_buffers, outputstream=pdf_output)
        print(f"Saved as '{pdf_file_name}'")


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(prog="zip2pdf")

    # Set up the arguments available
    parser.add_argument("-f", "--files", nargs=argparse.ONE_OR_MORE, required=False, help="one or more zip files to convert", type=str)
    parser.add_argument("-d", "--directories", nargs=argparse.ONE_OR_MORE, required=False, help="onr or more directories to look for *.zip files. May be recursive with -r option", type=str)
    parser.add_argument("-r", "--recursive", required=False, help="recursively look under directories specified by -d", action='store_const', const=True)
    parser.add_argument("-a", "--algorithm", nargs=None, choices=['img2pdf', 'reportlab'], required=False, help="determine whether to use 'reportlab' or 'img2pdf' algorithm.", type=str)
    parser.add_argument("-o", "--output-path", nargs=None, required=False, help="set the output path of the PDF. default folder is chdir", type=str)
    parser.add_argument("-v", "--version", action='version', version='%(prog)s 1.0', help="show this application version")

    # Parse CLI arguments
    args: argparse.Namespace = parser.parse_args(argv[1:])

    # Collect all zip files to process
    zip_file_names: List[str] = []

    # Add zips from directories arg to collection
    if args.directories is not None:
        for directory in args.directories:
            if args.recursive is True:
                glob_filter = '**/*.zip'
            else:
                glob_filter = '*.zip'

            # Get the zips under specified directory
            directory_zip = list(pathlib.Path(directory).glob(glob_filter))

            # Collect those zips
            zip_file_names += directory_zip

    # Add zips from files arg to collection
    if args.files is not None:
        zip_file_names += args.files

    # Determine algorithm, args has been validated by arg parser
    if args.algorithm == 'reportlab':
        convert = convert_reportlab
    elif args.algorithm == 'img2pdf':
        convert = convert_img2pdf
    else:
        # currently reportlab is the default, may be changed
        convert = convert_reportlab

    # Get the output folder
    if args.output_path is None:
        output_folder: Path = Path(os.getcwd())
    else:
        output_folder: Path = Path(args.output_path)

    # Convert
    for name in zip_file_names:
        try:
            convert(name, output_folder)
        except Exception as ex:
            print(f"Error! Unable to process zip '{name}'.")
            tb = traceback.print_exc()
            break


if __name__ == "__main__":
    # Ensure Python 3+
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or a more recent version is required.")

    main(sys.argv)
