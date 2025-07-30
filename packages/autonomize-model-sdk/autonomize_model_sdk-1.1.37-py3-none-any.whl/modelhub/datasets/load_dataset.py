""" This module contains the function to load a dataset from the ModelHub dataset client. """

from typing import Dict, Optional, Union

from datasets import DatasetDict

from ..clients import DatasetClient


def load_dataset(
    name: str,
    version: Optional[int] = None,
    split: Optional[str] = None,
    directory: Optional[str] = None,
) -> Union[DatasetDict, Dict[str, DatasetDict]]:
    """
    Load a dataset from the ModelHub dataset client.

    Args:
        name (str): The name of the dataset.
        version (Optional[int], optional): The version of the dataset. Defaults to None.
        split (Optional[str], optional): The split of the dataset. If None, all splits will be loaded. Defaults to None.
        directory (Optional[str], optional): The directory path to the dataset. Defaults to None.

    Returns:
        Union[DatasetDict, Dict[str, DatasetDict]]:
        The loaded dataset or a dictionary of datasets if loading all folders.
    """
    client = DatasetClient()

    return client.load_dataset(
        dataset_name=name, version=version, split=split, directory=directory
    )


def list_datasets():
    """
    List all datasets in the ModelHub dataset client.

    Returns:
        List[Dict[str, Any]]: A list of datasets.
    """
    client = DatasetClient()

    return client.list_datasets()
