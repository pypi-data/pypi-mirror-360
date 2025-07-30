from enum import Enum

class Color(Enum):
    """Represents the color options available for Canvas elements."""
    GRAY = "0"
    RED = "1"
    ORANGE = "2"
    YELLOW = "3"
    GREEN = "4"
    BLUE = "5"
    PURPLE = "6"

class Range(Enum):
    """Defines the scope for search or deletion operations within the Canvas."""
    NODE = "node"
    EDGE = "edge"
    ALL = "all"

class NodeType(Enum):
    """Specifies the type of a node in the Obsidian Canvas."""
    TEXT = "text"
    FILE = "file"
    LINK = "link" # Corresponds to URL nodes
    GROUP = "group"

class Side(Enum):
    """Indicates the side of a node for edge connections."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"