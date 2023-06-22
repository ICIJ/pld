import json

from spytula.builder import SpytulaBuilder
from langcodes import Language
from pathlib import Path
from rich.progress import Progress, SpinnerColumn
from typing import Optional, List

class Report:
    def __init__(self, report_file: Path, output_dir: Optional[Path] = 'out', report_format: Optional[str] = 'json'):
        """
        Initialize the PdfLanguageDetector class.

        Args:
            report_file: Path to the report file.
            output_dir: Path to the output directory.
            report_format: Format of the report after reading information in the output dir.
        """
        self.report_file = report_file
        self.output_dir = output_dir
        self.report_format = report_format.lower()

    def fetch_reports(self):
        """
        Fetch the report data from all valid output directories.

        This method glob all directories within the output directory path, 
        validate them and if valid, fetches the report from each directory.

        :return: List of reports
        """
        # Initialize a list to store all reports.
        output_dir_reports = []
        # Initialize a progress bar.
        with Progress(SpinnerColumn(), "[progress.description]{task.description}", transient=True) as progress:
            task = progress.add_task('Fetching reports...', total=None)            
            # Loop through each directory in the output directory path.
            for output_dir in self.get_reports_dirs():
                # Check if the current directory is a valid output directory.
                if self.is_valid_output_dir(output_dir):
                    # If the directory is valid, get the report and append it to the list.
                    report = self.get_output_dir_report(output_dir)
                    output_dir_reports.append(report)
                    count_reports = len(output_dir_reports)
                    # Update the progress bar.
                    progress.update(task, advance=1, description=f'Fetching reports... ({count_reports} done)')
        return output_dir_reports

    def write_report(self, output_dir_reports):
        """
        Write the report data to the report file.

        This method takes the list of reports, get the output and 
        write it into the report file.

        :param output_dir_reports: List of reports
        :return: None
        """
        count_reports = len(output_dir_reports)
        # Open the report file in write mode.
        with self.report_file.open("w") as report_file:
            # Get the output from the list of reports.
            output = self.get_output(output_dir_reports)
            # Write the output to the file.
            report_file.write(output)
        print(f"✓ {count_reports} report{'s'[:count_reports^1]} written to {self.report_file}")

    def generate(self):
        """
        Generate a report file with information aggregated from all valid output directories.

        This is the main method that calls fetch_reports method to fetch all reports 
        and then call write_report method to write those reports into the file.

        :return: None
        """
        # Fetch the reports from all valid output directories.
        output_dir_reports = self.fetch_reports()
        # Write the fetched reports into the file.
        self.write_report(output_dir_reports)


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
        return dict(lang=lang, **meta)
    
    def get_reports_dirs(self):
        """
        Returns a list of all reports dirs in the output_dir.

        Returns:
            A list of all reports dirs in the output_dir.
        """
        return self.output_dir.glob('*/**/')
        
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
            return json.load(source)
        
    def get_output(self, output_dirs: List[dict]):
        """
        Prints the output directories in the specified report format.

        Args:
            output_dirs: List of output directories.

        Raises:
            NotImplementedError: If the report format is not supported yet.
        """
        if self.report_format == 'json':
            return self.spytula_builder(output_dirs).to_json(indent=2)
        elif self.report_format == 'yaml':
            return self.spytula_builder(output_dirs).to_yaml(indent=2)
        else:
            raise NotImplementedError('This format is not supported yet.')
        
    def spytula_builder(self, output_dirs: List[dict]) -> SpytulaBuilder:
        """
        Instanciate a SpytulaBuilder with the output and the correct output structure

        Args:
            output_dirs: List of output directories.

        Returns:
            An instance SpytulaBuilder.
        """
        # The SpytulaBuilder is instanciated with an "output_dirs" root meaning
        # it will output this key instead of an object.
        builder = SpytulaBuilder(root='output_dirs')
        # Format key in camel case as it's the standart in Javascript
        builder.key_format(camelize={'uppercase_first_letter': False})
        # Each output dir has it's own report and attributes
        for (report_builder, report) in builder.each('output_dirs', output_dirs):
            lang_name = Language.get(report['lang']).display_name().upper()
            report_builder.attributes(report, ['lang', 'input_file', 'output_dir'])
            report_builder.attribute('lang_name', lang_name)
        return builder

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
        