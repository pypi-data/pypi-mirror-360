"""
PDF utility functions for ModelhubModelService.
"""

import logging
from io import BytesIO
from typing import List, Union

from PIL import Image

logger = logging.getLogger("modelhub.serving.pdf_utils")

# Try to import PyMuPDF, an optional dependency
try:
    import fitz

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF (fitz) is not available. PDF processing will be limited.")


def pdf2image(
    byte_stream: bytes, return_image: bool = False, zoom: int = 1
) -> List[Union[bytes, "Image.Image"]]:
    """
    Convert a PDF byte stream to images.

    Args:
        byte_stream (bytes): The PDF as bytes
        return_image (bool): If True, return PIL Image objects, otherwise return PNG bytes
        zoom (int): Zoom factor for rendering (higher values = better quality but larger images)

    Returns:
        List[Union[bytes, Image.Image]]: List of images (as bytes or PIL Image objects)
    """
    if not PYMUPDF_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) is required for PDF processing")

    result = []

    # Open the PDF from the byte stream
    with fitz.open(stream=byte_stream, filetype="pdf") as doc:
        # Process each page
        for page_num in range(doc.page_count):
            page = doc[page_num]
            # Create a matrix for higher quality rendering
            matrix = fitz.Matrix(zoom, zoom)
            # Render the page to a pixmap
            pixmap = page.get_pixmap(matrix=matrix)
            # Convert to PNG bytes
            png_bytes = pixmap.tobytes()

            if return_image:
                # Convert PNG bytes to PIL Image if requested
                try:
                    image = Image.open(BytesIO(png_bytes))
                    result.append(image)
                except ImportError:
                    logger.warning(
                        "PIL is required for return_image=True. Returning bytes instead."
                    )
                    result.append(png_bytes)
            else:
                result.append(png_bytes)

    return result
