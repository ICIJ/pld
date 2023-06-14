import os
import sys
import typer
import pytesseract

from contextlib import contextmanager
from sh import pdfimages
from pathlib import Path
from typing import Optional
from PIL import Image

from lingua import Language, LanguageDetectorBuilder

tesseract_langs = ['grc', 'eng']
lingua_langs = [Language.GREEK, Language.ENGLISH]
lang_detector = LanguageDetectorBuilder.from_languages(*lingua_langs)


def print_flush(msg: str):
    sys.stdout.write('\r{0}'.format(msg))
    sys.stdout.flush()


@contextmanager
def print_done(msg: str):
    # Avoid conflicting with a high log level
    msg = '\r%s...' % msg
    print_flush(msg)
    yield
    print('{0} \033[92mdone\033[0m'.format(msg))


def get_output_dir(input_file: Path, input_dir: Path, output_dir: Path):
    output_file_dir = input_file.relative_to(input_dir)
    output_file_dir = output_file_dir.parent / output_file_dir.stem
    output_file_dir = output_dir / output_file_dir
    return output_file_dir


def analyse_file(input_file: Path, output_file_dir: Path):
    images_dir = output_file_dir / 'images'
    texts_dir = output_file_dir / 'texts'
    # Build the directories to save images and text    
    os.makedirs(images_dir.resolve(), exist_ok=True)
    os.makedirs(texts_dir.resolve(), exist_ok=True)
    # Extract images with pdfimages
    pdfimages('-tiff', input_file.resolve(), (images_dir / 'page').resolve())
    # Iterate of each image
    for image_file in images_dir.glob('**/*.tif'):
        text_dir = texts_dir / '-'.join(tesseract_langs)
        os.makedirs(text_dir.resolve(), exist_ok=True)
        text_file = (text_dir / image_file.stem).with_suffix('.txt')
        with text_file.open("a") as f: 
            lang = '+'.join(tesseract_langs)
            image_text = pytesseract.image_to_string(Image.open(image_file), lang=lang)
            print(lang_detector.detect_language_of(image_text))
            f.write(image_text)


def main(input_dir: Path, output_dir: Optional[Path] = typer.Option('out')):
    # Iterate of each PDF in the input dir
    for input_file in input_dir.glob('**/*.pdf'):
        output_file_dir = get_output_dir(input_file, input_dir, output_dir)
        with print_done(input_file.resolve()):
            analyse_file(input_file, output_file_dir)
        
    
if __name__ == "__main__":
    typer.run(main)
