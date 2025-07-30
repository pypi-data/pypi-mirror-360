import os

import numpy as np
from tifffile import imread, imwrite

from auxiliary.turbopath import turbopath


def read_tiff(tiff_path: str) -> np.ndarray:
    """
    Read a TIFF file and return its data as a NumPy array.

    Args:
        tiff_path (str): Path to the TIFF file to be read.

    Returns:
        np.ndarray: Data from the TIFF file as a NumPy array.
    """
    data = imread(tiff_path)
    return data


def write_tiff(
    numpy_array: np.ndarray,
    output_tiff_path: str,
    create_parent_directory: bool = False,
    transpose: bool = False,
) -> None:
    """
    Write a NumPy array to a TIFF file.

    Args:
        numpy_array (np.ndarray): NumPy array containing the data to be written.
        output_tiff_path (str): Path to the output TIFF file.
        create_parent_directory (bool): Whether to create the parent directory if it doesn't exist.
        transpose (bool): Whether to transpose the input array before writing.
    """
    if transpose:
        numpy_array = numpy_array.T

    if create_parent_directory:
        output_tiff_path = turbopath(
            output_tiff_path
        )  # Custom function to modify the path
        parent_dir = output_tiff_path.parent
        os.makedirs(parent_dir, exist_ok=True)

    # Write the NumPy array to the specified TIFF file
    imwrite(output_tiff_path, numpy_array)
