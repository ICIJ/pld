import json
import os
import pytesseract

from multiprocessing import Pool, JoinableQueue
from lingua import IsoCode639_3, LanguageDetectorBuilder
from langcodes import Language, find as find_language
from pathlib import Path
from PIL import Image
from rich import print
from sh import pdftoppm
from typing import Optional, List

class PdfLanguageDetector:
    def __init__(self, 
                languages: List[str], 
                input_dir: Path = Path(),
                output_dir: Optional[Path] = 'out',
                max_pages: Optional[int] = 5,
                resume:  Optional[bool] = False,
                skip_images:  Optional[bool] = False,
                skip_ocr:  Optional[bool] = False,
                parallel: Optional[int] = 1):
        """
        Initialize the PdfLanguageDetector class.

        Args:
            languages: List of ISO3 language codes.
            input_dir: Path to the input directory.
            output_dir: Path to the output directory.
            max_pages: Maximum number of pages to process per PDF file.
            resume: Skip PDF files already analyzed.
            skip_images: Skip the extraction of PDF files as images.
            skip_ocr: Skip the OCR of images from PDF files.
            parallel: Number of threads to run in parallel.
        """
        self.languages = [Language.get(language) for language in languages]
        self.lang_detector = LanguageDetectorBuilder.from_iso_codes_639_3(*self.lingua_langs).build()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.resume = resume
        self.skip_images = skip_images
        self.skip_ocr = skip_ocr
        self.parallel = parallel

    def create_output_directories(self, *dirs: Path):
        """
        Create output directories if they don't exist.

        Args:
            *dirs: Variable number of directory paths to create.
        """
        for dir_path in dirs:
            os.makedirs(dir_path.resolve(), exist_ok=True)
    
    def extract_meta(self, input_file: Path):
        output_dir = self.get_output_dir(input_file)
        meta_file = output_dir / 'meta.json'
        meta = dict(input_file=str(input_file.resolve()), output_dir=str(output_dir.resolve()))
        with meta_file.open("w") as f:
            f.write(json.dumps(meta, indent=2))

    def extract_images(self, input_file: Path, images_dir: Path):
        """
        Extract images from a PDF file using pdftoppm.

        Args:
            input_file: Path to the input PDF file.
            images_dir: Directory to save the extracted images.
        """
        pdftoppm('-l', self.max_pages, '-jpeg', input_file.resolve(), (images_dir / 'page').resolve())

    def extract_text(self, image_file: Path) -> str:
        """
        Extract text from an image using Tesseract OCR.

        Args:
            image_file: Path to the input image file.

        Returns:
            Extracted text from the image.
        """
        lang = '+'.join(self.tesseract_langs)
        image_text = pytesseract.image_to_string(Image.open(image_file), lang=lang)
        return image_text

    def save_text(self, image_text: str, text_file: Path):
        """
        Save extracted text to a text file.

        Args:
            image_text: Text to be saved.
            text_file: Path to the output text file.
        """
        with text_file.open("a") as f:
            f.write(image_text)

    def save_language(self, detected_lang, lang_file: Path):
        """
        Save detected language information to a JSON file.

        Args:
            detected_lang: Language detection result.
            lang_file: Path to the output JSON file.
        """
        langs = [language.name for language, _ in detected_lang]
        langs = [find_language(name).to_alpha3().upper() for name in langs]
        coeffs = [value for _, value in detected_lang]
        data = dict(zip(langs, coeffs))
        with lang_file.open("w") as f:
            f.write(json.dumps(data, indent=2))

    def process_images(self, images_dir: Path, texts_dir: Path, langs_dir: Path):
        """
        Process the extracted images, extract text, and save text and language information.

        Args:
            images_dir: Directory containing the extracted images.
            texts_dir: Directory to save the extracted text.
            langs_dir: Directory to save the language information.
        """
        for image_file in sorted(self.get_images_files(images_dir)):
            image_text = self.extract_text(image_file)
            detected_lang = self.lang_detector.compute_language_confidence_values(image_text)
            text_file = (texts_dir / image_file.stem).with_suffix('.txt')
            lang_file = (langs_dir / image_file.stem).with_suffix('.json')
            self.save_text(image_text, text_file)
            self.save_language(detected_lang, lang_file)

    def calculate_coeff_avgs(self, langs_dir: Path) -> dict:
        """
        Calculate the average coefficient for each language.

        Args:
            langs_dir: Directory containing the language information files.

        Returns:
            A dictionary with the average coefficient for each language.
        """
        coeff_avgs = dict.fromkeys([lang.to_alpha3().upper() for lang in self.languages], 0)
        for index, lang_file in enumerate(self.get_lang_files(langs_dir)):
            with lang_file.open(encoding="UTF-8") as source:
                coeffs = json.load(source)
                for lang in coeff_avgs:
                    coeff_avgs[lang] = (coeff_avgs[lang] * index + coeffs[lang]) / (index + 1)
        return coeff_avgs
        
    def get_lang_files(self, langs_dir: Path) -> list:
        """
        Get a list of language files in the specified directory.

        Args:
            langs_dir: Path to the directory containing language files.

        Returns:
            A list of language files.

        """
        return list(langs_dir.glob('*.json'))[:self.max_pages]

    def get_images_files(self, images_dir: Path) -> list:
        """
        Get a list of image files in the specified directory.

        Args:
            images_dir: Path to the directory containing image files.

        Returns:
            A list of image files.

        """
        return sorted(images_dir.glob('*.jpg'))[:self.max_pages]

    def analyse_file(self, input_file: Path, output_file_dir: Path) -> str:
        """
        Analyze a PDF file, extract images, process them, and calculate language averages.

        Args:
            input_file: Path to the input PDF file.
            output_file_dir: Directory to save the analysis results.

        Returns:
            The language with the highest average coefficient.
        """
        images_dir = output_file_dir / 'images'
        texts_dir = output_file_dir / 'texts'
        langs_dir = output_file_dir / 'langs'
        self.create_output_directories(images_dir, texts_dir, langs_dir)
        self.extract_meta(input_file)
        if not self.skip_images:
            self.extract_images(input_file, images_dir)
        if not self.skip_ocr:
            self.process_images(images_dir, texts_dir, langs_dir)
        coeff_avgs = self.calculate_coeff_avgs(langs_dir)
        coeff_avgs_file = output_file_dir.resolve() / 'avgs.json'
        with coeff_avgs_file.open("w") as f:
            f.write(json.dumps(coeff_avgs, indent=2))
        return max(coeff_avgs, key=coeff_avgs.get)

    def worker(self, queue: JoinableQueue):
        while True:
            input_file, output_file_dir = queue.get()
            try:
                if self.resume and self.is_already_analyzed(output_file_dir):
                    print(f"→ {input_file.resolve()} [blue]SKIPPED[/blue]")
                else:
                    print(f"┅ {input_file.resolve()}")
                    lang = self.analyse_file(input_file, output_file_dir)
                    print(f"✓ {input_file.resolve()} [green]{lang}[/green]")
            except Exception:
                print(f"✕ {input_file.resolve()} [red]ERROR[/red]")
            finally:
                queue.task_done()

    def process_input_files(self):
        """
        Process all the PDF files in the input directory.
        """
        # Create a queue that each worker will join
        queue = JoinableQueue(self.parallel)
        # Start a pool of worker processes
        with Pool(self.parallel, self.worker, (queue,)):
            for input_file in self.input_dir.glob('**/*.pdf'):
                output_file_dir = self.get_output_dir(input_file)
                queue.put((input_file, output_file_dir))
            queue.join()
                
    def get_output_dir(self, input_file: Path) -> Path:
        """
        Get the output directory path for a given input file.

        Args:
            input_file: Path to the input file.

        Returns:
            The output directory path.
        """
        output_file_dir = input_file.relative_to(self.input_dir)
        output_file_dir = output_file_dir.parent / output_file_dir.stem
        output_file_dir = self.output_dir / output_file_dir
        return output_file_dir
    
    def is_already_analyzed(self, output_file_dir: Path) -> bool:
        return (output_file_dir / 'avgs.json').exists()

    @property
    def tesseract_langs(self):
        """
        Get the list of languages for Tesseract. As opposed to Lingua,
        Tesseract uses ISO 639-2/B (derived from English)e.

        Returns:
            Languages as ISO 639-2/B string
        """
        return [lang.to_alpha3(variant="T") for lang in self.languages]

    @property
    def lingua_langs(self):
        """
        Get the list of languages for Lingua. As opposed to Tesseract,
        Tesseract uses ISO 639-2/A (derived from native names of languages)

        Returns:
            Languages as IsoCode639_3 constants
        """
        return [IsoCode639_3[lang.to_alpha3().upper()] for lang in self.languages]
