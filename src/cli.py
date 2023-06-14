import typer

from pathlib import Path
from typing import Optional, List
from src.pld import PdfLanguageDetector

app = typer.Typer()

@app.command()
def main(languages: List[str] = typer.Option(..., '--language'), 
         input_dir: Path  = typer.Option(..., '--input_dir'),
         output_dir: Optional[Path] = typer.Option('out'),
         max_pages: Optional[int] = 5):
    """
    Process PDF files and detect the dominant language.
    """
    detector = PdfLanguageDetector(languages, input_dir, output_dir, max_pages)
    detector.process_input_files()


if __name__ == "__main__":
    typer.run(main)
