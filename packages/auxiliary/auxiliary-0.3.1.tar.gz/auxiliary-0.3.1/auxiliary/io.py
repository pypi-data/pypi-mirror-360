from pathlib import Path
from typing import Optional

import numpy as np
import SimpleITK as sitk
from numpy.typing import NDArray


def write_image(
    input_array: str | NDArray,
    output_path: str,
    reference_path: Optional[str] = None,
    create_parent_directory: bool = False,
) -> None:
    """
    Write an image file from a NumPy array or file using SimpleITK.
    Supports e.g. NIfTI and other formats. More details: https://simpleitk.readthedocs.io/en/master/IO.html

    Args:
        input_array (numpy.ndarray or str): The NumPy array containing the data to be written or the path to it.
            Note: boolean arrays will be converted to uint8.
        output_path (str): The path where the output file will be saved.
        reference_path (str, optional): Path to a reference file for spatial metadata.
        create_parent_directory (bool): If True, create parent directories if they don't exist.

    Returns:
        None
    """
    if isinstance(input_array, str):
        input_array = read_image(input_path=input_array)
    elif input_array.dtype == bool:
        # Convert bool arrays to uint8 for SimpleITK compatibility
        input_array = input_array.astype(np.uint8)

    # Convert NumPy array to SimpleITK image (zyx expected)
    image = sitk.GetImageFromArray(input_array)

    if reference_path:
        reference = sitk.ReadImage(reference_path)
        image.CopyInformation(reference)

    if create_parent_directory:
        parent_dir = Path(output_path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)

    sitk.WriteImage(image, output_path)


def read_image(
    input_path: str,
    force_dtype: Optional[int] = None,
) -> NDArray:
    """
    Read an image file using SimpleITK and return its data as a NumPy array.
    Supports e.g. NIfTI and other formats. More details: https://simpleitk.readthedocs.io/en/master/IO.html

    Args:
        input_path (str): Path to the input file.
        force_dtype: Optional[int]: If provided, cast the image to the given sitk data type, e.g. sitk.sitkFloat32.

    Returns:
        numpy.ndarray: Image data as a NumPy array.
    """

    image = sitk.ReadImage(input_path)
    if force_dtype is None:
        array = sitk.GetArrayFromImage(image)
    else:
        array = sitk.GetArrayFromImage(sitk.Cast(image, force_dtype))

    return array
