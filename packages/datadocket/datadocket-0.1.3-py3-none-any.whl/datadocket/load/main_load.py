import json
import csv

def Txt(filepath, mode="r", encoding="utf-8", split=False):
    """
    Loads the contents of a text file.

    Args:
        filepath (str): Path to the text file.
        mode (str, optional): reading mode. Default is "r"
        encoding (str, optional): Encoding to use. Defaults to "utf-8".
        split (bool, optional): Wether to split the text by linebreaks. If True returns a list. Default is False

    Returns:
        str: Contents of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
    """
    data = ""
    with open(filepath, mode, encoding=encoding) as f:
        data = f.read()
    
    if split:
        data = data.split("\n")
        data = [item.strip() for item in data]

    return data


def Json(filepath, mode="r", encoding="utf-8"):
    """
    Loads the contents of a JSON file.

    Args:
        filepath (str): Path to the JSON file.
        encoding (str, optional): Encoding to use. Defaults to "utf-8".

    Returns:
        object: The parsed JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(filepath, mode, encoding=encoding) as f:
        return json.load(f)


def Csv(filepath, mode="r", encoding="utf-8", delimiter=","):
    """
    Loads the contents of a CSV file.

    Args:
        filepath (str): Path to the CSV file.
        encoding (str, optional): Encoding to use. Defaults to "utf-8".
        delimiter (str, optional): Delimiter to use. Defaults to ",".

    Returns:
        list: List of rows, where each row is a list of values.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
        csv.Error: If there is an error parsing the CSV.
    """

    with open(filepath, mode, encoding=encoding, newline='') as f:
        reader = csv.reader(f, delimiter=delimiter)
        return [row for row in reader]
