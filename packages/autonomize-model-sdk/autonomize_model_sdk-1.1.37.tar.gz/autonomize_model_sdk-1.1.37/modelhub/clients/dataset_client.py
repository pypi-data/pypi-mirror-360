import io
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import numpy as np
from datasets import Dataset, DatasetDict, Features, Image, Value, load_dataset
from PIL import Image as PILImage

from ..core import BaseClient
from ..utils import setup_logger

logger = setup_logger(__name__)


class DatasetClient(BaseClient):
    """Client for interacting with datasets."""

    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all available datasets.

        Returns:
            List[Dict[str, Any]]: A list of available datasets.
        """
        response = self.get("datasets")
        return response["data"]

    def get_dataset_by_name(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get a dataset by name.

        Args:
            dataset_name (str): The name of the dataset.

        Returns:
            Dict[str, Any]: The dataset.
        """
        response = self.get(f"datasets/{dataset_name}")
        return response["data"]

    def get_dataset_versions(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a specific dataset.

        Args:
            dataset_id (str): The ID of the dataset.

        Returns:
            List[Dict[str, Any]]: A list of dataset versions.
        """
        response = self.get(f"datasets/{dataset_id}")
        return response["data"]["versions"]

    def get_signed_url(
        self,
        dataset_id: str,
        file_path: str,
        version: Optional[int],
        is_read: bool = True,
    ) -> str:
        """
        Get a signed URL for a file.

        Args:
            file_path (str): The path to the file.
            is_read (bool): Whether the URL is for reading. Defaults to True.
            dataset_id (str): The ID of the dataset.
            version (int): The version of the file.

        Returns:
            str: The signed URL.
        """
        body = {"file_path": file_path}
        if version:
            body["version"] = version

        endpoint = (
            f"datasets/{dataset_id}/signedurl/read"
            if is_read
            else f"datasets/{dataset_id}/signedurl/upload"
        )
        response = self.post(endpoint, json=body)
        return response["data"]["signedUrl"]

    def load_dataset(
        self,
        dataset_name: str,
        version: Optional[int] = None,
        split: Optional[str] = None,
        directory: Optional[str] = None,
    ) -> DatasetDict:
        """
        Load a dataset by name and version.

        Args:
            dataset_name (str): The name of the dataset.
            version (int, optional): The version of the dataset. Defaults to None.
            split (str, optional): The split of the dataset. Defaults to None.
            directory (str, optional): The directory path to the dataset. Defaults to None.

        Returns:
            DatasetDict: The loaded dataset.
        """
        dataset = self.get_dataset_by_name(dataset_name)
        versions = dataset["versions"]
        if version:
            version_data = next(
                (v for v in versions if v["version_id"] == version), None
            )
        else:
            version_data = versions[0]  # Default to latest version

        if not version_data:
            raise ValueError(f"Version {version} not found for dataset {dataset_name}.")

        # Check for nested directories
        nested_directories = self._check_nested_directories(version_data["files"])
        if nested_directories and not directory:
            raise ValueError(
                f"Multiple nested directories found: {nested_directories}. "
                f"Please specify a directory path."
            )

        # Collect file URLs and determine splits
        split_file_urls = self._collect_split_file_urls(
            dataset["id"], version_data["files"], split=split, directory=directory
        )

        logger.info("split_file_urls %s", split_file_urls)
        # Load dataset using the `datasets` library
        return self._load_dataset_by_format(split_file_urls)

    def _load_dataset_by_format(
        self, split_file_urls: Dict[str, List[str]]
    ) -> DatasetDict:
        """
        Load a dataset from file URLs, determining the format and handling nested paths.

        Args:
            split_file_urls (Dict[str, List[str]]):
            A dictionary where keys are split names and values are lists of file URLs.

        Returns:
            DatasetDict: The loaded dataset.
        """
        data_files = split_file_urls
        file_extensions = [
            self.get_file_extension(file)
            for files in split_file_urls.values()
            for file in files
        ]

        # Determine the dataset format based on file extensions
        if all(ext == ".csv" for ext in file_extensions):
            return load_dataset("csv", data_files=data_files)
        elif all(ext == ".json" for ext in file_extensions):
            return load_dataset("json", data_files=data_files)
        elif all(ext == ".parquet" for ext in file_extensions):
            return load_dataset("parquet", data_files=data_files)
        elif all(ext == ".txt" for ext in file_extensions):
            return load_dataset("text", data_files=data_files)
        elif all(ext in [".png", ".jpg", ".jpeg"] for ext in file_extensions):
            # For image datasets, actually load the images
            logger.info("Loading image dataset...")
            return self._load_image_dataset(split_file_urls)
        elif any(
            ext not in [".csv", ".json", ".parquet", ".txt", ".png", ".jpg", ".jpeg"]
            for ext in file_extensions
        ):
            # Check for any unsupported format before falling back to mixed format handler
            unsupported = next(
                ext
                for ext in file_extensions
                if ext
                not in [".csv", ".json", ".parquet", ".txt", ".png", ".jpg", ".jpeg"]
            )
            raise ValueError(f"Unsupported file format: {unsupported}")
        else:
            # Handle mixed formats or unsupported formats
            from datasets import Dataset

            datasets_dict = {}
            for split_name, urls in split_file_urls.items():
                datasets_dict[split_name] = Dataset.from_dict({"file_path": urls})

            return DatasetDict(datasets_dict)

    def _load_image_dataset(self, split_file_urls: Dict[str, List[str]]) -> DatasetDict:
        """
        Load image dataset by actually fetching and decoding the images.

        Args:
            split_file_urls (Dict[str, List[str]]): A dictionary mapping split names to lists of image URLs.

        Returns:
            DatasetDict: Dataset containing the loaded images.
        """
        datasets_dict = {}

        for split_name, urls in split_file_urls.items():
            logger.info(f"Loading {len(urls)} images for split {split_name}")

            # Create a features object for the image dataset
            features = Features({"image": Image(), "file_path": Value("string")})

            # Load the actual images
            images = []
            file_paths = []

            for url in urls:
                try:
                    # Fetch the image data using the inherited httpx client
                    response = self.client.get(url)
                    response.raise_for_status()

                    # Create a PIL image from the response content
                    img = PILImage.open(io.BytesIO(response.content))

                    # Convert to RGB if the image has an alpha channel
                    if img.mode == "RGBA":
                        img = img.convert("RGB")

                    # Append the image and path to their respective lists
                    images.append(img)
                    file_paths.append(url)

                except Exception as e:
                    logger.error(f"Error loading image from {url}: {e}")

            # Create a dataset from the loaded images
            dataset = Dataset.from_dict(
                {"image": images, "file_path": file_paths}, features=features
            )

            datasets_dict[split_name] = dataset

        return DatasetDict(datasets_dict)

    def _collect_split_file_urls(
        self,
        dataset_id: str,
        files: List[Dict[str, Any]],
        split: Optional[str],
        directory: Optional[str],
    ) -> Dict[str, List[str]]:
        """
        Collect file URLs categorized by splits based on folder names.

        Args:
            dataset_id (str): The ID of the dataset.
            files (List[Dict[str, Any]]): List of file metadata.
            split (str, optional): The split of the dataset. Defaults to None.
            directory (str, optional): The directory path to the dataset. Defaults to None.

        Returns:
            Dict[str, List[str]]: A dictionary where keys are split names and values are lists of file URLs.
        """
        split_file_urls = {}
        for file in files:
            file_path = file["file_path"]
            if directory and not file_path.startswith(directory):
                continue

            # Extract the split name from the file path
            path_parts = file_path.split("/")
            split_name = path_parts[-2] if directory else path_parts[-3]

            if split and split != split_name:
                continue

            if split_name not in split_file_urls:
                split_file_urls[split_name] = []
            logger.info("file %s", file)
            split_file_urls[split_name].append(
                self.get_signed_url(
                    dataset_id, file["file_path"], version=file["version_id"]
                )
            )

        if split and split not in split_file_urls:
            raise ValueError(f"Split {split} not found in the dataset.")

        return split_file_urls

    def _check_nested_directories(self, files: List[Dict[str, Any]]) -> List[str]:
        """
        Check for nested directories up to the split level. Args:
            files (List[Dict[str, Any]]): List of file metadata. Returns:
            List[str]: A list of nested directories.
        """
        nested_directories = set()
        for file in files:
            nested_directory = "/".join(file["file_path"].split("/")[:-2])
            if nested_directory:
                nested_directories.add(nested_directory)
        return list(nested_directories)

    def get_file_extension(self, file_url: str) -> str:
        """
        Extract the file extension from a URL.

        Args:
            file_url (str): The file URL.

        Returns:
            str: The file extension.
        """
        path = urlparse(file_url).path
        return os.path.splitext(path)[1].lower()  # Convert to lowercase for consistency
