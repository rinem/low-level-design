# console_appender.py
from log_appender import LogAppender

class ConsoleAppender(LogAppender):
    def append(self, log_message):
        print(log_message)

# database_appender.py
import psycopg2
from log_appender import LogAppender

class DatabaseAppender(LogAppender):
    def __init__(self, db_url, username, password):
        self.db_url = db_url
        self.username = username
        self.password = password
    
    def append(self, log_message):
        try:
            connection = psycopg2.connect(self.db_url, self.username, self.password)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO logs (level, message, timestamp) VALUES (%s, %s, %s)",
                           (log_message.get_level().name, log_message.get_message(), log_message.get_timestamp()))
            connection.commit()
            cursor.close()
            connection.close()
        except psycopg2.Error as e:
            print(f"Error: {e}")

# file_appender.py
from log_appender import LogAppender

class FileAppender(LogAppender):
    def __init__(self, file_path):
        self.file_path = file_path
    
    def append(self, log_message):
        with open(self.file_path, "a") as file:
            file.write(str(log_message) + "\n")

# log_appender.py
from abc import ABC, abstractmethod

class LogAppender(ABC):
    @abstractmethod
    def append(self, log_message):
        pass

# log_level.py
from enum import Enum

class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5

# log_message.py
import time

class LogMessage:
    def __init__(self, level, message):
        self.level = level
        self.message = message
        self.timestamp = int(time.time() * 1000)
    
    def get_level(self):
        return self.level
    
    def get_message(self):
        return self.message
    
    def get_timestamp(self):
        return self.timestamp
    
    def __str__(self):
        return f"[{self.level}] {self.timestamp} - {self.message}"

# logger.py
from logger_config import LoggerConfig
from log_level import LogLevel
from log_message import LogMessage
from console_appender import ConsoleAppender

class Logger:
    _instance = None
    
    def __init__(self):
        if Logger._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Logger._instance = self
            self.config = LoggerConfig(LogLevel.INFO, ConsoleAppender())
    
    @staticmethod
    def get_instance():
        if Logger._instance is None:
            Logger()
        return Logger._instance
    
    def set_config(self, config):
        self.config = config
    
    def log(self, level, message):
        if level.value >= self.config.get_log_level().value:
            log_message = LogMessage(level, message)
            self.config.get_log_appender().append(log_message)
    
    def debug(self, message):
        self.log(LogLevel.DEBUG, message)
    
    def info(self, message):
        self.log(LogLevel.INFO, message)
    
    def warning(self, message):
        self.log(LogLevel.WARNING, message)
    
    def error(self, message):
        self.log(LogLevel.ERROR, message)
    
    def fatal(self, message):
        self.log(LogLevel.FATAL, message)

# logger_config.py
class LoggerConfig:
    def __init__(self, log_level, log_appender):
        self.log_level = log_level
        self.log_appender = log_appender
    
    def get_log_level(self):
        return self.log_level
    
    def set_log_level(self, log_level):
        self.log_level = log_level
    
    def get_log_appender(self):
        return self.log_appender
    
    def set_log_appender(self, log_appender):
        self.log_appender = log_appender

# logging_framework_demo.py
from logger import Logger
from logger_config import LoggerConfig
from log_level import LogLevel
from file_appender import FileAppender

class LoggingFrameworkDemo:
    @staticmethod
    def run():
        logger = Logger.get_instance()
        
        # Logging with default configuration
        logger.info("This is an information message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        
        # Changing log level and appender
        config = LoggerConfig(LogLevel.DEBUG, FileAppender("app.log"))
        logger.set_config(config)
        
        logger.debug("This is a debug message")
        logger.info("This is an information message")

if __name__ == "__main__":
    LoggingFrameworkDemo.run()

