
from __future__ import annotations

import sys
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

CONSOLE_LOGGER = logging.StreamHandler(stream=sys.stdout)
CONSOLE_LOGGER.setLevel(logging.INFO)
CONSOLE_LOGGER.setFormatter(
    logging.Formatter('%(levelname)-8s - %(message)s')
)

LOGGER.addHandler(CONSOLE_LOGGER)
