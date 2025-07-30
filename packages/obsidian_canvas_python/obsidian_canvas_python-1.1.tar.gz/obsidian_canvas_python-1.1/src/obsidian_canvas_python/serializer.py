import json
from typing import Dict, Any, List
from .models import Node, Edge
from .exceptions import CanvasError # Using a more general CanvasError for IOError

def serialize_canvas_objects(nodes: List[Node], edges: List[Edge], raw_canvas_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializes lists of Node and Edge objects into a dictionary representing Obsidian Canvas JSON data.

    Args:
        nodes: A list of Node objects.
        edges: A list of Edge objects.
        raw_canvas_data: A dictionary of raw canvas data (excluding 'nodes' and 'edges') to be included.

    Returns:
        A dictionary containing the complete Canvas JSON data.
    """
    serialized_nodes = [node.to_dict() for node in nodes]
    serialized_edges = [edge.to_dict() for edge in edges]

    canvas_data = raw_canvas_data.copy()
    canvas_data["nodes"] = serialized_nodes
    canvas_data["edges"] = serialized_edges

    return canvas_data

def save_canvas_file(file_path: str, nodes: List[Node], edges: List[Edge], raw_canvas_data: Dict[str, Any]) -> None:
    """
    Saves lists of Node and Edge objects and raw canvas data to an Obsidian Canvas file.

    Args:
        file_path: The path to the .canvas JSON file where the data will be saved.
        nodes: A list of Node objects.
        edges: A list of Edge objects.
        raw_canvas_data: A dictionary of raw canvas data (excluding 'nodes' and 'edges') to be included.

    Raises:
        CanvasError: If there is an IOError during file writing.
    """
    canvas_data = serialize_canvas_objects(nodes, edges, raw_canvas_data)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(canvas_data, f, indent=4)
    except IOError as e:
        raise CanvasError(f"Error saving canvas file to {file_path}: {e}")
