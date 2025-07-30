import os
import zipfile

def Zip(input_filepath, output_zipfile=None):
    """
    Compress a file into a .zip archive.

    Args:
        input_filepath (str): Path to the file to compress.
        output_zipfile (str, optional): Path to the output .zip file. 
            If None, will use input_filepath + '.zip'.

    Returns:
        str: Path to the created .zip file.

    Raises:
        FileNotFoundError: If the input file does not exist.
        OSError: If compression fails.
    """

    if not os.path.isfile(input_filepath):
        raise FileNotFoundError(f"No such file: '{input_filepath}'")

    if output_zipfile is None:
        output_zipfile = input_filepath + '.zip'

    try:
        with zipfile.ZipFile(output_zipfile, 'w', zipfile.ZIP_DEFLATED) as zipf:
            arcname = os.path.basename(input_filepath)
            zipf.write(input_filepath, arcname=arcname)
    except Exception as e:
        raise OSError(f"Failed to compress '{input_filepath}' to '{output_zipfile}': {e}")

    return output_zipfile


def Unzip(zip_filepath, output_dir=None):
    """
    Decompress a .zip archive.

    Args:
        zip_filepath (str): Path to the .zip file to decompress.
        output_dir (str, optional): Directory to extract files to. 
            If None, extracts to the same directory as the zip file.

    Returns:
        str: Path to the directory where files were extracted.

    Raises:
        FileNotFoundError: If the zip file does not exist.
        OSError: If decompression fails.
    """
    if not os.path.isfile(zip_filepath):
        raise FileNotFoundError(f"No such zip file: '{zip_filepath}'")

    if output_dir is None:
        output_dir = os.path.splitext(zip_filepath)[0]

    try:
        with zipfile.ZipFile(zip_filepath, 'r') as zipf:
            zipf.extractall(output_dir)
    except Exception as e:
        raise OSError(f"Failed to decompress '{zip_filepath}' to '{output_dir}': {e}")

    return output_dir
