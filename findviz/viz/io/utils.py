"""
File I/O utilities
"""
import csv
import os

from typing import List, Literal, Iterator, Optional
from io import TextIOWrapper


def get_file_ext(fp: str) -> str:
    """
    get file ext from file path
    """
    base, ext = os.path.splitext(fp)
    return ext


def parse_nifti_file_ext(fp: str) -> Optional[Literal['.nii', '.nii.gz']]:
    """
    get file extension from nifti file path (.nii or .nii.gz). If the file
    is not a nifti file extension return None.
    """
    base, ext = os.path.splitext(fp)
    if ext == '.gz':
        base, ext = os.path.splitext(base)
        if ext == '.nii':
            return '.nii.gz'
        else:
            return
    elif ext == '.nii':
        return '.nii'
    else:
        return

def get_csv_reader(
    file,
    delimiter: str = ',',
    method=Literal['cli', 'browser']
) -> Iterator[List]:
    """
    Return csv reader with specified delimeter based on method of upload.
    Filestream for browser upload.
    """
    if method == 'cli':
        try:
            reader = csv.reader(file, delimiter = delimiter)
        # propagate error to parent function
        except Exception as e:
            raise e
    elif method == 'browser':
        try:
            file_stream = TextIOWrapper(file.stream, encoding='utf-8-sig')
            reader = csv.reader(file_stream, delimiter=delimiter)
        # propagate error to parent function
        except Exception as e:
            raise e

    return reader