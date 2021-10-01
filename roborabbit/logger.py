import logging
import os

logging.basicConfig(level=str(os.getenv('loglevel', 'info')).upper())
logger = logging.getLogger(__name__)
