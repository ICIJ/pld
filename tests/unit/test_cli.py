import pytest

from typer.testing import CliRunner
from src.cli import app


@pytest.fixture
def runner():
    return CliRunner()

def test_validate_relative_to(runner, mocker):
    # Given
    mocker.patch('src.pld.PdfLanguageDetector')
    # When
    result = runner.invoke(app, [
        "detect",
        "--language", "eng",
        "--language", "fra",
        "--input-dir", ".",
        "--relative-to", "/"
    ])
    # Then
    assert result.exit_code == 0

def test_dont_validate_relative_to(runner, mocker):
    # Given
    mocker.patch('src.pld.PdfLanguageDetector')
    # When
    result = runner.invoke(app, [
        "detect",
        "--language", "eng",
        "--language", "fra",
        "--input-dir", ".",
        "--relative-to", "./foo"
    ])
    # Then
    assert result.exit_code == 2
  
def test_validate_input_dir(runner, mocker, tmp_path):
  # Given
  mocker.patch('src.pld.PdfLanguageDetector')
  input_dir = tmp_path
  # When
  result = runner.invoke(app, [
      "detect",
      "--language", "eng",
      "--language", "fra",
      "--input-dir", input_dir
  ])
  # Then
  assert result.exit_code == 0

def test_dont_validate_input_dir(runner, mocker, tmp_path):
  # Given
  mocker.patch('src.pld.PdfLanguageDetector')
  input_dir = tmp_path / 'unknown'
  # When
  result = runner.invoke(app, [
      "detect",
      "--language", "eng",
      "--language", "fra",
      "--input-dir", input_dir
  ])
  # Then
  assert result.exit_code == 2

def test_validate_one_parallel(runner, mocker, tmp_path):
    # Given
    mocker.patch('src.pld.PdfLanguageDetector')
    paralell = 1
    # When
    with mocker.patch('os.cpu_count', return_value=10):
      result = runner.invoke(app, [
          "detect",
          "--language", "eng",
          "--language", "fra",
          "--input-dir", tmp_path,
          "--parallel", paralell
      ])
      # Then
      assert result.exit_code == 0

def test_validate_ten_parallel(runner, mocker, tmp_path):
    # Given
    mocker.patch('src.pld.PdfLanguageDetector')
    paralell = 10
    # When
    with mocker.patch('os.cpu_count', return_value=10):
      result = runner.invoke(app, [
          "detect",
          "--language", "eng",
          "--language", "fra",
          "--input-dir", tmp_path,
          "--parallel", paralell
      ])
      # Then
      assert result.exit_code == 0

def test_dont_validate_twenty_parallel(runner, mocker, tmp_path):
    # Given
    mocker.patch('src.pld.PdfLanguageDetector')
    paralell = 20
    # When
    with mocker.patch('os.cpu_count', return_value=10):
      result = runner.invoke(app, [
          "detect",
          "--language", "eng",
          "--language", "fra",
          "--input-dir", tmp_path,
          "--parallel", paralell
      ])
      # Then
      assert result.exit_code == 2

def test_validate_languages(runner, mocker, tmp_path):
  # Given
  mocker.patch('src.pld.PdfLanguageDetector')
  input_dir = tmp_path
  # When
  result = runner.invoke(app, [
      "detect",
      "--language", "spa",
      "--language", "ell",
      "--input-dir", input_dir
  ])
  # Then
  assert result.exit_code == 0

def test_dont_validate_languages(runner, mocker, tmp_path):
  # Given
  mocker.patch('src.pld.PdfLanguageDetector')
  input_dir = tmp_path
  # When
  result = runner.invoke(app, [
      "detect",
      "--language", "spa",
      "--language", "foo",
      "--input-dir", input_dir
  ])
  # Then
  assert result.exit_code == 2

def test_dont_validate_one_language(runner, mocker, tmp_path):
  # Given
  mocker.patch('src.pld.PdfLanguageDetector')
  input_dir = tmp_path
  # When
  result = runner.invoke(app, [
      "detect",
      "--language", "spa",
      "--input-dir", input_dir
  ])
  # Then
  assert result.exit_code == 2

def test_dont_validate_max_pages(runner, mocker, tmp_path):
    # Given
    mocker.patch('src.pld.PdfLanguageDetector')
    input_dir = tmp_path
    max_page = -5
    # When
    result = runner.invoke(app, [
        "detect",
        "--language", "spa",
        "--language", "ell",
        "--input-dir", input_dir,
        "--max-page", max_page
    ])
    # Then
    assert result.exit_code == 2