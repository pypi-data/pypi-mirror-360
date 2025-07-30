"""
utils.py

Shared helpers for loading files, handling errors, etc.
"""

import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
