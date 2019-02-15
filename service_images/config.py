"""
default config for the factory
"""
from pathlib import Path
import logging


class Config:
    DEBUG = __debug__          # Turns on/off debugging features in Flask
    PROCESSED_DIR_PATH = Path(__file__).parent / 'data'   # static_folder
    PROCESSED_IMAGE_FORMAT = 'png'
    LOG_PATH = PROCESSED_DIR_PATH / 'server.log'
    LOGGING_LEVEL = logging.INFO
