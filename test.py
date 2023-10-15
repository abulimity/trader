from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout)
logger.level("foobar", no=33, icon="🤖", color="<blue>")

logger.log("foobar", "A message")