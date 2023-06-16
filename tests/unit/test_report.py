import json
import pytest

from pathlib import Path
from unittest.mock import patch, MagicMock
from src.report import Report


def test_get_coeff_avgs():
    # Given
    report = Report()
    output_dir = Path('/valid/dir')
    coeff_avgs_content = {'ENG': 1, 'FRA': 0}

    # Mock the Path object and its methods
    with patch('pathlib.Path.open', new=MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(coeff_avgs_content)

        # When
        result = report.get_coeff_avgs(output_dir)

        # Then
        assert result == coeff_avgs_content

def test_is_valid_output_dir():
    # Given
    report = Report()
    output_dir = Path('/valid/dir')
    # Mock the Path objects and their is_dir and is_file methods
    with patch('pathlib.Path.is_dir') as mock_is_dir, patch('pathlib.Path.is_file') as mock_is_file:
        mock_is_dir.return_value = True
        mock_is_file.return_value = True

        # When
        result = report.is_valid_output_dir(output_dir)

        # Then
        assert result

def test_get_output_dir_meta():
    # Given
    report = Report()
    output_dir = Path('/valid/dir')
    meta_content = {'key': 'value'}

    # Mock the Path object and its methods
    with patch('pathlib.Path.exists') as mock_exists, patch('pathlib.Path.open', new=MagicMock()) as mock_open:
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(meta_content)

        # When
        result = report.get_output_dir_meta(output_dir)

        # Then
        assert result == meta_content

def test_get_output_dir_report():
    # Given
    report = Report()
    output_dir = Path('/valid/dir')
    coeff_avgs_content = {'eng': 1, 'fra': 0}
    meta_content = {'key': 'value'}

    # Mock methods
    with patch.object(Report, 'get_coeff_avgs') as mock_get_coeff_avgs, \
         patch.object(Report, 'get_output_dir_meta') as mock_get_output_dir_meta:
        mock_get_coeff_avgs.return_value = coeff_avgs_content
        mock_get_output_dir_meta.return_value = meta_content

        # When
        result = report.get_output_dir_report(output_dir)

        # Then
        assert result == {'lang': 'eng', 'lang_name': 'ENGLISH', 'key': 'value'}

def test_print_output_dirs():
    # Given
    report = Report(report_format='json')
    output_dirs = [{'lang': 'eng', 'lang_name': 'ENGLISH', 'key': 'value'}]

    # Mock print function
    with patch('builtins.print') as mock_print:
        # When
        report.print_output_dirs(output_dirs)

        # Then
        mock_print.assert_called_once_with(json.dumps(output_dirs, indent=2))

def test_print_output_dirs_unsupported_format():
    # Given
    report = Report(report_format='xml')
    output_dirs = [{'lang': 'eng', 'lang_name': 'ENGLISH', 'key': 'value'}]

    # When
    with pytest.raises(NotImplementedError):
        report.print_output_dirs(output_dirs)
