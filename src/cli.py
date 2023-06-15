import typer

from pathlib import Path
from typing import Optional, List
from src.pld import PdfLanguageDetector

app = typer.Typer()

@app.command()
def main(languages: List[str] = typer.Option(..., '--language', help="An ISO3 language code."), 
         input_dir: Path  = typer.Option(..., '--input-dir', help="Path to the input directory."),
         output_dir: Optional[Path] = typer.Option('out', help="Path to the output directory."),
         max_pages: Optional[int] = typer.Option(5, help="Maximum number of pages to process per PDF file."),
         skip_images:  Optional[bool] = typer.Option(False, help="Skip the extraction of PDF files as images."),
         skip_ocr:  Optional[bool] = typer.Option(False, help="Skip the OCR of images from PDF files.")):
    """
    Process PDF files and detect the dominant language.
    """
    detector = PdfLanguageDetector(languages, input_dir, output_dir, max_pages, skip_images, skip_ocr)
    detector.process_input_files()


if __name__ == "__main__":
    typer.run(main)
