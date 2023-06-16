import json
import pytest

from lingua import IsoCode639_3, Language
from pathlib import Path
from src.pld import PdfLanguageDetector
from unittest.mock import call, mock_open, patch

@pytest.fixture
def pdf_language_detector():
    languages = ['eng', 'fra']
    input_dir = Path('/input')
    output_dir = Path('/output')
    return PdfLanguageDetector(languages, input_dir, output_dir)

def test_create_output_directories(pdf_language_detector):
    # Given
    dirs = [Path('/output/subdir1'), Path('/output/subdir2')]
    with patch('os.makedirs') as mocked_makedirs:
        # When
        pdf_language_detector.create_output_directories(*dirs)
        # Then
        calls = [call(dir.resolve(), exist_ok=True) for dir in dirs]
        mocked_makedirs.assert_has_calls(calls)

def test_extract_meta(pdf_language_detector):
    # Given
    input_file = Path('/input/test.pdf')
    output_dir = pdf_language_detector.get_output_dir(input_file)
    meta = dict(input_file=str(input_file.resolve()), output_dir=str(output_dir.resolve()))
    with patch('pathlib.Path.open', new=mock_open()) as mock_file:
        # When
        pdf_language_detector.extract_meta(input_file)
        # Then
        mock_file.assert_called_with("w")
        mock_file().write.assert_called_once_with(json.dumps(meta, indent=2))

def test_save_text(pdf_language_detector):
    # Given
    text_file = Path('/output/test.txt')
    image_text = "Sample Text"
    with patch('pathlib.Path.open', new=mock_open()) as mock_file:
        # When
        pdf_language_detector.save_text(image_text, text_file)
        # Then
        mock_file.assert_called_with("a")
        mock_file().write.assert_called_once_with(image_text)

def test_save_language(pdf_language_detector):
    # Given
    detected_lang = [(Language.ENGLISH, 1), (Language.FRENCH, 0)]
    lang_file = Path('/output/lang.json')
    langs = ["ENG", "FRA"]
    coeffs = [1, 0]
    data = dict(zip(langs, coeffs))
    with patch('pathlib.Path.open', new=mock_open()) as mock_file:
        # When
        pdf_language_detector.save_language(detected_lang, lang_file)
        # Then
        mock_file.assert_called_with("w")
        mock_file().write.assert_called_once_with(json.dumps(data, indent=2))

def test_get_output_dir(pdf_language_detector):
    # Given
    input_file = Path('/input/foo/test.pdf')
    output_file_dir = Path('/output/foo/test')
    # When
    result = pdf_language_detector.get_output_dir(input_file)
    # Then
    assert result == output_file_dir

def test_is_already_analyzed(pdf_language_detector):
    # Given
    output_file_dir = Path('/output/test')
    with patch('pathlib.Path.exists') as mocked_exists:
        # When
        pdf_language_detector.is_already_analyzed(output_file_dir)
        # Then
        mocked_exists.assert_called_once_with()

def test_tesseract_langs(pdf_language_detector):
    # Given
    expected_result = ['eng', 'fra']
    # When
    result = pdf_language_detector.tesseract_langs
    # Then
    assert result == expected_result

def test_lingua_langs(pdf_language_detector):
    # Given
    expected_result = [IsoCode639_3.ENG, IsoCode639_3.FRA]
    # When
    result = pdf_language_detector.lingua_langs
    # Then
    assert result == expected_result

def test_get_output_dir_with_relative_to_none(mocker):
    # Given
    languages = ['eng', 'fra']
    input_dir = Path('input')
    output_dir = Path('output')
    input_file = Path('input/test.pdf')
    
    # Mock the resolve method to avoid actual file interactions
    mocker.patch.object(Path, "resolve", return_value=Path('input/test.pdf'))
    
    detector = PdfLanguageDetector(languages, input_dir=input_dir, output_dir=output_dir)
    expected_output_dir = output_dir / 'test'

    # When
    actual_output_dir = detector.get_output_dir(input_file)
    
    # Then
    assert actual_output_dir.resolve() == expected_output_dir.resolve()

def test_get_output_dir_with_relative_to(mocker):
    # Given
    languages = ['eng', 'fra']
    input_dir = Path('input')
    output_dir = Path('output')
    relative_to = Path('input/subfolder')
    input_file = Path('input/subfolder/test.pdf')
    
    # Mock the resolve method to avoid actual file interactions
    mocker.patch.object(Path, "resolve", return_value=Path('input/subfolder/test.pdf'))
    
    detector = PdfLanguageDetector(languages, input_dir=input_dir, output_dir=output_dir, relative_to=relative_to)
    expected_output_dir = output_dir / 'test'

    # When
    actual_output_dir = detector.get_output_dir(input_file)
    
    # Then
    assert actual_output_dir.resolve() == expected_output_dir.resolve()
