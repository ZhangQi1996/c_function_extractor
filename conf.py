import os
import sys

ROOT_PATH = root_path = os.path.abspath(os.path.dirname(__file__))

# log
LOG_STREAM = sys.stderr
LOG_LEVEL = 'INFO'
LOG_FMT = '%(asctime)s [%(levelname)s] %(message)s'
LOG_DATE_FMT = '%Y-%m-%d %H:%M:%S'

ENCODING = 'utf-8'
