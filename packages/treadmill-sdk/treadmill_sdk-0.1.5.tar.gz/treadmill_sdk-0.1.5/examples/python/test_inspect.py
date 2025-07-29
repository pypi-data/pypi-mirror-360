from logger import getLogger
import logging
from utils import inspect_class
import treadmill_sdk

libtml = treadmill_sdk
inspect_class(treadmill_sdk)

logger = getLogger(logging.DEBUG)
logger.info(treadmill_sdk.get_sdk_version())

# logger.info(libtml.ForceLevel(1))
# logger.info(libtml.ForceLevel.Small.int_value)
