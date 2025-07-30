import logging
import os


app_logger = None


def get_innermost_package(pathname):
    """
    Extracts the innermost package name from the file path.
    """
    # Convert path to module-like structure (remove .py and split by os separators)
    path_parts = os.path.normpath(pathname).split(os.sep)
    # Find the deepest package by looking for a folder structure before the filename
    if len(path_parts) > 1:
        return path_parts[-2]  # Second-last element is usually the package name
    return "(no package)"  # If there's no deeper package structure


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Extract innermost package from pathname
        record.innermost_package = get_innermost_package(record.pathname)
        return super().format(record)
    

def setup_logging_to_file(filename):
    global app_logger
    logger = logging.getLogger('customInfoLogger')
    logger.setLevel(logging.INFO)  # Set to capture info and above levels
    # Ensure the filename ends with ".log"
    if not filename.endswith(".log"):
        filename = f"{filename}.log"
    # Create and configure the file handler
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(pathname)s - %(funcName)s- %(message)s')
    file_handler.setFormatter(formatter)
    # Add the file handler to the logger
    logger.addHandler(file_handler)
    # Update the global logger variable
    app_logger = logger


def setup_basic_logging():
    formatter = CustomFormatter("[%(asctime)s] %(levelname)s in %(innermost_package)s.%(module)s (%(lineno)s): %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def get_logger():
    global app_logger
    if app_logger is None:
        # If the global logger hasn't been set up, set up basic logging and return a default logger
        setup_basic_logging()
        app_logger = logging.getLogger(__name__)
    return app_logger

get_logger()
