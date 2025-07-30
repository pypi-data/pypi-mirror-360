class CanvasError(Exception):
    """Base exception for obsidian_canvas_python."""
    pass

class CanvasFileNotFoundError(CanvasError):
    """Raised when the specified canvas file is not found."""
    pass

class InvalidCanvasFormatError(CanvasError):
    """Raised when the canvas JSON format is invalid or does not conform to the Canvas specification."""
    pass

class NodeNotFoundError(CanvasError):
    """Raised when a specified node is not found."""
    pass

class EdgeNotFoundError(CanvasError):
    """Raised when a specified edge is not found."""
    pass

class InvalidArgumentError(CanvasError):
    """Raised when a method receives an invalid argument."""
    pass