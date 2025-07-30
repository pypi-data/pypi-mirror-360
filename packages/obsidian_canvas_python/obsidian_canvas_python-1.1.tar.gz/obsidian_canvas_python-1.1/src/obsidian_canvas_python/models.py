from typing import Dict, Any, Optional, Union, List
from uuid import uuid4
from .enums import Color, NodeType, Side

class CanvasObject:
    """Base class for all Obsidian Canvas elements (nodes and edges).

    Provides common attributes and abstract methods for serialization and deserialization.
    """
    _id_prefix: str = ""

    def __init__(self, obj_id: str = None, **kwargs):
        """Initializes a CanvasObject instance.

        Args:
            obj_id (str, optional): The unique ID of the object. If None, a new ID is generated.
            **kwargs: Arbitrary keyword arguments to store as raw data.
        """
        self._id = obj_id if obj_id else self._generate_id()
        self._raw_data = kwargs

    @property
    def id(self) -> str:
        """Gets the unique ID of the Canvas object.

        Returns:
            str: The object's unique ID.
        """
        return self._id

    def _generate_id(self) -> str:
        """Generates a unique ID for the Canvas object.

        The ID is prefixed with `_id_prefix` and a 16-character UUID.

        Returns:
            str: A unique ID string.
        """
        return f"{self._id_prefix}{str(uuid4())[:16]}"

    def to_dict(self) -> Dict[str, Any]:
        """Converts the object to a dictionary in Obsidian Canvas JSON format.

        This is an abstract method that must be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            Dict[str, Any]: A dictionary representation of the object.
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Creates an object instance from an Obsidian Canvas JSON dictionary.

        This is an abstract class method that must be implemented by subclasses.

        Args:
            data (Dict[str, Any]): A dictionary containing the object's data.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.

        Returns:
            CanvasObject: An instance of the CanvasObject subclass.
        """
        raise NotImplementedError

