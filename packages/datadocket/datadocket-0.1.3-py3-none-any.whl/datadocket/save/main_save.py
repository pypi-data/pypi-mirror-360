import json
import csv


def Txt(filepath, data, mode="w", encoding="utf-8"):
    """
    Saves data to a text file.

    Args:
        filepath (str): Path to the text file.
        data (str): Data to write to the file.
        encoding (str, optional): Encoding to use. Defaults to "utf-8".

    Raises:
        IOError: If there is an error writing the file.
    """
    with open(filepath, mode, encoding=encoding) as f:
        f.write(data)


def Json(filepath, data, mode="w", encoding="utf-8", **json_kwargs):
    """
    Saves data to a JSON file.

    Args:
        filepath (str): Path to the JSON file.
        data (object): Data to write to the file (must be JSON serializable).
        encoding (str, optional): Encoding to use. Defaults to "utf-8".
        **json_kwargs: Additional keyword arguments for json.dump().

    Raises:
        IOError: If there is an error writing the file.
        TypeError: If the data is not JSON serializable.
    """
    with open(filepath, mode, encoding=encoding) as f:
        json.dump(data, f, **json_kwargs)


def Csv(filepath, data, mode="w", encoding="utf-8", delimiter=",", newline=""):
    """
    Saves data to a CSV file.

    Args:
        filepath (str): Path to the CSV file.
        data (list): List of rows, where each row is a list of values.
        encoding (str, optional): Encoding to use. Defaults to "utf-8".
        delimiter (str, optional): Delimiter to use. Defaults to ",".
        newline (str, optional): Newline parameter for open(). Defaults to "".

    Raises:
        IOError: If there is an error writing the file.
        csv.Error: If there is an error writing the CSV.
    """
    with open(filepath, mode, encoding=encoding, newline=newline) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(data)
