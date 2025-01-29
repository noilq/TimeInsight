import os
import sys

from time_insight.logging.logger import logger

def restart_application():
    logger.info("Restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)