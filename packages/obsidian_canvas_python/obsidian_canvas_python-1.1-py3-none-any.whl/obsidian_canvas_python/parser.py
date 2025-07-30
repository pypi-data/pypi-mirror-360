import json
from typing import Dict, Any, List, Tuple
from .models import Node, Edge
from .exceptions import InvalidCanvasFormatError, CanvasFileNotFoundError

def parse_canvas_json(json_data: Dict[str, Any]) -> Tuple[List[Node], List[Edge], Dict[str, Any]]:
    """
    Parses a dictionary representing Obsidian Canvas JSON data into Node and Edge objects.

    Args:
        json_data: A dictionary containing the Canvas JSON data.

    Returns:
        A tuple containing:
            - A list of Node objects.
            - A list of Edge objects.
            - A dictionary of raw canvas data (excluding 'nodes' and 'edges').

    Raises:
        InvalidCanvasFormatError: If the JSON data is missing 'nodes' or 'edges' keys.
    """
    if "nodes" not in json_data or "edges" not in json_data:
        raise InvalidCanvasFormatError("Canvas JSON data must contain 'nodes' and 'edges' keys.")

    nodes = [Node.from_dict(node_data) for node_data in json_data["nodes"]]
    edges = [Edge.from_dict(edge_data) for edge_data in json_data["edges"]]

    raw_canvas_data = {k: v for k, v in json_data.items() if k not in ["nodes", "edges"]}

    return nodes, edges, raw_canvas_data

def load_canvas_file(file_path: str) -> Tuple[List[Node], List[Edge], Dict[str, Any]]:
    """
    Loads and parses an Obsidian Canvas file from the given file path.

    Args:
        file_path: The path to the .canvas JSON file.

    Returns:
        A tuple containing:
            - A list of Node objects.
            - A list of Edge objects.
            - A dictionary of raw canvas data (excluding 'nodes' and 'edges').

    Raises:
        CanvasFileNotFoundError: If the specified file does not exist.
        InvalidCanvasFormatError: If the file content is not valid JSON or does not conform to Canvas format.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return parse_canvas_json(json_data)
    except FileNotFoundError:
        raise CanvasFileNotFoundError(f"Canvas file not found at: {file_path}")
    except json.JSONDecodeError as e:
        raise InvalidCanvasFormatError(f"Invalid JSON format in canvas file: {e}")
    except Exception as e:
        raise InvalidCanvasFormatError(f"Error parsing canvas file: {e}")
