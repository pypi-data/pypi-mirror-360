import pytest
import json
import os
from obsidian_canvas_python import (
    Canvas,
    Color,
    Range,
    NodeType,
    Side,
    CanvasError,
    CanvasFileNotFoundError,
    InvalidCanvasFormatError,
    NodeNotFoundError,
    EdgeNotFoundError,
    InvalidArgumentError,
)
from obsidian_canvas_python.models import Node, Edge
from obsidian_canvas_python.parser import parse_canvas_json, load_canvas_file
from obsidian_canvas_python.serializer import serialize_canvas_objects, save_canvas_file
from obsidian_canvas_python.utils import generate_unique_id

# --- Test Enums ---
def test_color_enum():
    assert Color.GRAY.value == "0"
    assert Color.RED.value == "1"

def test_range_enum():
    assert Range.NODE.value == "node"
    assert Range.ALL.value == "all"

def test_nodetype_enum():
    assert NodeType.TEXT.value == "text"
    assert NodeType.FILE.value == "file"
    assert NodeType.LINK.value == "link"
    assert NodeType.GROUP.value == "group"

def test_side_enum():
    assert Side.TOP.value == "top"
    assert Side.BOTTOM.value == "bottom"

# --- Test CanvasObject (Base Class) ---
def test_canvas_object_id_generation():
    obj = Node() # Using Node as a concrete CanvasObject for testing
    assert obj.id.startswith("node-")
    assert len(obj.id) == len("node-") + 16

def test_canvas_object_custom_id():
    obj = Node(obj_id="my-custom-id")
    assert obj.id == "my-custom-id"


# --- Test Node ---
def test_node_creation_defaults():
    node = Node()
    assert node.node_type == NodeType.TEXT
    assert node.x == 0
    assert node.y == 0
    assert node.width == 250
    assert node.height == 60
    assert node.color == Color.GRAY
    assert node.text is None
    assert node.file is None
    assert node.url is None
    assert node.style_attributes == {}

def test_node_creation_with_args():
    node = Node(
        node_type=NodeType.FILE,
        x=100, y=200, width=300, height=150,
        color=Color.BLUE,
        file="path/to/file.md",
        style_attributes={"font": "Arial"}
    )
    assert node.node_type == NodeType.FILE
    assert node.x == 100
    assert node.y == 200
    assert node.width == 300
    assert node.height == 150
    assert node.color == Color.BLUE
    assert node.file == "path/to/file.md"
    assert node.style_attributes == {"font": "Arial"}
    assert node.text is None
    assert node.url is None

def test_node_to_dict_text_type():
    node = Node(text="Hello World")
    data = node.to_dict()
    assert data["type"] == "text"
    assert data["text"] == "Hello World"
    assert "file" not in data
    assert "url" not in data

def test_node_to_dict_file_type():
    node = Node(node_type=NodeType.FILE, file="my_note.md")
    data = node.to_dict()
    assert data["type"] == "file"
    assert data["file"] == "my_note.md"
    assert "text" not in data
    assert "url" not in data

def test_node_to_dict_link_type():
    node = Node(node_type=NodeType.LINK, url="https://example.com")
    data = node.to_dict()
    assert data["type"] == "link"
    assert data["url"] == "https://example.com"
    assert "text" not in data
    assert "file" not in data

def test_node_to_dict_with_style_attributes():
    node = Node(text="Styled Node", style_attributes={"font": "Arial", "fontSize": 16})
    data = node.to_dict()
    assert data["text"] == "Styled Node"
    assert data["font"] == "Arial"
    assert data["fontSize"] == 16

def test_node_from_dict_text_type():
    data = {
        "id": "node-123", "type": "text", "x": 10, "y": 20, "width": 100, "height": 50,
        "color": "1", "text": "Test Text Node", "font": "Verdana"
    }
    node = Node.from_dict(data)
    assert node.id == "node-123"
    assert node.node_type == NodeType.TEXT
    assert node.x == 10
    assert node.y == 20
    assert node.width == 100
    assert node.height == 50
    assert node.color == Color.RED
    assert node.text == "Test Text Node"
    assert node.style_attributes == {"font": "Verdana"}

def test_node_from_dict_file_type():
    data = {
        "id": "node-456", "type": "file", "x": 10, "y": 20, "width": 100, "height": 50,
        "file": "another_note.md"
    }
    node = Node.from_dict(data)
    assert node.node_type == NodeType.FILE
    assert node.file == "another_note.md"

def test_node_from_dict_link_type():
    data = {
        "id": "node-789", "type": "link", "x": 10, "y": 20, "width": 100, "height": 50,
        "url": "https://obsidian.md"
    }
    node = Node.from_dict(data)
    assert node.node_type == NodeType.LINK
    assert node.url == "https://obsidian.md"

