from typing import Optional
from warnings import warn

from numpy.typing import NDArray

from auxiliary.io import read_image, write_image


def write_nifti(
    input_array: NDArray,
    output_nifti_path: str,
    reference_nifti_path: Optional[str] = None,
    create_parent_directory: bool = False,
) -> None:
    """
    Write a NIfTI file from a NumPy array using SimpleITK.

    Args:
        input_array (np.ndarray): The NumPy array containing the data to be written.
        output_nifti_path (str): The path where the output NIfTI file will be saved.
        reference_nifti_path (str, optional): Path to a reference NIfTI file for spatial metadata.
        create_parent_directory (bool): If True, create parent directories if they don't exist.

    Returns:
        None
    """
    warn(
        "'auxiliary.nifti.io.write_nifti' is deprecated and will be removed in future versions. Use 'auxiliary.io.write_image' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    write_image(
        input_array=input_array,
        output_path=output_nifti_path,
        reference_path=reference_nifti_path,
        create_parent_directory=create_parent_directory,
    )


def read_nifti(
    input_nifti_path: str,
    maintain_dtype: bool = True,
) -> NDArray:
    """
    Read a NIfTI file and return its data as a NumPy array.

    Args:
        input_nifti_path (str): Path to the input NIfTI file.
        maintain_dtype (bool, optional): If True, maintain the data type of the NIfTI data.
                                         If False, allow data type conversion to float. Default is True.

    Returns:
        numpy.ndarray: NIfTI data as a NumPy array.
    """
    warn(
        "'auxiliary.nifti.io.read_nifti' is deprecated and will be removed in future versions. Use 'auxiliary.io.read_image' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return read_image(
        input_path=input_nifti_path,
        maintain_dtype=maintain_dtype,
    )
