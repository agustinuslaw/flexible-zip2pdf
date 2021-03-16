# flexible-zip2pdf
Flexible zip2pdf that can use img2pdf lossless algorithm which may be picky about certain types of images, or the more liberal reportlab algorithm which simply embeds the image in the PDF.  Note that currently for 'reportlab' algorithm the size is fixed to A4, due to the initial intent of this application to convert zip/cbz comic files for booklet printing.

## Requirements
The `requirements.txt` file should list all Python libraries that flexible-zip2pdf needs, and they will be installed using:

```
pip install -r requirements.txt
```

## CLI Documentation
The arguments list can be requested via --help
```
python zip2pdf.py --help
```
Which will output the documentation.
```
usage: zip2pdf [-h] [-f FILES [FILES ...]] [-d DIRECTORIES [DIRECTORIES ...]]
               [-r] -a {img2pdf,reportlab} [-o OUTPUT_PATH] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        one or more zip files to convert
  -d DIRECTORIES [DIRECTORIES ...], --directories DIRECTORIES [DIRECTORIES ...]
                        onr or more directories to look for *.zip files. May
                        be recursive with -r option
  -r, --recursive       recursively look under directories specified by -d
  -a {img2pdf,reportlab}, --algorithm {img2pdf,reportlab}
                        determine whether to use 'reportlab' or 'img2pdf'
                        algorithm.
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        set the output path of the PDF. default folder is
                        chdir
  -v, --version         show this application version
```

## Sample Usage: Recursive directory conversion with specified output path
Suppose you have a directory (relative to chdir) `./shonen` which has `/shonen/jujutsu_kaisen/*.zip` and `/shonen/one_piece/*.zip` under them.
This means you have to pick the parent directory `--directories shonen` and option `--recursive`.
To convert in a light and lossless way, then use algorithm `--algorithm img2pdf`. 
Finally set the output folder (relative to chdir) `--output-path ./shonen_pdf`
```
python zip2pdf.py --algorithm img2pdf --directories shonen --recursive --output-path ./shonen_pdf
```

Note when specific zip files failed, use the other algorithm `reportlab` instead. It will be slightly slower and heavier, with minimal compression.
As the image is directly embedded to the PDF. Also note that with reportlab the page and image size is fixed to A4 (aspect ratio is preserved). Option to adjust size and aspect ratio preservation will be added in the future.
```
python zip2pdf.py --algorithm reportlab --directories shonen --recursive --output-path ./shonen_pdf
```

## Sample Usage: Multiple directories and files
It is also possible to have multiple files and directories in a single request.

Suppose you have a directory (relative to chdir) ./shonen which has `/shonen/jujutsu_kaisen/*.zip` and `/shonen/one_piece/*.zip`. But suppose you want to avoid `/shonen/*.zip`and all the other sub folders while including `/shonen/hunter_x_hunter_ch001.zip` and `/shonen/hunter_x_hunter_ch002.zip `
Then the request will be.
```
python zip2pdf.py --algorithm reportlab --directories "/shonen/jujutsu_kaisen" "/shonen/one_piece" --files "/shonen/hunter_x_hunter_ch001.zip" "/shonen/hunter_x_hunter_ch002.zip "
```

