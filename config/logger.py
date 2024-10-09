import logging
import sys

logger = logging.getLogger()

# create formatter
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create handler
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('stock.log')

# set formatter
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add logger to handler
logger.handlers = [stream_handler, file_handler]

# set log level

logger.setLevel(logging.INFO)

