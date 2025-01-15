import os
import sys
import logging
import logging.config
from time_insight.config import BASE_DIR

if getattr(sys, 'frozen', False):
    #builded version
    config_path = os.path.join(sys._MEIPASS, 'time_insight', 'logging', 'logging.conf')
else:
    #not builded version
    config_path = os.path.join(BASE_DIR, 'time_insight', 'logging', 'logging.conf')

logging.config.fileConfig(config_path)

logger = logging.getLogger('debugLogger')