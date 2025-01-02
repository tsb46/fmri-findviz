import pytest
from io import StringIO, BytesIO
from unittest.mock import Mock
from findviz.viz.io.utils import (
    get_filename,
    get_file_ext,
    parse_nifti_file_ext,
    get_csv_reader
)

def test_get_filename():
    """Test getting filename from different input types"""
    # Test with string path
    assert get_filename('/path/to/file.txt') == 'file.txt'
    assert get_filename('file.txt') == 'file.txt'
    
    # Test with FileStorage mock
    mock_file = Mock()
    mock_file.filename = 'uploaded.txt'
    assert get_filename(mock_file) == 'uploaded.txt'

def test_get_file_ext():
    """Test getting file extensions from various file paths"""
    assert get_file_ext('file.txt') == '.txt'
    assert get_file_ext('file.csv') == '.csv'
    assert get_file_ext('file.nii') == '.nii'
    
    assert get_file_ext('/path/to/file.txt') == '.txt'
    assert get_file_ext('../../file.csv') == '.csv'
    assert get_file_ext('file.name.txt') == '.txt'
    assert get_file_ext('file') == ''
    assert get_file_ext('file.') == '.'

def test_parse_nifti_file_ext():
    """Test parsing nifti file extensions"""
    assert parse_nifti_file_ext('file.nii') == '.nii'
    assert parse_nifti_file_ext('file.nii.gz') == '.nii.gz'
    assert parse_nifti_file_ext('file.txt') is None
    assert parse_nifti_file_ext('file.gz') is None
    assert parse_nifti_file_ext('file') is None

def test_get_csv_reader_cli():
    """Test CSV reader creation for CLI method"""
    test_data = "a,b,c\n1,2,3\n4,5,6"
    mock_file = StringIO(test_data)
    
    reader = get_csv_reader(mock_file, method='cli')
    rows = list(reader)
    assert len(rows) == 3
    assert rows[0] == ['a', 'b', 'c']
    assert rows[1] == ['1', '2', '3']

def test_get_csv_reader_browser():
    """Test CSV reader creation for browser method"""
    test_data = "a,b,c\n1,2,3\n4,5,6"
    
    # Create a mock file object that behaves like a browser upload
    mock_file = Mock()
    mock_file.stream = BytesIO(test_data.encode('utf-8-sig'))
    
    reader = get_csv_reader(mock_file, method='browser')
    rows = list(reader)
    assert len(rows) == 3
    assert rows[0] == ['a', 'b', 'c']
    assert rows[1] == ['1', '2', '3']

def test_get_csv_reader_with_custom_delimiter():
    """Test CSV reader with custom delimiter"""
    test_data = "a;b;c\n1;2;3"
    mock_file = StringIO(test_data)
    
    reader = get_csv_reader(mock_file, delimiter=';', method='cli')
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == ['a', 'b', 'c']
    assert rows[1] == ['1', '2', '3']

def test_get_csv_reader_error_handling():
    """Test error handling in CSV reader creation"""
    # Test CLI method with invalid file
    mock_file = Mock()
    mock_file.read.side_effect = Exception("Read error")
    
    with pytest.raises(Exception):
        get_csv_reader(mock_file, method='cli')
    
    # Test browser method with invalid file
    mock_file = Mock()
    mock_file.stream = Mock()
    mock_file.stream.read.side_effect = Exception("Stream error")
    
    with pytest.raises(Exception):
        get_csv_reader(mock_file, method='browser')

def test_get_csv_reader_encoding():
    """Test CSV reader with different encodings"""
    # Test with UTF-8 BOM encoding
    test_data = "a,b,c\n1,2,3" 
    mock_file = Mock()
    # Add BOM to the beginning of the bytes
    bom = b'\xef\xbb\xbf'  # UTF-8 BOM
    mock_file.stream = BytesIO(bom + test_data.encode('utf-8'))
    
    reader = get_csv_reader(mock_file, method='browser')
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == ['a', 'b', 'c']
    assert rows[1] == ['1', '2', '3']

def test_get_csv_reader_with_empty_file():
    """Test CSV reader with empty file"""
    mock_file = Mock()
    mock_file.stream = BytesIO(b"")
    
    reader = get_csv_reader(mock_file, method='browser')
    rows = list(reader)
    assert len(rows) == 0

def test_get_csv_reader_with_whitespace():
    """Test CSV reader with whitespace in data"""
    test_data = "  a  ,  b  ,  c  \n 1 , 2 , 3 "
    mock_file = Mock()
    mock_file.stream = BytesIO(test_data.encode('utf-8-sig'))
    
    reader = get_csv_reader(mock_file, method='browser')
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == ['  a  ', '  b  ', '  c  ']
    assert rows[1] == [' 1 ', ' 2 ', ' 3 ']