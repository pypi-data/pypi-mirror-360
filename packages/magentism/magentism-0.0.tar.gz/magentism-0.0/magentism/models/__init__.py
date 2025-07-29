from ormantism import connect
connect("sqlite://:memory:")


import logging
from colorlog import ColoredFormatter

# Create a colored formatter
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(name)-32s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Get the root logger
root_logger = logging.getLogger()

# Ensure the root logger has no handlers to avoid duplicate messages
root_logger.handlers.clear()

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Add the formatter to the console handler
console_handler.setFormatter(formatter)

# Add the console handler to the root logger
root_logger.addHandler(console_handler)

# Set the logging level for the root logger
root_logger.setLevel(logging.DEBUG)
