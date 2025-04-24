from loguru import logger
import sys
import os

logFilePath = os.path.join(os.getcwd(), "logs", "runningLogs.log")
logFormat = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

logger.remove()

logger.add(sys.stdout, colorize = True, format = logFormat)
logger.add(logFilePath, format = logFormat, enqueue = True, mode = "w")