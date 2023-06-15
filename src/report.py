import json
from langcodes import Language
from pathlib import Path
from typing import Optional, List

class Report:
    def __init__(self, output_dir: Optional[Path] = 'out', report_format: Optional[str] = 'json'):
        """
        Initialize the PdfLanguageDetector class.

        Args:
            output_dir: Path to the output directory.
            report_format: Format of the report after reading information in the output dir.
        """
        self.output_dir = output_dir
        self.report_format = report_format

    def generate(self):
        output_dirs = list(map(self.get_output_dir_report, self.output_dirs))
        self.print_output_dirs(output_dirs)

    def get_output_dir_report(self, output_dir) -> dict:
        """
        Returns a dictionary containing the language, language name, and metadata for a given output directory.

        Args:
            output_dir: Path to the output directory.

        Returns:
            A dictionary with the language, language name, and metadata.
        """
        coeff_avgs = self.get_coeff_avgs(output_dir)
        meta = self.get_output_dir_meta(output_dir)
        lang = max(coeff_avgs, key=coeff_avgs.get)
        lang_name = Language.get(lang).display_name().upper()
        return dict(lang=lang, lang_name=lang_name, **meta)
        
    def get_coeff_avgs(self, output_dir: Path) -> dict:
        """
        Returns a dictionary containing the coefficient averages for a given output directory.

        Args:
            output_dir: Path to the output directory.

        Returns:
            A dictionary with the coefficient averages.
        """
        avgs_file = output_dir / 'avgs.json'
        with avgs_file.open(encoding="UTF-8") as source:
            coeff_avgs = json.load(source)
            return coeff_avgs     
        
    def get_output_dir_meta(self, output_dir: Path) -> dict:
        """
        Returns the metadata for a given output directory.

        Args:
            output_dir: Path to the output directory.

        Returns:
            A dictionary with the metadata.
        """
        meta_file = output_dir / 'meta.json'
        if not meta_file.exists():
            return dict()
        with meta_file.open(encoding="UTF-8") as source:
            meta = json.load(source)
            return meta    
        
    def print_output_dirs(self, output_dirs: List[dict]):
        """
        Prints the output directories in the specified report format.

        Args:
            output_dirs: List of output directories.

        Raises:
            NotImplementedError: If the report format is not supported yet.
        """
        if self.report_format == 'json':
            print(json.dumps(output_dirs, indent=2))
        else:
            raise NotImplementedError('This format is not supported yet.')

    @property
    def output_dirs(self) -> list:
        """
        Returns a list of valid output directories.

        Returns:
            A list of valid output directories.
        """
        output_dirs = self.output_dir.glob('*/**/')
        filtered_output_dirs = filter(self.is_valid_output_dir, output_dirs)
        return list(filtered_output_dirs)

    def is_valid_output_dir(self, output_dir) -> bool:
        """
        Checks if an output directory is valid.

        Args:
            output_dir: Output directory to check.

        Returns:
            True if the output directory is valid, False otherwise.
        """
        sub_dirs = [output_dir / 'images', output_dir / 'langs', output_dir / 'texts']
        sub_files = [output_dir / 'avgs.json', output_dir / 'meta.json']
        return all(d.is_dir() for d in sub_dirs) and all(d.is_file() for d in sub_files)
        