class Node(CanvasObject):
    """Represents a node element in an Obsidian Canvas.

    Nodes can be of various types (text, file, link, group) and have properties
    like position, size, color, and content.
    """
    _id_prefix: str = "node-"

    def __init__(self,
                 obj_id: str = None,
                 node_type: NodeType = NodeType.TEXT,
                 x: Union[int, float] = 0,
                 y: Union[int, float] = 0,
                 width: Union[int, float] = 250,
                 height: Union[int, float] = 60,
                 color: Optional[Color] = None,
                 text: Optional[str] = None,
                 file: Optional[str] = None,
                 url: Optional[str] = None,
                 style_attributes: Optional[Dict] = None,
                 **kwargs):
        """Initializes a Node instance.

        Args:
            obj_id (str, optional): The unique ID of the node. If None, a new ID is generated.
            node_type (NodeType): The type of the node (e.g., TEXT, FILE, LINK, GROUP).
                                  Defaults to NodeType.TEXT.
            x (Union[int, float]): The X-coordinate of the node's top-left corner. Defaults to 0.
            y (Union[int, float]): The Y-coordinate of the node's top-left corner. Defaults to 0.
            width (Union[int, float]): The width of the node. Defaults to 250.
            height (Union[int, float]): The height of the node. Defaults to 60.
            color (Color, optional): The color of the node. Defaults to Color.GRAY.
            text (str, optional): The text content for TEXT type nodes.
            file (str, optional): The file path for FILE type nodes.
            url (str, optional): The URL for LINK type nodes.
            style_attributes (Dict, optional): A dictionary of additional style attributes.
            **kwargs: Arbitrary keyword arguments to store as raw data.
        """
        super().__init__(obj_id, **kwargs)
        self.node_type = node_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color if color else Color.GRAY
        self.text = text
        self.file = file
        self.url = url
        self.style_attributes = style_attributes if style_attributes is not None else {}
        self._raw_data.update(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Node object to a dictionary in Obsidian Canvas JSON format.

        Returns:
            Dict[str, Any]: A dictionary representation of the node.
        """
        data = {
            "id": self.id,
            "type": self.node_type.value,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color.value if self.color else None,
            **self.style_attributes,
            **self._raw_data
        }
        if self.node_type == NodeType.TEXT:
            data["text"] = self.text
        elif self.node_type == NodeType.FILE:
            data["file"] = self.file
        elif self.node_type == NodeType.LINK:
            data["url"] = self.url
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Creates a Node instance from an Obsidian Canvas JSON dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing the node's data.

        Returns:
            Node: A Node instance.
        """
        node_type = NodeType(data.get("type", "text"))
        color = Color(data["color"]) if "color" in data else None

        text = data.get("text")
        file = data.get("file")
        url = data.get("url")

        known_keys = ["id", "type", "x", "y", "width", "height", "color", "text", "file", "url"]
        remaining_data = {k: v for k, v in data.items() if k not in known_keys}
        
        style_attributes = remaining_data
        
        return cls(
            obj_id=data.get("id"),
            node_type=node_type,
            x=data.get("x", 0),
            y=data.get("y", 0),
            width=data.get("width", 250),
            height=data.get("height", 60),
            color=color,
            text=text,
            file=file,
            url=url,
            style_attributes=style_attributes,
        )

class Edge(CanvasObject):
    """Represents an edge (connection) element in an Obsidian Canvas.

    Edges connect two nodes and can have properties like color and a label.
    """
    _id_prefix: str = "edge-"

    def __init__(self,
                 obj_id: str = None,
                 from_node: str = "",
                 to_node: str = "",
                 from_side: Optional[Side] = None,
                 to_side: Optional[Side] = None,
                 color: Optional[Color] = None,
                 label: Optional[str] = None,
                 style_attributes: Optional[Dict] = None,
                 **kwargs):
        """Initializes an Edge instance.

        Args:
            obj_id (str, optional): The unique ID of the edge. If None, a new ID is generated.
            from_node (str): The ID of the source node.
            to_node (str): The ID of the target node.
            from_side (Side, optional): The side of the source node the edge connects from.
            to_side (Side, optional): The side of the target node the edge connects to.
            color (Color, optional): The color of the edge. Defaults to Color.GRAY.
            label (str, optional): A text label for the edge.
            style_attributes (Dict, optional): A dictionary of additional style attributes.
            **kwargs: Arbitrary keyword arguments to store as raw data.
        """
        super().__init__(obj_id, **kwargs)
        self.from_node = from_node
        self.to_node = to_node
        self.from_side = from_side
        self.to_side = to_side
        self.color = color if color else Color.GRAY
        self.label = label
        self.style_attributes = style_attributes if style_attributes is not None else {}
        self._raw_data.update(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Edge object to a dictionary in Obsidian Canvas JSON format.

        Returns:
            Dict[str, Any]: A dictionary representation of the edge.
        """
        data = {
            "id": self.id,
            "fromNode": self.from_node,
            "toNode": self.to_node,
            "color": self.color.value if self.color else None,
            **self.style_attributes,
            **self._raw_data
        }
        if self.from_side:
            data["fromSide"] = self.from_side.value
        if self.to_side:
            data["toSide"] = self.to_side.value
        if self.label:
            data["label"] = self.label
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Creates an Edge instance from an Obsidian Canvas JSON dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing the edge's data.

        Returns:
            Edge: An Edge instance.
        """
        from_side = Side(data["fromSide"]) if "fromSide" in data else None
        to_side = Side(data["toSide"]) if "toSide" in data else None
        color = Color(data["color"]) if "color" in data else None

        known_keys = ["id", "fromNode", "toNode", "fromSide", "toSide", "color", "label"]
        remaining_data = {k: v for k, v in data.items() if k not in known_keys}
        
        style_attributes = {}
        
        return cls(
            obj_id=data.get("id"),
            from_node=data.get("fromNode"),
            to_node=data.get("toNode"),
            from_side=from_side,
            to_side=to_side,
            color=color,
            label=data.get("label"),
            style_attributes=style_attributes,
            **remaining_data
        )