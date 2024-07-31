import sys
from os import path
import logging


sys.path.append(path.join(path.dirname(__file__), '../../app'))
logging.basicConfig(level=logging.DEBUG)
