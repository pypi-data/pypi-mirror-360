"""
KServe model service implementations for ModelHub.
"""

import importlib  # Add importlib for the _try_import_pdf2image method
import logging
import os
from io import BytesIO
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import pandas as pd
from kserve import InferRequest, InferResponse, Model

from modelhub.clients import MLflowClient
from modelhub.core.credential import ModelhubCredential

# Try importing optional dependencies
try:
    import mlflow.transformers  # pylint: disable=unused-import

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modelhub.serving")


class ModelhubModelService(Model):
    """
    Base class for KServe model services using models tracked in ModelHub/MLflow.

    This class provides the foundation for serving models tracked with ModelHub SDK.
    Projects can extend this class to add custom preprocessing/postprocessing logic.

    Attributes:
        name (str): The name of the model service.
        run_uri (str): The MLflow run URI for the model.
        model_type (str): The type of model (pyfunc, transformer, etc.).
        loaded_model (Any): The loaded model object.
        ready (bool): Whether the model is loaded and ready for serving.
    """

    def __init__(
        self,
        name: str,
        run_uri: str,
        model_type: str = "pyfunc",
        modelhub_base_url: Optional[str] = None,
    ):
        """
        Initialize the model service.

        Args:
            name (str): The name of the model service.
            run_uri (str): The MLflow run URI (e.g., "runs:/abc123/model").
            model_type (str, optional): The type of model. Defaults to "pyfunc".
            modelhub_base_url (str, optional): The base URL for ModelHub. If not provided,
                                              it will be read from the MODELHUB_BASE_URL
                                              environment variable.
        """
        super().__init__(name)
        self.name = name
        self.run_uri = run_uri
        self.model_type = model_type
        self.modelhub_base_url = modelhub_base_url or os.getenv("MODELHUB_BASE_URL")

        if not self.modelhub_base_url:
            raise ValueError("MODELHUB_BASE_URL environment variable is required")

        credential = ModelhubCredential()

        self.client = MLflowClient(
            credential=credential,
            client_id=os.getenv("CLIENT_ID"),
            copilot_id=os.getenv("COPILOT_ID"),
        )
        self.loaded_model = None
        self.ready = False

        logger.info(
            "Initialized ModelhubModelService: %s (run_uri: %s, type: %s)",
            name,
            run_uri,
            model_type,
        )

    def load(self):
        """
        Load the model from MLflow.

        This method loads the model from MLflow based on the run_uri and model_type.
        """
        logger.info("Loading model from run URI: %s", self.run_uri)

        try:
            if self.model_type == "pyfunc":
                self.loaded_model = self.client.mlflow.pyfunc.load_model(self.run_uri)
                logger.info("Loaded model as PyFunc")
            elif self.model_type == "transformer":
                if not TRANSFORMERS_AVAILABLE:
                    logger.error("mlflow.transformers is not available")
                    raise ImportError(
                        "mlflow.transformers is required for transformer models"
                    )
                self.loaded_model = self.client.mlflow.transformers.load_model(
                    self.run_uri
                )
                logger.info("Loaded model as Transformer")
            elif self.model_type == "sklearn":
                self.loaded_model = self.client.mlflow.sklearn.load_model(self.run_uri)
                logger.info("Loaded model as scikit-learn model")
            else:
                # Default to pyfunc for custom models
                self.loaded_model = self.client.mlflow.pyfunc.load_model(self.run_uri)
                logger.info(
                    "Loaded model as custom type (%s) using PyFunc", self.model_type
                )

            self.ready = True
            logger.info("Model loaded successfully")
        except Exception as exc:
            logger.error("Error loading model: %s", str(exc))
            raise

    # pylint: disable=too-many-return-statements
    async def predict(
        self,
        payload: Union[Dict, InferRequest],
        headers: Dict[str, str] = None,
        response_headers: Dict[str, str] = None,
    ) -> Union[Dict, InferResponse, AsyncIterator[Any]]:
        """
        Make predictions with the loaded model.

        This method processes the input request and makes predictions using the loaded model.
        It detects the type of input and routes to the appropriate prediction method.

        Args:
            payload (Dict[str, Any]): The prediction request data.
            headers (Dict[str, str], optional): HTTP headers for the request.
            response_headers (Dict[str, str], optional): HTTP headers for the response.

        Returns:
            Dict[str, Any]: The prediction response with status code and data.
        """
        if not self.ready:
            return {"statusCode": 503, "message": "Model is not loaded yet"}

        try:
            # Route to appropriate handler based on input type
            if "text" in payload:
                return await self.predict_text(payload, headers)
            if "data" in payload:
                return await self.predict_tabular(payload, headers)
            if "image" in payload:
                return await self.predict_image(payload, headers)
            if "pdf_file" in payload:
                return await self.predict_pdf(payload, headers)
            if "images" in payload:
                return await self.predict_images(payload, headers)
            # Default to raw prediction for any other input
            return await self.predict_raw(payload, headers)

        except Exception as exc:  # pylint: disable=broad-except
            # This broad exception is justified as we need to catch all errors in prediction
            logger.error("Error during prediction: %s", str(exc))
            return {
                "statusCode": 400,
                "message": f"Error during prediction: {str(exc)}",
            }

    async def predict_text(
        self,
        request: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """
        Process text input for prediction.

        Args:
            request (Dict[str, Any]): The prediction request with text data.
            headers (Dict[str, str], optional): HTTP headers for the request.

        Returns:
            Dict[str, Any]: The prediction response.
        """
        text_input = request.get("text")
        if not text_input:
            return {"statusCode": 400, "message": "Missing 'text' field in request"}

        logger.info("Processing text input: %s...", text_input[:100])

        prediction = self.loaded_model.predict(text_input)

        return {"statusCode": 200, "data": prediction}

    async def predict_tabular(
        self,
        request: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """
        Process tabular data for prediction.

        Args:
            request (Dict[str, Any]): The prediction request with tabular data.
            headers (Dict[str, str], optional): HTTP headers for the request.

        Returns:
            Dict[str, Any]: The prediction response.
        """
        data = request.get("data")
        if not data:
            return {"statusCode": 400, "message": "Missing 'data' field in request"}

        logger.info(
            "Processing tabular data with shape: %s",
            len(data) if isinstance(data, list) else 1,
        )

        # Convert to DataFrame if it's a list
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])

        prediction = self.loaded_model.predict(df)

        # Convert to serializable format
        if isinstance(prediction, pd.DataFrame):
            result = prediction.to_dict(orient="records")
        elif isinstance(prediction, pd.Series):
            # Series doesn't support the 'orient' parameter for to_dict
            result = prediction.to_dict()
        elif hasattr(prediction, "tolist"):
            result = prediction.tolist()
        else:
            result = prediction

        return {"statusCode": 200, "data": result}

    async def predict_image(
        self,
        request: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """
        Process a single image for prediction.

        Args:
            request (Dict[str, Any]): The prediction request with image data.
            headers (Dict[str, str], optional): HTTP headers for the request.

        Returns:
            Dict[str, Any]: The prediction response.
        """
        image_data = request.get("image")
        if not image_data:
            return {"statusCode": 400, "message": "Missing 'image' field in request"}

        logger.info("Processing image input")

        try:
            # Create a DataFrame with the image data
            df = pd.DataFrame({"image": [image_data]})

            # Make prediction
            prediction = self.loaded_model.predict(df)

            return {"statusCode": 200, "data": prediction}

        except Exception as exc:  # pylint: disable=broad-except
            # This exception must be caught to provide a meaningful error message
            logger.error("Error processing image: %s", str(exc))
            return {"statusCode": 400, "message": f"Error processing image: {str(exc)}"}

    async def predict_images(
        self,
        request: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """
        Process multiple images for prediction.

        Args:
            request (Dict[str, Any]): The prediction request with a list of images.
            headers (Dict[str, str], optional): HTTP headers for the request.

        Returns:
            Dict[str, Any]: The prediction response.
        """
        images = request.get("images", [])
        if not images:
            return {
                "statusCode": 400,
                "message": "Missing or empty 'images' field in request",
            }

        logger.info("Processing %s images", len(images))

        try:
            # Process each image to get binary data if needed
            img_byte_arr_list = []

            for image in images:
                # Convert the image to binary data if it's a PIL Image
                if hasattr(image, "save"):
                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format="PNG")
                    img_byte_arr_list.append(img_byte_arr.getvalue())
                else:
                    # Assume it's already binary data
                    img_byte_arr_list.append(image)

            # Create a DataFrame with the image data
            df = pd.DataFrame({"image": img_byte_arr_list})

            # Make prediction
            prediction = self.loaded_model.predict(df)

            return {"statusCode": 200, "data": prediction}

        except Exception as exc:  # pylint: disable=broad-except
            # This exception handling is needed to provide user-friendly error messages
            logger.error("Error processing images: %s", str(exc))
            return {
                "statusCode": 400,
                "message": f"Error processing images: {str(exc)}",
            }

    def _try_import_pdf2image(self):
        """Helper method to try importing custom pdf2image function."""
        # First try to import pdf_utils module using importlib
        try:
            pdf_utils = importlib.import_module("modelhub.serving.pdf_utils")
            return pdf_utils.pdf2image
        except ImportError:
            # Fall back to direct implementation if PyMuPDF is available
            try:
                # pylint: disable=import-outside-toplevel
                from modelhub.serving.pdf_utils import PYMUPDF_AVAILABLE

                if PYMUPDF_AVAILABLE:
                    from modelhub.serving.pdf_utils import pdf2image

                    return pdf2image
                return None
            except ImportError:
                return None

    async def predict_pdf(
        self,
        request: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """
        Process a PDF file for prediction.

        Args:
            request (Dict[str, Any]): The prediction request with PDF file data.
            headers (Dict[str, str], optional): HTTP headers for the request.

        Returns:
            Dict[str, Any]: The prediction response.
        """
        pdf_file = request.get("pdf_file")
        if not pdf_file:
            return {"statusCode": 400, "message": "Missing 'pdf_file' field in request"}

        logger.info("Processing PDF input")

        try:
            # Try to get pdf2image function
            pdf2image_func = self._try_import_pdf2image()
            if pdf2image_func is None:
                return {
                    "statusCode": 400,
                    "message": "PyMuPDF (fitz) is required for PDF processing",
                }

            # Convert PDF to images using our custom function
            images = pdf2image_func(byte_stream=pdf_file, return_image=True, zoom=2)
            if not images:
                return {
                    "statusCode": 400,
                    "message": "Failed to extract images from PDF",
                }

            logger.info("Converted PDF to %s images", len(images))

            # Process images
            img_byte_arr_list = []
            for image in images:
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format="PNG")
                img_byte_arr_list.append(img_byte_arr.getvalue())

            # Create a DataFrame with the image data
            df = pd.DataFrame({"image": img_byte_arr_list})

            # Make prediction
            prediction = self.loaded_model.predict(df)

            return {"statusCode": 200, "data": prediction}

        except Exception as exc:  # pylint: disable=broad-except
            # This exception handling is required to report PDF-specific errors
            logger.error("Error processing PDF: %s", str(exc))
            return {"statusCode": 400, "message": f"Error processing PDF: {str(exc)}"}

    async def predict_raw(
        self,
        request: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """
        Process raw input for prediction.

        Args:
            request (Dict[str, Any]): The raw prediction request.
            headers (Dict[str, str], optional): HTTP headers for the request.

        Returns:
            Dict[str, Any]: The prediction response.
        """
        logger.info("Processing raw input")

        prediction = self.loaded_model.predict(request)

        return {"statusCode": 200, "data": prediction}


class ImageModelService(ModelhubModelService):
    """
    Specialized model service for image-based models.

    This service extends ModelhubModelService to provide specific
    functionality for models that process images or PDFs.
    """

    def __init__(
        self, name: str, run_uri: str, modelhub_base_url: Optional[str] = None
    ):
        """Initialize the image model service."""
        super().__init__(name, run_uri, "pyfunc", modelhub_base_url)

    def _process_pdf(self, pdf_data):
        """Process PDF data into images."""
        pdf2image_func = self._try_import_pdf2image()
        if pdf2image_func is None:
            raise ImportError("PyMuPDF (fitz) is required for PDF processing")
        return pdf2image_func(byte_stream=pdf_data, return_image=True, zoom=2)

    async def predict(
        self,
        payload: Union[Dict, InferRequest],
        headers: Dict[str, str] = None,
        response_headers: Dict[str, str] = None,
    ) -> Union[Dict, InferResponse, AsyncIterator[Any]]:
        """
        Process the prediction request for images or PDFs.

        Args:
            payload (Dict[str, Any]): The prediction request with image or PDF data.
            headers (Dict[str, str], optional): HTTP headers for the request.
            response_headers (Dict[str, str], optional): HTTP headers for the request.

        Returns:
            Dict[str, Any]: The prediction response.
        """
        if not self.ready:
            return {"statusCode": 503, "message": "Model is not loaded yet"}

        try:
            # Handle different input types
            pdf_file = payload.get("pdf_file")
            images = payload.get("images", [])

            img_byte_arr_list = []

            # Process PDF if provided
            if pdf_file:
                try:
                    pdf_images = self._process_pdf(pdf_file)
                    logger.info("Converted PDF to %s images", len(pdf_images))
                    images.extend(pdf_images)
                except ImportError as exc:
                    logger.error("PDF processing error: %s", str(exc))
                    return {
                        "statusCode": 400,
                        "message": "PyMuPDF (fitz) is required for PDF processing",
                    }
                except Exception as exc:  # pylint: disable=broad-except
                    # This broad exception is needed to handle various PDF processing errors
                    logger.error("PDF processing error: %s", str(exc))
                    return {
                        "statusCode": 400,
                        "message": f"Error processing PDF: {str(exc)}",
                    }

            # Process each image
            for image in images:
                # Convert the image to binary data if it's a PIL Image
                if hasattr(image, "save"):
                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format="PNG")
                    img_byte_arr = img_byte_arr.getvalue()
                else:
                    # Assume it's already binary data
                    img_byte_arr = image

                # Append the binary data to the list
                img_byte_arr_list.append(img_byte_arr)

            # Create a DataFrame with the binary data
            input_df = pd.DataFrame({"image": img_byte_arr_list})

            # Make prediction
            prediction = self.loaded_model.predict(input_df)

            return {"statusCode": 200, "data": prediction}

        except Exception as exc:  # pylint: disable=broad-except
            # General exception handling for the predict method
            logger.error("Error during prediction: %s", str(exc))
            return {
                "statusCode": 400,
                "message": f"Error during prediction: {str(exc)}",
            }


class ModelServiceGroup:
    """
    Group multiple model services together.

    This class helps manage multiple model services that need to be
    loaded and served together.

    Attributes:
        models (List[ModelhubModelService]): List of model services in the group.
    """

    def __init__(self, models: List[ModelhubModelService]):
        """
        Initialize the model service group.

        Args:
            models (List[ModelhubModelService]): List of model services to group.
        """
        self.models = models

    def load_models(self):
        """Load all models in the group."""
        for model in self.models:
            model.load()