# --- Test Edge ---
def test_edge_creation_defaults():
    edge = Edge(from_node="nodeA", to_node="nodeB")
    assert edge.from_node == "nodeA"
    assert edge.to_node == "nodeB"
    assert edge.from_side is None
    assert edge.to_side is None
    assert edge.color == Color.GRAY
    assert edge.label is None
    assert edge.style_attributes == {}

def test_edge_creation_with_args():
    edge = Edge(
        from_node="nodeX", to_node="nodeY",
        from_side=Side.TOP, to_side=Side.BOTTOM,
        color=Color.GREEN, label="Connects X to Y",
        style_attributes={"lineStyle": "dashed"}
    )
    assert edge.from_node == "nodeX"
    assert edge.to_node == "nodeY"
    assert edge.from_side == Side.TOP
    assert edge.to_side == Side.BOTTOM
    assert edge.color == Color.GREEN
    assert edge.label == "Connects X to Y"
    assert edge.style_attributes == {"lineStyle": "dashed"}

def test_edge_to_dict():
    edge = Edge(
        obj_id="edge-123", from_node="n1", to_node="n2",
        from_side=Side.LEFT, to_side=Side.RIGHT,
        color=Color.ORANGE, label="Flow",
        style_attributes={"thickness": 2}
    )
    data = edge.to_dict()
    assert data["id"] == "edge-123"
    assert data["fromNode"] == "n1"
    assert data["toNode"] == "n2"
    assert data["fromSide"] == "left"
    assert data["toSide"] == "right"
    assert data["color"] == "2"
    assert data["label"] == "Flow"
    assert data["thickness"] == 2

def test_edge_from_dict():
    data = {
        "id": "edge-456", "fromNode": "n3", "toNode": "n4",
        "fromSide": "top", "toSide": "bottom", "color": "4", "label": "Dependency"
    }
    edge = Edge.from_dict(data)
    assert edge.id == "edge-456"
    assert edge.from_node == "n3"
    assert edge.to_node == "n4"
    assert edge.from_side == Side.TOP
    assert edge.to_side == Side.BOTTOM
    assert edge.color == Color.GREEN
    assert edge.label == "Dependency"

# --- Test Parser ---
@pytest.fixture
def sample_canvas_json_data():
    return {
        "nodes": [
            {"id": "node-1", "type": "text", "x": 0, "y": 0, "width": 100, "height": 50, "text": "Node 1"},
            {"id": "node-2", "type": "file", "x": 100, "y": 100, "width": 120, "height": 60, "file": "file.md"}
        ],
        "edges": [
            {"id": "edge-1", "fromNode": "node-1", "toNode": "node-2"}
        ],
        "metadata": {"version": 1},
        "other_root_prop": "value"
    }

def test_parse_canvas_json(sample_canvas_json_data):
    nodes, edges, raw_data = parse_canvas_json(sample_canvas_json_data)
    assert len(nodes) == 2
    assert isinstance(nodes[0], Node)
    assert nodes[0].id == "node-1"
    assert nodes[0].text == "Node 1"
    assert len(edges) == 1
    assert isinstance(edges[0], Edge)
    assert edges[0].id == "edge-1"
    assert raw_data == {"metadata": {"version": 1}, "other_root_prop": "value"}

def test_parse_canvas_json_missing_keys():
    with pytest.raises(InvalidCanvasFormatError):
        parse_canvas_json({"nodes": []}) # Missing edges
    with pytest.raises(InvalidCanvasFormatError):
        parse_canvas_json({"edges": []}) # Missing nodes

@pytest.fixture
def temp_canvas_file(tmp_path, sample_canvas_json_data):
    file_path = tmp_path / "test_canvas.canvas"
    with open(file_path, "w") as f:
        json.dump(sample_canvas_json_data, f)
    return file_path

def test_load_canvas_file(temp_canvas_file):
    nodes, edges, raw_data = load_canvas_file(temp_canvas_file)
    assert len(nodes) == 2
    assert len(edges) == 1
    assert raw_data == {"metadata": {"version": 1}, "other_root_prop": "value"}

def test_load_canvas_file_not_found():
    with pytest.raises(CanvasFileNotFoundError):
        load_canvas_file("non_existent_file.canvas")

def test_load_canvas_file_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.canvas"
    file_path.write_text("this is not json")
    with pytest.raises(InvalidCanvasFormatError):
        load_canvas_file(file_path)

# --- Test Serializer ---
def test_serialize_canvas_objects(sample_canvas_json_data):
    nodes, edges, raw_data = parse_canvas_json(sample_canvas_json_data)
    serialized_data = serialize_canvas_objects(nodes, edges, raw_data)
    
    assert "nodes" in serialized_data
    assert "edges" in serialized_data
    assert len(serialized_data["nodes"]) == 2
    assert len(serialized_data["edges"]) == 1
    assert serialized_data["metadata"] == {"version": 1}
    assert serialized_data["other_root_prop"] == "value"
    assert serialized_data["nodes"][0]["id"] == "node-1"
    assert serialized_data["edges"][0]["id"] == "edge-1"

