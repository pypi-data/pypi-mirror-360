""" This module contains utility functions for the modelhub package. """

# Use logger from autonomize-core
from autonomize.utils.logger import setup_logger

from .encoder import encode_file

__all__ = ["setup_logger", "encode_file"]
