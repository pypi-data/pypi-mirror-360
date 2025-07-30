import logging

def get_logger(name="app"):
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

# Create default logger instance for direct impor
logger = get_logger()

