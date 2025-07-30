import os
import sys
import time
import logging
import datetime
from pathlib import Path

class Logger():
    """
    A custom logger class that handles log creation, daily log rotation,
    and automatic deletion of expired log files based on a defined expiration.

    Attributes:
        level (str): The logging level for the logger (e.g., 'DEBUG', 'INFO').
        console (str): The logging level for console output.
        file (str): The logging level for file output.
        root (str): The root directory where log files are stored.
        file_prefix (str): Prefix for log files.
        expired (int): Number of days after which log files are considered expired and deleted.
        namespace (str): Namespace for the logger, useful for differentiating logs in larger applications.
        location (str): Specifies whether to log the filename or pathname in the logs.
        style (str): Style of the log format, can be '[', '-', or ':'.

    Example:
        logger = Logger(level='DEBUG', console='INFO', file='ERROR', root='logs', file_prefix='app')
        logger.info("This is an info message.")
    """

    VALID_LOG_LEVELS = ['debug', 'info', 'warning', 'error', 'critical', 'exception']

    def __init__(
            self,
            level='DEBUG',
            console='',
            file='',
            root='logs',
            file_prefix='',
            expired=-1,
            namespace='',
            location='',  # 'filename' or 'pathname' or ''
            style='-'  # '[' or '-' or ':'
        ):
        self.level = level
        self.console = console.upper() if console else ''
        self.file = file.upper() if file else ''
        if file:
            self.root = root
            self.file_prefix = file_prefix + '_' if file_prefix != '' else ''
            self.expired = expired
            self.delete_expired_log()

        self.namespace = namespace

        if location and sys.version_info < (3, 8):
            # stacklevel is only supported in Python 3.8 and above
            print("Warning: 'location' parameter is only supported in Python 3.8 and above. Setting location to False.")
            self.location = ''
        elif location not in ['filename', 'pathname', '']:
            self.location = ''
        else:
            self.location = location
        
        self.style = style
        if self.style not in ['[', '-', ':']:
            print(f"Warning: Invalid style '{self.style}' provided. Defaulting to '['.")
            self.style = '['

        self.day = time.strftime('%Y-%m-%d')
        self.setup()

    def __getattr__(self, name):
        """
        Allows dynamic access to standard logging methods like debug, info, etc.
        
        Raises:
            AttributeError: If the attribute is not a recognized log level.
        """
        if name in self.VALID_LOG_LEVELS:
            def log_method(msg, *args, **kwargs):
                self.check()
                if self.location and 'stacklevel' not in kwargs:
                    # Since now the logger is a class attribute, 
                    # we need to set stacklevel to 2
                    # in order to point to the caller of the log method.
                    kwargs['stacklevel'] = 2
                getattr(self.logger, name)(msg, *args, **kwargs)
            return log_method
        raise AttributeError(f"'{name}' is not a valid logging level. Valid levels are: {', '.join(self.VALID_LOG_LEVELS)}")
 
    def setup(self):
        """
        Create or recreate the logging handlers based on the current configuration.
        This is called internally to handle log rotation.
        """
        self.shutdown()

        # create a logger obj and set level
        # use __name__ to avoid use root logger
        if self.namespace:
            if self.namespace == 'global':
                self.logger = logging.getLogger()
            else:
                self.logger = logging.getLogger(self.namespace)
        else:
            self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, self.level))
        
        # create a formatter obj and add it into the handlers
        self.formatter = logging.Formatter(self.get_format())
        self.formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        
        # create a console handler
        if self.console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.console))
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
            
        # create a file handler
        if self.file:
            if not os.path.isdir(self.root):
                os.mkdir(self.root)
            file_handler = logging.FileHandler(f"{self.root}/{self.file_prefix}{self.day}.log")
            file_handler.setLevel(getattr(logging, self.file))
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

    def get_format(self):
        """
        Returns the log format string based on the logger's configuration.
        """
        _format = []
        _format.append('%(asctime)s')
        _format.append('%(levelname)s')
        if self.location:
            # location can be 'filename', 'pathname', or ''
            # %(filename)s is the name of the file without the path
            # %(pathname)s is the full path of the file
            # %(lineno)d is the line number in the file where the log was called
            _format.append(f'%({self.location})s:%(lineno)d')
        _format.append('%(message)s')

        if self.style == '[':
            _format = [f'[{part}]' for part in _format[:-1]] + [_format[-1]]
            return ' '.join(_format)
        elif self.style == '-':
            return ' - '.join(_format)
        elif self.style == ':':
            return ':'.join(_format)
    
    def delete_expired_log(self):
        """
        Delete log files that are older than the 'expired' days setting.
        """
        if not self.file:
            return
        
        if self.expired < 0:
            return
        
        today = datetime.date.today()
        log_dir = Path(self.root)
        if not log_dir.exists():
            return

        for file_path in log_dir.iterdir():
            if file_path.suffix == '.log':
                try:
                    file_date_str = file_path.stem.split('_')[-1]
                    file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d").date()
                    if (today - file_date).days > self.expired:
                        file_path.unlink()
                        print(f'delete expired log: {file_path}', flush=True)
                except ValueError:
                    print(f"Skipped invalid log file: {file_path}", flush=True)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}", flush=True)

    def check(self):
        """
        Check if the log file needs to be rotated based on the current date.
        """
        if time.strftime('%Y-%m-%d') != self.day:
            self.day = time.strftime('%Y-%m-%d')
            self.setup()
            self.delete_expired_log()
        
    def shutdown(self):
        """
        Properly close and remove all handlers from the logger.
        """
        if not hasattr(self, 'logger'):
            return
        for handler in self.logger.handlers:
            print(handler, flush=True)
            handler.close()
            self.logger.removeHandler(handler)