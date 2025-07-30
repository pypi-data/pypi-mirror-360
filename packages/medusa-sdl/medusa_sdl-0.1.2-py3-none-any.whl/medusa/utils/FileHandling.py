from typing import Union, List, Dict
from pathlib import Path
import json


def load_json(file: Path) -> Union[Dict, List]:
    """
    Loads a json file and returns the contained data (dictionary / list).

    Args:
        file (Path): Path to the json file to be loaded.

    Returns:
        Union[Dict, List]: The data contained in the json file.
    """
    with open(file, "r") as f:
        data = json.load(f)

    return data


def save_json(data: Union[Dict, List], file: Path) -> None:
    """
    Saves a dictionary or list to a json file.

    Args:
        data (Union[Dict, List]): The data to be saved.
        file (Path): The path to the json file to be saved.
    """
    with open(file, "w") as f:
        json.dump(data, f, indent=2)
