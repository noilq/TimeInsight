import os
import logging
import logging.config
from time_insight.config import BASE_DIR

logging.config.fileConfig(os.path.join(BASE_DIR, 'time_insight', 'logging', 'logging.conf'))

logger = logging.getLogger('debugLogger')