def test_save_canvas_file(tmp_path, sample_canvas_json_data):
    nodes, edges, raw_data = parse_canvas_json(sample_canvas_json_data)
    output_file = tmp_path / "output_canvas.canvas"
    save_canvas_file(output_file, nodes, edges, raw_data)
    
    assert output_file.exists()
    with open(output_file, "r") as f:
        loaded_data = json.load(f)
    
    assert loaded_data["nodes"][0]["id"] == "node-1"
    assert loaded_data["edges"][0]["id"] == "edge-1"
    assert loaded_data["metadata"] == {"version": 1}

# --- Test Canvas Class ---
@pytest.fixture
def empty_canvas():
    return Canvas()

@pytest.fixture
def populated_canvas(temp_canvas_file):
    return Canvas(file_path=temp_canvas_file)

def test_canvas_init_empty():
    canvas = Canvas()
    assert len(canvas.nodes) == 0
    assert len(canvas.edges) == 0

def test_canvas_init_with_file(temp_canvas_file):
    canvas = Canvas(file_path=temp_canvas_file)
    assert len(canvas.nodes) == 2
    assert len(canvas.edges) == 1
    assert canvas.nodes[0].id == "node-1"

def test_canvas_load(empty_canvas, temp_canvas_file):
    empty_canvas.load(temp_canvas_file)
    assert len(empty_canvas.nodes) == 2
    assert len(empty_canvas.edges) == 1

def test_canvas_load_non_existent_file(empty_canvas):
    with pytest.raises(CanvasFileNotFoundError):
        empty_canvas.load("non_existent.canvas")

def test_canvas_save(populated_canvas, tmp_path):
    new_file_path = tmp_path / "saved_canvas.canvas"
    populated_canvas.save(new_file_path)
    assert new_file_path.exists()
    
    loaded_canvas = Canvas(file_path=new_file_path)
    assert len(loaded_canvas.nodes) == 2
    assert len(loaded_canvas.edges) == 1

def test_canvas_save_no_path_provided_and_not_loaded(empty_canvas):
    with pytest.raises(InvalidArgumentError):
        empty_canvas.save()

def test_canvas_get_node(populated_canvas):
    node = populated_canvas.get_node("node-1")
    assert node is not None
    assert node.text == "Node 1"
    assert populated_canvas.get_node("non-existent-node") is None

def test_canvas_get_edge(populated_canvas):
    edge = populated_canvas.get_edge("edge-1")
    assert edge is not None
    assert edge.from_node == "node-1"
    assert populated_canvas.get_edge("non-existent-edge") is None

def test_canvas_add_node(empty_canvas):
    node = empty_canvas.add_node(node_type=NodeType.TEXT, text="New Node")
    assert len(empty_canvas.nodes) == 1
    assert node.text == "New Node"
    assert empty_canvas.get_node(node.id) == node

def test_canvas_add_edge(populated_canvas):
    node3 = populated_canvas.add_node(node_type=NodeType.TEXT, text="Node 3")
    edge = populated_canvas.add_edge(from_node_id="node-1", to_node_id=node3.id, label="New Edge")
    assert len(populated_canvas.edges) == 2
    assert edge.label == "New Edge"
    assert populated_canvas.get_edge(edge.id) == edge

def test_canvas_add_edge_node_not_found(empty_canvas):
    with pytest.raises(NodeNotFoundError):
        empty_canvas.add_edge(from_node_id="non-existent", to_node_id="another-non-existent")
    empty_canvas.add_node(obj_id="n1")
    with pytest.raises(NodeNotFoundError):
        empty_canvas.add_edge(from_node_id="n1", to_node_id="non-existent")

def test_canvas_delete_node(populated_canvas):
    assert populated_canvas.get_node("node-1") is not None
    assert populated_canvas.get_edge("edge-1") is not None # Edge connected to node-1

    deleted = populated_canvas.delete_object("node-1", obj_type=Range.NODE)
    assert deleted is True
    assert populated_canvas.get_node("node-1") is None
    assert populated_canvas.get_edge("edge-1") is None # Associated edge should be deleted

    # Try deleting non-existent node
    deleted = populated_canvas.delete_object("non-existent", obj_type=Range.NODE)
    assert deleted is False

def test_canvas_delete_edge(populated_canvas):
    assert populated_canvas.get_edge("edge-1") is not None
    deleted = populated_canvas.delete_object("edge-1", obj_type=Range.EDGE)
    assert deleted is True
    assert populated_canvas.get_edge("edge-1") is None

    # Try deleting non-existent edge
    deleted = populated_canvas.delete_object("non-existent", obj_type=Range.EDGE)
    assert deleted is False

