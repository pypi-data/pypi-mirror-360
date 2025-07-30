from typing import List, Optional, Dict, Any, Tuple
import os
from .models import Node, Edge, NodeType, Color, Side
from .enums import Range
from .parser import load_canvas_file
from .serializer import save_canvas_file
from .exceptions import (
    CanvasFileNotFoundError,
    NodeNotFoundError,
    EdgeNotFoundError,
    InvalidArgumentError,
)
from .utils import configure_logger

logger = configure_logger(__name__)

class Canvas:
    """Represents an Obsidian Canvas, providing methods to manage and manipulate its nodes and edges.

    This class serves as the primary interface for interacting with an Obsidian Canvas
    file. It allows loading, saving, adding, deleting, finding, and converting
    Canvas elements to other formats like Mermaid.
    """
    def __init__(self, file_path: Optional[str] = None):
        """Initializes a Canvas instance.

        Args:
            file_path (str, optional): The path to an existing .canvas JSON file to load.
                                       If provided, the canvas will be loaded upon initialization.
                                       Defaults to None, creating an empty canvas.
        """
        self._file_path: Optional[str] = None
        self._nodes: List[Node] = []
        self._edges: List[Edge] = []
        self._raw_canvas_data: Dict[str, Any] = {}

        if file_path:
            self.load(file_path)

    @property
    def nodes(self) -> List[Node]:
        """Gets the list of Node objects currently in the canvas.

        Returns:
            List[Node]: A list of Node objects.
        """
        return self._nodes

    @property
    def edges(self) -> List[Edge]:
        """Gets the list of Edge objects currently in the canvas.

        Returns:
            List[Edge]: A list of Edge objects.
        """
        return self._edges

    def load(self, file_path: str):
        """Loads and parses an Obsidian Canvas file into the current Canvas instance.

        Args:
            file_path (str): The path to the .canvas JSON file.

        Raises:
            CanvasFileNotFoundError: If the specified file does not exist.
            InvalidCanvasFormatError: If the file content is not valid JSON or does not conform to Canvas format.
        """
        if not os.path.exists(file_path):
            raise CanvasFileNotFoundError(f"Canvas file not found: {file_path}")
        
        self._nodes, self._edges, self._raw_canvas_data = load_canvas_file(file_path)
        self._file_path = file_path
        logger.info(f"Canvas loaded from {file_path} with {len(self._nodes)} nodes and {len(self._edges)} edges.")

    def save(self, file_path: Optional[str] = None):
        """Saves the current Canvas state to a .canvas file.

        If `file_path` is provided, the canvas will be saved to that path.
        If `file_path` is None, it will attempt to save to the path from which
        it was originally loaded.

        Args:
            file_path (str, optional): The path to save the file. If None, uses the path
                                       from which the canvas was loaded.

        Raises:
            InvalidArgumentError: If no file path is provided and the canvas was not
                                  loaded from an existing file.
            CanvasError: If there is an IOError during file writing.
        """
        target_path = file_path if file_path else self._file_path
        if not target_path:
            raise InvalidArgumentError("No file path provided for saving the canvas.")
        
        save_canvas_file(target_path, self._nodes, self._edges, self._raw_canvas_data)
        self._file_path = target_path
        logger.info(f"Canvas saved to {target_path}.")

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieves a node by its unique ID.

        Args:
            node_id (str): The unique ID of the node to retrieve.

        Returns:
            Node or None: The Node object if found, otherwise None.
        """
        return next((node for node in self._nodes if node.id == node_id), None)

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Retrieves an edge by its unique ID.

        Args:
            edge_id (str): The unique ID of the edge to retrieve.

        Returns:
            Edge or None: The Edge object if found, otherwise None.
        """
        return next((edge for edge in self._edges if edge.id == edge_id), None)

    def add_node(self, node_type: NodeType = NodeType.TEXT, **kwargs) -> Node:
        """Adds a new node to the canvas.

        A unique ID will be automatically generated for the new node.

        Args:
            node_type (NodeType): The type of the node (e.g., NodeType.TEXT, NodeType.FILE, etc.).
                                  Defaults to NodeType.TEXT.
            **kwargs: Additional attributes for the node, such as `x`, `y`, `width`, `height`,
                      `text` (for TEXT nodes), `file` (for FILE nodes), `url` (for LINK nodes),
                      `color`, and `style_attributes`.

        Returns:
            Node: The newly created Node object.
        """
        node = Node(node_type=node_type, **kwargs)
        self._nodes.append(node)
        logger.debug(f"Added node: {node.id} (Type: {node.node_type.value})")
        return node

    def add_edge(self, from_node_id: str, to_node_id: str, **kwargs) -> Edge:
        """Adds a new edge between two existing nodes.

        A unique ID will be automatically generated for the new edge.

        Args:
            from_node_id (str): The ID of the source node for the edge.
            to_node_id (str): The ID of the target node for the edge.
            **kwargs: Additional attributes for the edge, such as `color`, `label`,
                      `from_side` (Side), and `to_side` (Side).

        Returns:
            Edge: The newly created Edge object.

        Raises:
            NodeNotFoundError: If either `from_node_id` or `to_node_id` does not
                               correspond to an existing node in the canvas.
        """
        if not self.get_node(from_node_id):
            raise NodeNotFoundError(f"Source node with ID '{from_node_id}' not found.")
        if not self.get_node(to_node_id):
            raise NodeNotFoundError(f"Target node with ID '{to_node_id}' not found.")
        
        edge = Edge(from_node=from_node_id, to_node=to_node_id, **kwargs)
        self._edges.append(edge)
        logger.debug(f"Added edge: {edge.id} (From: {from_node_id}, To: {to_node_id})")
        return edge

    def delete_object(self, obj_id: str, obj_type: Range = Range.ALL) -> bool:
        """Deletes a node or an edge from the canvas.

        If a node is deleted, all associated edges connected to that node will also be deleted.

        Args:
            obj_id (str): 要删除的对象（节点或边）的 ID。
            obj_type (Range): 要删除的对象类型。
                               使用 `Range.NODE` 仅删除节点，
                               使用 `Range.EDGE` 仅删除边，
                               或 `Range.ALL`（默认）删除节点或边。

        Returns:
            bool: 如果找到对象并成功删除，则为 True，否则为 False。
        """
        deleted = False
        
        if obj_type in [Range.NODE, Range.ALL]:
            initial_node_count = len(self._nodes)
            self._nodes = [node for node in self._nodes if node.id != obj_id]
            if len(self._nodes) < initial_node_count:
                # 如果节点被删除，则同时删除所有关联的边
                initial_edge_count = len(self._edges)
                self._edges = [
                    edge for edge in self._edges
                    if edge.from_node != obj_id and edge.to_node != obj_id
                ]
                if len(self._edges) < initial_edge_count:
                    logger.debug(f"Deleted node {obj_id} and {initial_edge_count - len(self._edges)} associated edges.")
                else:
                    logger.debug(f"Deleted node {obj_id}.")
                deleted = True

        if obj_type in [Range.EDGE, Range.ALL]:
            initial_edge_count = len(self._edges)
            self._edges = [edge for edge in self._edges if edge.id != obj_id]
            if len(self._edges) < initial_edge_count:
                logger.debug(f"Deleted edge {obj_id}.")
                deleted = True
        
        return deleted

    def find_nodes(self, **criteria) -> List[Node]:
        """根据各种条件查找节点。

        Args:
            **criteria: 用于过滤节点的关键字参数。
                        支持：id、color、node_type、text_contains、file_path、url_contains、
                                   x_range（元组：(min_x, max_x)）、y_range（元组：(min_y, max_y)）。

        Returns:
            List[Node]: 匹配条件的 Node 对象列表。
        """
        results = self._nodes
        
        if "id" in criteria:
            results = [node for node in results if node.id == criteria["id"]]
        if "color" in criteria and isinstance(criteria["color"], Color):
            results = [node for node in results if node.color == criteria["color"]]
        if "node_type" in criteria and isinstance(criteria["node_type"], NodeType):
            results = [node for node in results if node.node_type == criteria["node_type"]]
        if "text_contains" in criteria and isinstance(criteria["text_contains"], str):
            search_text = criteria["text_contains"].lower()
            results = [node for node in results if node.text and search_text in node.text.lower()]
        if "file_path" in criteria and isinstance(criteria["file_path"], str):
            results = [node for node in results if node.file == criteria["file_path"]]
        if "url_contains" in criteria and isinstance(criteria["url_contains"], str):
            search_url = criteria["url_contains"].lower()
            results = [node for node in results if node.url and search_url in node.url.lower()]
        if "x_range" in criteria and isinstance(criteria["x_range"], tuple) and len(criteria["x_range"]) == 2:
            min_x, max_x = criteria["x_range"]
            results = [node for node in results if min_x <= node.x <= max_x]
        if "y_range" in criteria and isinstance(criteria["y_range"], tuple) and len(criteria["y_range"]) == 2:
            min_y, max_y = criteria["y_range"]
            results = [node for node in results if min_y <= node.y <= max_y]
            
        return results

    def find_edges(self, **criteria) -> List[Edge]:
        """根据各种条件查找边。

        Args:
            **criteria: 用于过滤边的关键字参数。
                        支持：id、color、label_contains、from_node_id、to_node_id。

        Returns:
            List[Edge]: 匹配条件的 Edge 对象列表。
        """
        results = self._edges

        if "id" in criteria:
            results = [edge for edge in results if edge.id == criteria["id"]]
        if "color" in criteria and isinstance(criteria["color"], Color):
            results = [edge for edge in results if edge.color == criteria["color"]]
        if "label_contains" in criteria and isinstance(criteria["label_contains"], str):
            search_label = criteria["label_contains"].lower()
            results = [edge for edge in results if edge.label and search_label in edge.label.lower()]
        if "from_node_id" in criteria:
            results = [edge for edge in results if edge.from_node == criteria["from_node_id"]]
        if "to_node_id" in criteria:
            results = [edge for edge in results if edge.to_node == criteria["to_node_id"]]
            
        return results

    def to_mermaid(self) -> str:
        """将画布转换为 Mermaid 图形语法字符串。

        目前支持 'graph TD'（从上到下）方向。

        Returns:
            str: Mermaid 图形语法字符串。
        """
        mermaid_lines = ["graph TD"]
        
        # 添加节点
        for node in self._nodes:
            node_label = ""
            if node.node_type == NodeType.TEXT:
                node_label = node.text if node.text else f"Node {node.id}"
            elif node.node_type == NodeType.FILE:
                node_label = os.path.basename(node.file) if node.file else f"File {node.id}"
            elif node.node_type == NodeType.LINK:
                node_label = node.url if node.url else f"Link {node.id}"
            elif node.node_type == NodeType.GROUP:
                node_label = f"Group {node.id}" # Groups are not directly represented as nodes in Mermaid
            
            # 为 Mermaid 转义双引号
            node_label = node_label.replace('"', '"')

            if node.node_type != NodeType.GROUP:
                mermaid_lines.append(f'    {node.id}["{node_label}"]')

        # 添加边
        for edge in self._edges:
            edge_label = ""
            if edge.label:
                edge_label = f"""|"{edge.label.replace('"', '"')}"|"""
            # Mermaid 边语法: from_node -->|label| to_node
            mermaid_lines.append(f"    {edge.from_node} -->{edge_label} {edge.to_node}")
            
        return "\n".join(mermaid_lines)
