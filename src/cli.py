import typer

from pathlib import Path
from typing import Optional, List
from src.pld import PdfLanguageDetector
from src.report import Report

app = typer.Typer()

@app.command()
def detect(languages: List[str] = typer.Option(..., '--language', help="An ISO3 language code."), 
         input_dir: Path  = typer.Option(..., '--input-dir', help="Path to the input directory."),
         output_dir: Optional[Path] = typer.Option('out', help="Path to the output directory."),
         max_pages: Optional[int] = typer.Option(5, help="Maximum number of pages to process per PDF file."),
         resume: Optional[bool] = typer.Option(False, help="Skip PDF files already analyzed."),
         skip_images:  Optional[bool] = typer.Option(False, help="Skip the extraction of PDF files as images."),
         skip_ocr:  Optional[bool] = typer.Option(False, help="Skip the OCR of images from PDF files."),
         parallel: Optional[int] = typer.Option(1, help="Number of paralell PDF to process in threads.")):
    """
    Process PDF files and detect the dominant language.
    """
    detector = PdfLanguageDetector(languages, input_dir, output_dir, max_pages, resume, skip_images, skip_ocr, parallel)
    detector.process_input_files()

@app.command()
def report(output_dir: Optional[Path] = typer.Option('out', help="Path to the output directory.")):
    """
    Process generated files to output a report
    """
    report = Report(output_dir)
    report.generate()