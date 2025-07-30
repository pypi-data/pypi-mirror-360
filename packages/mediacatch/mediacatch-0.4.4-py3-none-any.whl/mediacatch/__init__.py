import logging
import sys

from dotenv import load_dotenv

logging.basicConfig(
    format='[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
    datefmt='%d/%m/%Y-%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
)

load_dotenv()

__version__ = '0.4.4'
