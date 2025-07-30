""" This module contains utility functions for encoding files. """

import base64


def encode_file(file_path):
    """Encode the contents of a file in Base64."""
    with open(file_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode("utf-8")
    return encoded
