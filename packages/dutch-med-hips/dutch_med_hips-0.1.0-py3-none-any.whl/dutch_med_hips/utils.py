import json
import pickle
from pathlib import Path
from typing import Union


def load_json(file_path: Union[str, Path]) -> dict:
    """
    Reads a json file and returns a dictionary.
    """
    with open(file_path, "r") as fp:
        json_dict = json.load(fp)

    return json_dict


def load_pickle(file_path: Union[str, Path]):
    """
    Reads a pickle file and returns the object.
    """
    with open(file_path, "rb") as fp:
        obj = pickle.load(fp)

    return obj
