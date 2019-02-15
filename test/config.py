from pathlib import Path
import logging

class Config:
    TESTING = True
    TEST_PATH = Path(__file__).parent
    PROCESSED_DIR_PATH = TEST_PATH / 'images_out'
    LOG_PATH = TEST_PATH / 'server.log'
    LOGGING_LEVEL = logging.DEBUG
