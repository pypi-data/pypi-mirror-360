import uuid
import json

class FlowNode:
    def __init__(self, node_id, module_type, position, name=None, inputs=None, outputs=None):
        self.id = node_id
        self.type = "custom"
        self.initialized = False
        self.position = position
        self.data = {
            "moduleType": module_type,
            "name": name or node_id,
            "inputs": inputs or [],
            "outputs": outputs or [],
            "id": node_id,
            "disabled": False
        }

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "initialized": self.initialized,
            "position": self.position,
            "data": self.data
        }

class FlowEdge:
    def __init__(self, source, target, source_handle="", target_handle=""):
        self.id = str(uuid.uuid4())
        self.type = "custom"
        self.source = source
        self.target = target
        self.sourceHandle = source_handle
        self.targetHandle = target_handle
        self.data = {}
        self.label = ""
        self.animated = False
        self.sourceX = 0
        self.sourceY = 0
        self.targetX = 0
        self.targetY = 0

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "target": self.target,
            "sourceHandle": self.sourceHandle,
            "targetHandle": self.targetHandle,
            "data": self.data,
            "label": self.label,
            "animated": self.animated,
            "sourceX": self.sourceX,
            "sourceY": self.sourceY,
            "targetX": self.targetX,
            "targetY": self.targetY
        }

class FlowGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.viewport = {"x": 0, "y": 0, "zoom": 1.0}

    def add_node(self, node_id, module_type, position, name=None, inputs=None, outputs=None):
        node = FlowNode(node_id, module_type, position, name, inputs, outputs)
        self.nodes.append(node)

    def add_edge(self, source, target, source_handle="", target_handle=""):
        edge = FlowEdge(source, target, source_handle, target_handle)
        self.edges.append(edge)

    def to_json(self):
        return json.dumps({
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "viewport": self.viewport
        }, indent=2, ensure_ascii=False)

    def set_viewport(self, x, y, zoom):
        self.viewport = {"x": x, "y": y, "zoom": zoom}


if __name__ == "__main__":
    graph = FlowGraph()

    graph.add_node(node_id="agent1", module_type="questionInput", position={"x": 0, "y": 100})
    graph.add_node(node_id="agent2", module_type="infoExtract", position={"x": 300, "y": 100})

    graph.add_edge(source="agent1", target="agent2", source_handle="userChatInput", target_handle="text")

    # 导出为 JSON 请求体
    print(graph.to_json())