import typer

from pathlib import Path
from typing import Optional, List
from src.pld import PdfLanguageDetector

app = typer.Typer()

@app.command()
def main(languages: List[str] = typer.Option(..., '--language', help="An ISO3 language code."), 
         input_dir: Path  = typer.Option(..., '--input_dir', help="Path to the input directory."),
         output_dir: Optional[Path] = typer.Option('out', help="Path to the output directory."),
         max_pages: Optional[int] = typer.Option(5, help="Maximum number of pages to process per PDF file.")):
    """
    Process PDF files and detect the dominant language.
    """
    detector = PdfLanguageDetector(languages, input_dir, output_dir, max_pages)
    detector.process_input_files()


if __name__ == "__main__":
    typer.run(main)
