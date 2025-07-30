"""Client for interacting with inference endpoints."""

import mimetypes
import os
from typing import Any, BinaryIO, Dict, Optional, Tuple, Union
from urllib.parse import urlparse

import httpx

from modelhub.core import ModelHubAPIException

from ..core import BaseClient
from ..utils import setup_logger

logger = setup_logger(__name__)


class InferenceClient(BaseClient):
    """Client for running inference on deployed models."""

    def run_text_inference(
        self, model_name: str, text: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run text-based inference on a deployed model.

        Args:
            model_name (str): The name of the model to use for inference.
            text (str): The text input for the model.
            parameters (Dict[str, Any], optional): Additional parameters for inference. Defaults to None.

        Returns:
            Dict[str, Any]: The inference results.

        Raises:
            ModelHubAPIException: If the inference request fails.
        """
        logger.info("Running text inference on model: %s", model_name)

        payload = {"text": text, "parameters": parameters or {}}

        try:
            endpoint = f"model-card/{model_name}/predict"
            response = self.post(endpoint, json=payload)
            logger.debug("Text inference completed successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"Text inference failed: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    def _is_url(self, file_path: str) -> bool:
        """Check if a path is a URL.

        Args:
            file_path (str): The file path to check

        Returns:
            bool: True if the path is a URL, False otherwise
        """
        return file_path.startswith(
            ("http://", "https://", "s3://", "wasbs://", "azure://")
        )

    def _process_file(
        self,
        file_path: Union[str, BinaryIO],
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Tuple[str, bytes, str]:
        """Process a file and return its name, content and content type.

        Args:
            file_path (Union[str, BinaryIO]): The file path, URL or file-like object
            file_name (Optional[str]): The filename to use (required for file objects)
            content_type (Optional[str]): The content type (will be guessed if not provided)

        Returns:
            Tuple[str, bytes, str]: A tuple of (filename, file content, content type)

        Raises:
            ModelHubAPIException: If there are errors processing the file
        """
        # Handle string paths (local files or URLs)
        if isinstance(file_path, str):
            if self._is_url(file_path):
                logger.debug("Handling URL as file source: %s", file_path)
                # Extract filename from URL if not provided
                if not file_name:
                    parsed_url = urlparse(file_path)
                    basename = os.path.basename(parsed_url.path)
                    file_name = basename if basename else "file"

                # Download the file content
                # For http/https URLs, use httpx
                if file_path.startswith(("http://", "https://")):
                    try:
                        download_response = httpx.get(
                            file_path, timeout=self.timeout, follow_redirects=True
                        )
                        download_response.raise_for_status()
                        file_content = download_response.content
                        # Try to get content type from response
                        if (
                            not content_type
                            and "Content-Type" in download_response.headers
                        ):
                            content_type = download_response.headers["Content-Type"]
                    except httpx.HTTPError as e:
                        raise ModelHubAPIException(
                            f"Failed to download file from URL: {e}"
                        ) from e
                # For other URL schemes
                else:
                    raise ModelHubAPIException(
                        f"Unsupported URL scheme in {file_path}. Currently supported: http://, https://"
                    )
            else:
                # Local file path
                if not os.path.exists(file_path):
                    raise ModelHubAPIException(f"File not found: {file_path}")
                file_name = file_name or os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    file_content = f.read()
        else:
            # File-like object
            if not file_name:
                raise ModelHubAPIException(
                    "file_name is required when file_path is a file-like object"
                )
            file_content = file_path.read() if hasattr(file_path, "read") else file_path

        # Determine content type if not provided
        if not content_type:
            content_type = (
                mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            )

        return file_name, file_content, content_type

    def run_file_inference(
        self,
        model_name: str,
        file_path: Union[str, BinaryIO],
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run file-based inference on a deployed model.

        Args:
            model_name (str): The name of the model to use for inference.
            file_path (Union[str, BinaryIO]): The path to the file, \
            a file-like object, or a URL (http/https/s3/azure).
            file_name (str, optional): The name of the file. \
            Required if file_path is a file-like object. Defaults to None.
            content_type (str, optional): The content type of the file. \
            If not provided, it will be guessed. Defaults to None.

        Returns:
            Dict[str, Any]: The inference results.

        Raises:
            ModelHubAPIException: If the inference request fails or file handling errors occur.
        """
        logger.info("Running file inference on model: %s", model_name)

        try:
            # Process the file to get filename, content and type
            file_name, file_content, content_type = self._process_file(
                file_path, file_name, content_type
            )

            # Prepare multipart/form-data request
            files = {"file": (file_name, file_content, content_type)}

            endpoint = f"model-card/{model_name}/predict/file"

            # Use BaseClient post method with files parameter
            result = self.post(endpoint, files=files)
            logger.debug("File inference completed successfully")
            return result

        except httpx.HTTPError as e:
            error_msg = f"File inference failed: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        except Exception as e:
            error_msg = f"File inference error: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    # Async version of text inference
    async def arun_text_inference(
        self, model_name: str, text: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run text-based inference asynchronously on a deployed model.

        Args:
            model_name (str): The name of the model to use for inference.
            text (str): The text input for the model.
            parameters (Dict[str, Any], optional): Additional parameters for inference. Defaults to None.

        Returns:
            Dict[str, Any]: The inference results.

        Raises:
            ModelHubAPIException: If the inference request fails.
        """
        logger.info("Running async text inference on model: %s", model_name)

        payload = {"text": text, "parameters": parameters or {}}

        try:
            endpoint = f"model-card/{model_name}/predict"
            response = await self.apost(endpoint, json=payload)
            logger.debug("Async text inference completed successfully")
            return response
        except httpx.RequestError as e:
            error_msg = f"Async text inference failed: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e

    # Async version of file processing
    async def _aprocess_file(
        self,
        file_path: Union[str, BinaryIO],
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Tuple[str, bytes, str]:
        """Process a file asynchronously and return its name, content and content type.

        Args:
            file_path (Union[str, BinaryIO]): The file path, URL or file-like object
            file_name (Optional[str]): The filename to use (required for file objects)
            content_type (Optional[str]): The content type (will be guessed if not provided)

        Returns:
            Tuple[str, bytes, str]: A tuple of (filename, file content, content type)

        Raises:
            ModelHubAPIException: If there are errors processing the file
        """
        # Handle string paths (local files or URLs)
        if isinstance(file_path, str):
            if self._is_url(file_path):
                logger.debug("Handling URL as file source (async): %s", file_path)
                # Extract filename from URL if not provided
                if not file_name:
                    parsed_url = urlparse(file_path)
                    basename = os.path.basename(parsed_url.path)
                    file_name = basename if basename else "file"

                # Download the file content
                # For http/https URLs, use httpx
                if file_path.startswith(("http://", "https://")):
                    try:
                        async with httpx.AsyncClient(follow_redirects=True) as client:
                            download_response = await client.get(
                                file_path, timeout=self.timeout
                            )
                            download_response.raise_for_status()
                            file_content = download_response.content
                            # Try to get content type from response
                            if (
                                not content_type
                                and "Content-Type" in download_response.headers
                            ):
                                content_type = download_response.headers["Content-Type"]
                    except httpx.HTTPError as e:
                        raise ModelHubAPIException(
                            f"Failed to download file from URL: {e}"
                        ) from e
                # For other URL schemes
                else:
                    raise ModelHubAPIException(
                        f"Unsupported URL scheme in {file_path}. Currently supported: http://, https://"
                    )
            else:
                # Local file path
                if not os.path.exists(file_path):
                    raise ModelHubAPIException(f"File not found: {file_path}")
                file_name = file_name or os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    file_content = f.read()
        else:
            # File-like object
            if not file_name:
                raise ModelHubAPIException(
                    "file_name is required when file_path is a file-like object"
                )
            file_content = file_path.read() if hasattr(file_path, "read") else file_path

        # Determine content type if not provided
        if not content_type:
            content_type = (
                mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            )

        return file_name, file_content, content_type

    # Async version of file inference
    async def arun_file_inference(
        self,
        model_name: str,
        file_path: Union[str, BinaryIO],
        file_name: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run file-based inference asynchronously on a deployed model.

        Args:
            model_name (str): The name of the model to use for inference.
            file_path (Union[str, BinaryIO]): The path to the file, a file-like object, or a URL.
            file_name (str, optional): The name of the file. Required if file_path is a file-like object.
            content_type (str, optional): The content type of the file. Will be guessed if not provided.

        Returns:
            Dict[str, Any]: The inference results.

        Raises:
            ModelHubAPIException: If the inference request fails or file handling errors occur.
        """
        logger.info("Running async file inference on model: %s", model_name)

        try:
            # Process the file to get filename, content and type
            file_name, file_content, content_type = await self._aprocess_file(
                file_path, file_name, content_type
            )

            # Prepare multipart/form-data request
            files = {"file": (file_name, file_content, content_type)}

            endpoint = f"model-card/{model_name}/predict/file"

            # Use BaseClient's async post method with files parameter
            result = await self.apost(endpoint, files=files)
            logger.debug("Async file inference completed successfully")
            return result

        except httpx.HTTPError as e:
            error_msg = f"Async file inference failed: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
        except Exception as e:
            error_msg = f"Async file inference error: {str(e)}"
            logger.error(error_msg)
            raise ModelHubAPIException(error_msg) from e
