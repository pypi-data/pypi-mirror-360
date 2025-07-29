from datetime import datetime

from bconsole import ColoredFileLogger

logger = ColoredFileLogger.from_path(f"logs/{datetime.now().strftime('%Y-%m-%d')}.log")

logger.verbose("This is a verbose message.")
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.log("This is also an info message.", level="info")
logger.warning("This is a warning message.")

try:
    raise Warning("This is also a warning message.")
except Warning as w:
    logger.warning(w)

logger.error("This is an error message.")

try:
    raise Exception("This is also an error message.")
except Exception as e:
    logger.error(e)

logger.critical("This is a critical message.")

logger.close()
