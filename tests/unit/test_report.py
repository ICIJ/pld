import json
import pytest

from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from src.report import Report


def test_get_coeff_avgs():
    # Given
    report = Report(report_file=Path('dummy_report_file'))
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
    report = Report(report_file=Path('dummy_report_file'))
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
    report = Report(report_file=Path('dummy_report_file'))
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

def test_fetch_valid_reports():
    # Given
    report = Report(report_file=Path('dummy_report_file'), output_dir=Path('dummy_output_dir'))
    
    # Mock methods
    with patch.object(Report, 'is_valid_output_dir') as mock_is_valid, \
        patch.object(Report, 'get_reports_dirs') as mock_get_reports_dirs, \
        patch.object(Report, 'get_output_dir_report') as mock_get_report:
        
        mock_is_valid.return_value = True
        mock_get_reports_dirs.return_value = ['dummy_report']
        mock_get_report.return_value = 'dummy_report'

        # When
        result = report.fetch_reports()
        
        # Then
        assert result == ['dummy_report']

def test_write_report():
    # Given
    report = Report(report_file=Path('dummy_report_file'), output_dir=Path('dummy_output_dir'))
    output_dir_reports = ['dummy_report']
    dummy_output = 'dummy_output'
    
    # Mock methods
    with patch.object(Report, 'get_output') as mock_get_output, \
        patch.object(Path, 'open') as mock_open:
        
        mock_get_output.return_value = dummy_output
        mock_open.return_value = mock_open_context = MagicMock()
        mock_file = MagicMock()
        mock_open_context.__enter__.return_value = mock_file

        # When
        report.write_report(output_dir_reports)

        # Then
        mock_file.write.assert_called_once_with(dummy_output)

def test_generate():
    # Given
    report = Report(report_file=Path('dummy_report_file'), output_dir=Path('dummy_output_dir'))
    
    # Mock methods
    with patch.object(Report, 'fetch_reports') as mock_fetch_reports, \
        patch.object(Report, 'write_report') as mock_write_report:
        
        # When
        report.generate()

        # Then
        mock_fetch_reports.assert_called_once()
        mock_write_report.assert_called_once()

def test_get_output():
    # Given
    report = Report(report_file=Path('dummy_report_file'), output_dir=Path('dummy_output_dir'))
    output_dirs = [{'lang': 'eng', 'input_file': 'dummy_input_file', 'output_dir': 'dummy_output_dir'}]
    
    # Mock spytula_builder
    with patch.object(Report, 'spytula_builder') as mock_spytula_builder:
        mock_spytula_builder.return_value.to_json.return_value = 'dummy_json'

        # When
        result = report.get_output(output_dirs)

        # Then
        assert result == 'dummy_json'

def test_get_output_unsupported_format():
    # Given
    report = Report(report_file=Path('dummy_report_file'), output_dir=Path('dummy_output_dir'), report_format='xml')
    output_dirs = [{'lang': 'eng', 'input_file': 'dummy_input_file', 'output_dir': 'dummy_output_dir'}]
    
    # When
    with pytest.raises(NotImplementedError):
        report.get_output(output_dirs)
