import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout,level='DEBUG')

database_path = r"D:\sync\dev\database.db"
