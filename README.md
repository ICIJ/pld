# PLD (PDF Language Detector)  [![](https://img.shields.io/github/actions/workflow/status/icij/pld/main.yml)](https://github.com/ICIJ/pld/actions)


PLD is a Python program that analyzes PDF files, extracts images, processes them using Optical Character Recognition (OCR), and detects the dominant language of the text. It provides language detection information in JSON format and calculates the average confidence coefficient for each language.

## Requirements

- [Python 3.8](https://www.python.org/downloads/) or above
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [pdftoppm](https://poppler.freedesktop.org/)

## Installation

Install Tesseract OCR and pdftoppm using your package manager. For example, on Ubuntu:

```bash
sudo apt install tesseract-ocr tesseract-ocr-all poppler-utils
```

### From PyPi

Install with pip:

```bash
python3 -m pip install --user pdf-language-detector
```

Then run directly from your terminal:

```bash
pld --help
````

### From the sources

Clone the PLD repository:

```bash
git clone git@github.com:github.com/icij/pld.git
```

Install the required Python packages with poetry:

```bash
poetry install
````

Then run inside a virtual env managed by poetry:

```bash
poetry run pld --help
````

### From Docker

Install with Docker:

```bash
docker pull icij/pld
```

Then run inside a container:

```bash
docker run -it icij/pld pld --help
```

## Usage

### Detect

This command process PDF files and detect the dominant language.

```
pld detect --help

    --language A list of ISO3 language codes to detect.
    --input-dir: Path to the input directory containing PDF files. Default is the current directory.
    --output-dir (optional): Path to the output directory. Default is 'out' directory in the current directory.
    --max-pages (optional): Maximum number of pages to process per PDF file. Default is 5.
    --resume (optional): Skip PDF files already analyzed.
    --skip-images (optional): Skip the extraction of PDF files a images.
    --skip-ocr (optional): Skip the OCR of images from PDF files.
    --parallel (optional): Number of threads to run in parallel.
    --relative-to (optional): Path to the directory relative to which build the output dir path.
```

### Report

This command print a report from the previously detected language (using the same output dir).

```
pld report --help

    --output-dir: Path to the output directory. Default is 'out' directory in the current directory.
```

## Test

You can run the test suite (propulsed by pytest) with this command:

```bash
make test
```

## Examples

Process PDF files in the current directory, detect English and Spanish languages, and save the results in the 'results' directory:

```bash
pld --language eng --language spa --input-dir documents --output-dir results
```

Process PDF files in the 'documents' directory, detect French and Greek languages, and limit the processing to 3 pages per file:

```bash
pld --language fra --language ell --input-dir documents --max-pages 3
```

## License

This project is licensed under the MIT License.
