# PLD (PDF Language Detector)

PLD is a Python program that analyzes PDF files, extracts images, processes them using Optical Character Recognition (OCR), and detects the dominant language of the text. It provides language detection information in JSON format and calculates the average confidence coefficient for each language.

## Requirements

- Python 3.8 or above
- Tesseract OCR
- pdftoppm

## Installation

1. Clone the PLD repository:

```bash
git clone https://github.com/icij/pld.git
```

Install Tesseract OCR and pdftoppm using your package manager. For example, on Ubuntu:

```bash
sudo apt install tesseract-ocr tesseract-ocr-all poppler-utils
```

Install the required Python packages:

```bash
poetry install
````

## Usage


```bash
poetry run pld --help

    --language A comma-separated list of ISO3 language codes to detect.
    --input-dir (optional): Path to the input directory containing PDF files. Default is the current directory.
    --output-dir (optional): Path to the output directory. Default is 'out' directory in the current directory.
    --max-pages (optional): Maximum number of pages to process per PDF file. Default is 5.
```

## Examples

Process PDF files in the current directory, detect English and Spanish languages, and save the results in the 'results' directory:

```bash
poetry run pld --language eng y --languagespa --output-dir results
```

Process PDF files in the 'documents' directory, detect French and Greek languages, and limit the processing to 3 pages per file:

```bash
python run pld --language fra --language ell --input-dir documents --max-pages 3
```

## License

This project is licensed under the MIT License.
