import logging
import os

parent_dir = os.path.split(os.path.split(__file__)[0])[0]
logs_dir = os.path.join(parent_dir, 'logs')
if not os.path.isdir(logs_dir):
    os.mkdir(logs_dir)

log_file = os.path.join(logs_dir, 'main.log')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
