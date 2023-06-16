import typer
import os
from pathlib import Path
from typing import Optional, List
from src.pld import PdfLanguageDetector
from src.report import Report
from langcodes import Language
from langcodes.tag_parser import LanguageTagError

app = typer.Typer()

def validate_relative_to(ctx: typer.Context, param: typer.CallbackParam, value: Optional[Path]) -> Optional[Path]:
    """
    Validate that 'relative_to' is a parent of 'input_dir' or the input_dir itself.
    """
    input_dir = ctx.params.get("input_dir")
    if value is not None and value.resolve() != input_dir.resolve() and not value.resolve() in input_dir.resolve().parents:
        raise typer.BadParameter("relative_to must be a parent directory of input_dir, or the input_dir itself")
    return value

def validate_input_dir(ctx: typer.Context, param: typer.CallbackParam, value: Path) -> Path:
    """
    Validate that 'input_dir' exists.
    """
    if not value.is_dir():
        raise typer.BadParameter("input_dir must exist and be a directory")
    return value

def validate_parallel(ctx: typer.Context, param: typer.CallbackParam, value: int) -> int:
    """
    Validate that 'parallel' is not higher than the number of CPUs.
    """
    if value > os.cpu_count():
        raise typer.BadParameter("parallel must not be higher than the number of CPUs")
    return value

def validate_languages(ctx: typer.Context, param: typer.CallbackParam, value: List[str]) -> List[str]:
    """
    Validate that 'languages' is a valid list of ISO3 language codes.
    """
    if len(value) < 2:
        raise typer.BadParameter(f"You must specify at least 2 languages")
    for lang in value:
        try:
            if not Language.get(lang).is_valid():
                raise LanguageTagError()
        except LanguageTagError:
            raise typer.BadParameter(f"{lang} is not a valid ISO3 language code")
    return value

def validate_max_pages(ctx: typer.Context, param: typer.CallbackParam, value: int) -> int:
    """
    Validate that 'max_pages' is positive.
    """
    if value <= 0:
        raise typer.BadParameter("max_pages must be a positive integer")
    return value


@app.command()
def detect(
    languages: List[str] = typer.Option(..., '--language', help="An ISO3 language code.", callback=validate_languages), 
    input_dir: Path = typer.Option(..., '--input-dir', help="Path to the input directory.", callback=validate_input_dir),
    output_dir: Optional[Path] = typer.Option('out', help="Path to the output directory."),
    max_pages: Optional[int] = typer.Option(5, help="Maximum number of pages to process per PDF file.", callback=validate_max_pages),
    resume: Optional[bool] = typer.Option(False, help="Skip PDF files already analyzed."),
    skip_images: Optional[bool] = typer.Option(False, help="Skip the extraction of PDF files as images."),
    skip_ocr: Optional[bool] = typer.Option(False, help="Skip the OCR of images from PDF files."),
    parallel: Optional[int] = typer.Option(1, help="Number of paralell PDF to process in threads.", callback=validate_parallel),
    relative_to: Optional[Path] = typer.Option(None, help="Path to the directory relative to which build the output dir path.", callback=validate_relative_to)):
    """
    Process PDF files and detect the dominant language.
    """
    detector = PdfLanguageDetector(languages, input_dir, output_dir, max_pages, resume, 
                                   skip_images, skip_ocr, parallel, relative_to)
    detector.process_input_files()

@app.command()
def report(output_dir: Optional[Path] = typer.Option('out', help="Path to the output directory.")):
    """
    Process generated files to output a report
    """
    report = Report(output_dir)
    report.generate()