import uuid
import logging

def generate_unique_id() -> str:
    """Generates a unique, short ID for Canvas objects.

    This function uses UUID4 to generate a universally unique identifier,
    then truncates it to 16 characters for brevity, as commonly seen in
    Obsidian Canvas IDs.

    Returns:
        str: A 16-character unique ID string.
    """
    return str(uuid.uuid4())[:16]

def configure_logger(name: str = "obsidian_canvas_python", level=logging.INFO):
    """Configures the logger for the obsidian_canvas_python library.

    This function sets up a basic console logger if one is not already configured
    for the given name. It ensures that log messages from the library are
    properly formatted and displayed.

    Args:
        name (str): The name of the logger to configure. Defaults to "obsidian_canvas_python".
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
                     Defaults to logging.INFO.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to ch
        ch.setFormatter(formatter)

        # Add ch to logger
        logger.addHandler(ch)
    return logger