def test_canvas_delete_all_type(populated_canvas):
    # Add a new node and edge to ensure there are multiple objects
    node3 = populated_canvas.add_node(obj_id="node-3", text="Node 3")
    edge2 = populated_canvas.add_edge(obj_id="edge-2", from_node_id="node-1", to_node_id="node-3")

    # Delete node-1 (and its associated edges)
    deleted = populated_canvas.delete_object("node-1", obj_type=Range.ALL)
    assert deleted is True
    assert populated_canvas.get_node("node-1") is None
    assert populated_canvas.get_edge("edge-1") is None # original edge
    assert populated_canvas.get_edge("edge-2") is None # newly added edge

    # Delete node-3 (no associated edges left)
    deleted = populated_canvas.delete_object("node-3", obj_type=Range.ALL)
    assert deleted is True
    assert populated_canvas.get_node("node-3") is None

    # Delete non-existent object
    deleted = populated_canvas.delete_object("non-existent", obj_type=Range.ALL)
    assert deleted is False

def test_canvas_find_nodes(populated_canvas):
    # Add more nodes for comprehensive testing
    populated_canvas.add_node(node_type=NodeType.TEXT, text="Another Text Node", color=Color.BLUE, x=50, y=50)
    populated_canvas.add_node(node_type=NodeType.LINK, url="http://test.com", x=150, y=150)

    # Find by type
    text_nodes = populated_canvas.find_nodes(node_type=NodeType.TEXT)
    assert len(text_nodes) == 2 # Original node-1 and "Another Text Node"
    assert all(node.node_type == NodeType.TEXT for node in text_nodes)

    # Find by color
    blue_nodes = populated_canvas.find_nodes(color=Color.BLUE)
    assert len(blue_nodes) == 1
    assert blue_nodes[0].text == "Another Text Node"

    # Find by text_contains
    found_nodes = populated_canvas.find_nodes(text_contains="node")
    assert len(found_nodes) == 2 # "Node 1" and "Another Text Node"

    # Find by x_range
    x_range_nodes = populated_canvas.find_nodes(x_range=(0, 50))
    assert len(x_range_nodes) == 2 # node-1 (x=0) and "Another Text Node" (x=50)

    # Combined criteria
    combined_nodes = populated_canvas.find_nodes(node_type=NodeType.TEXT, text_contains="node", color=Color.BLUE)
    assert len(combined_nodes) == 1
    assert combined_nodes[0].text == "Another Text Node"

def test_canvas_find_edges(populated_canvas):
    # Add more edges for comprehensive testing
    populated_canvas.add_node(obj_id="node-3", text="Node 3")
    populated_canvas.add_node(obj_id="node-4", text="Node 4")
    populated_canvas.add_edge(from_node_id="node-1", to_node_id="node-3", label="Edge A", color=Color.RED)
    populated_canvas.add_edge(from_node_id="node-2", to_node_id="node-4", label="Edge B", color=Color.BLUE)

    # Find by from_node_id
    edges_from_node1 = populated_canvas.find_edges(from_node_id="node-1")
    assert len(edges_from_node1) == 2 # original edge-1 and "Edge A"

    # Find by label_contains
    found_edges = populated_canvas.find_edges(label_contains="edge")
    assert len(found_edges) == 2 # "Edge A" and "Edge B"

    # Find by color
    red_edges = populated_canvas.find_edges(color=Color.RED)
    assert len(red_edges) == 1
    assert red_edges[0].label == "Edge A"

    # Combined criteria
    combined_edges = populated_canvas.find_edges(from_node_id="node-1", color=Color.RED)
    assert len(combined_edges) == 1
    assert combined_edges[0].label == "Edge A"

def test_canvas_to_mermaid(populated_canvas):
    # Add more nodes and edges to make the mermaid output more interesting
    node3 = populated_canvas.add_node(obj_id="node-3", node_type=NodeType.TEXT, text="Another Node")
    node4 = populated_canvas.add_node(obj_id="node-4", node_type=NodeType.FILE, file="document.pdf")
    populated_canvas.add_edge(from_node_id="node-1", to_node_id="node-3", label="Connects")
    populated_canvas.add_edge(from_node_id="node-3", to_node_id="node-4", label="Refers to")

    mermaid_output = populated_canvas.to_mermaid()
    
    assert "graph TD" in mermaid_output
    assert 'node-1["Node 1"]' in mermaid_output
    assert 'node-2["file.md"]' in mermaid_output
    assert 'node-3["Another Node"]' in mermaid_output
    assert 'node-4["document.pdf"]' in mermaid_output
    assert "node-1 --> node-2" in mermaid_output
    assert 'node-1 -->|"Connects"| node-3' in mermaid_output
    assert 'node-3 -->|"Refers to"| node-4' in mermaid_output
