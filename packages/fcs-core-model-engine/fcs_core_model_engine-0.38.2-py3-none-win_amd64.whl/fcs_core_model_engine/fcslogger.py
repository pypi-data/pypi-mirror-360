
import logging
import os
from sys import platform
import datetime

from .fcsoptions import StatusMessageType

class DiagnosticLog:
    def __init__(self, log_level: StatusMessageType, log_msg: str):
        self.log_level = log_level.value
        self.log_msg = log_msg

class FCSLogger:
    """
    Class used for logging for all FCS operations.
    """
    def __init__(self, user_id: str, path_to_log_file: str, show_debug_logs: bool=True):
        self.logger = logging.getLogger(f'fcs_{user_id}')
        
        shared_debug_level = logging.INFO
        if show_debug_logs:
            shared_debug_level = logging.DEBUG
        self.logger.setLevel(shared_debug_level)

        self.path_to_log_file = path_to_log_file
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(shared_debug_level)
        self.stream_handler.setFormatter(formatter)
        self.logger.addHandler(self.stream_handler)

        try:
            self.file_handler = logging.FileHandler(self.path_to_log_file)
            self.file_handler.setLevel(shared_debug_level)
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)
        except Exception as ex:
            self.wrn(f"Failed to add FileHandler that should write out logs to {self.path_to_log_file}. Reason: {ex.args}")

    def set_logging_context(self, context_name: str) -> None:
        """The logging may refer to a custom addin. If so, we want to indicate that these logging messages
        come from inside plugin.

        Args:
            context_name (str): Name of the application.
        """

        formatter = logging.Formatter(f"{context_name} - %(asctime)s - %(levelname)s - %(message)s")
        self.stream_handler.setFormatter(formatter)
        self.file_handler.setFormatter(formatter)

    def get_log_file_path(self) -> str:
        """Returns path to log file.
        """
        return self.path_to_log_file

    def log(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.info(clean_message)

    def dbg(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.debug(clean_message)

    def wrn(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.warn(clean_message)

    def err(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.error(clean_message)

    def fatal(self, message: str):
        """These should be errors that indicate the binary backend 
        failed or created unexpected results.
        """
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.critical(clean_message)

def create_generic_logger(logging_directory: str, name_of_logger: str, show_debug_logs: bool=True) -> FCSLogger:
    """This type of logging is not user bound.

    Returns:
        FCSLogger: logging class
    """
    if not os.path.exists(logging_directory):
        raise Exception(f'Provided directory for logging that does not exist!')

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path_to_log_file = os.path.join(logging_directory, f'{name_of_logger}_{timestamp}.log')
    return FCSLogger(name_of_logger, path_to_log_file, show_debug_logs)

