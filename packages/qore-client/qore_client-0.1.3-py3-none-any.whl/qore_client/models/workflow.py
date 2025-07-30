from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field

from qore_client._internal.graph import GraphOperations
from qore_client._internal.nodes import NodeFactory
from qore_client._internal.validators import WorkflowValidator

from .workflow_models import CodeNodeData, Edge, EndNodeData, Node, NodeData, StartNodeData

if TYPE_CHECKING:
    from qore_client import QoreClient


class Params(BaseModel):
    model_config = ConfigDict(extra="allow")


class Workflow(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []
    params: Params = Field(default_factory=Params)

    @classmethod
    def from_dict(cls, workflow_json: dict) -> "Workflow":
        return cls.model_validate(workflow_json)

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_qore(cls, client: "QoreClient", workflow_id: str, diagram: bool = True) -> "Workflow":
        wf_json = client.get_workflow(workflow_id, diagram=diagram)
        return cls.model_validate(wf_json)

    def to_qore(self, client: "QoreClient", workflow_id: str) -> dict:
        return client.save_workflow(workflow_id, self)

    def summary(self) -> dict:
        return {
            "input_fields": self.get_input_fields(),
            "nodes": self.get_nodes(summary=True),
            "edges": self.get_edges(),
            "output_fields": self.get_output_fields(),
        }

    def validate_workflow(self, is_execute: bool = True) -> None:
        WorkflowValidator.validate_edges(self.edges, {n["id"] for n in self.get_nodes()})
        if is_execute:
            WorkflowValidator.validate_params(self.params.model_dump(), self.get_input_fields())

    def get_edges(self) -> Dict[str, List[str]]:
        return GraphOperations.build_adjacency_list(self.edges)

    def get_input_fields(self) -> list[dict]:
        start_node = self.get_node("start-node").get("request_body", None)
        input_fields = [rb.model_dump() for rb in start_node] if start_node else []

        return input_fields

    def get_output_fields(self) -> list[dict]:
        return self.get_node("end-node").get("inputs", None)

    def get_nodes(self, summary: bool = True) -> List[Dict[str, Any]]:
        nodes = []
        for node in self.nodes:
            node_info = {
                "id": node.id,
                "label": node.data.label,
                "type": getattr(node.data, "type", None),
            }

            if isinstance(node.data, StartNodeData):
                if not summary:
                    node_info["request_body"] = getattr(node.data, "request_body", [])

            elif isinstance(node.data, CodeNodeData):
                node_info["inputs"] = getattr(node.data, "inputs", [])
                node_info["outputs"] = getattr(node.data, "outputs", [])
                if not summary:
                    node_info["code"] = node.data.code
            elif isinstance(node.data, EndNodeData):
                if not summary:
                    node_info["inputs"] = getattr(node.data, "inputs", [])
            nodes.append(node_info)

        return nodes

    def get_node(self, node_id: str) -> dict:
        node = next((n for n in self.get_nodes(summary=False) if n["id"] == node_id), None)
        if node is None:
            raise ValueError(f"Node with id {node_id} not found")
        return node

    def update_node(self, node_id: str, data: NodeData | CodeNodeData) -> str:
        WorkflowValidator.validate_node_exists(node_id, self.nodes)

        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.nodes.append(NodeFactory.create_node(data, node_id))
        self._arrange_nodes_by_edges(self.get_edges())
        return node_id

    def delete_node(self, node_id: str) -> None:
        WorkflowValidator.validate_node_exists(node_id, self.nodes)
        WorkflowValidator.validate_node_can_be_deleted(node_id)

        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.edges = [e for e in self.edges if e.source != node_id and e.target != node_id]
        self._arrange_nodes_by_edges(self.get_edges())

    def update_start_node(
        self,
        request_bodies: Sequence[dict],
        description: Optional[str] = None,
    ) -> str:
        WorkflowValidator.validate_node_exists("start-node", self.nodes)

        node = NodeFactory.create_start_node(list(request_bodies), description)

        self.nodes = [n for n in self.nodes if n.id != "start-node"]
        self.nodes.append(node)
        self._arrange_nodes_by_edges(self.get_edges())
        return "start-node"

    def update_end_node(
        self,
        inputs: Sequence[dict],
        description: Optional[str] = None,
    ) -> str:
        WorkflowValidator.validate_node_exists("end-node", self.nodes)

        node = NodeFactory.create_end_node(list(inputs), description)

        self.nodes = [n for n in self.nodes if n.id != "end-node"]
        self.nodes.append(node)
        self._arrange_nodes_by_edges(self.get_edges())
        return "end-node"

    def update_code_node(
        self,
        node_id: str,
        code: str,
        label: str = "Code",
        description: Optional[str] = None,
        inputs: Optional[list[dict]] = None,
        outputs: Optional[list[str]] = None,
    ) -> str:
        WorkflowValidator.validate_node_exists(node_id, self.nodes)

        node = NodeFactory.create_code_node(code, label, description, inputs, outputs, node_id)

        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.nodes.append(node)
        self._arrange_nodes_by_edges(self.get_edges())
        return node_id

    def add_node(self, data: NodeData | CodeNodeData) -> str:
        node = NodeFactory.create_node(data)
        self.nodes.append(node)
        return node.id

    def add_code_node(
        self,
        code: str,
        label: str = "Code",
        inputs: Optional[list[dict]] = None,
        outputs: Optional[list[str]] = None,
    ) -> str:
        node = NodeFactory.create_code_node(code, label, None, inputs, outputs)
        self.nodes.append(node)
        self._arrange_nodes_by_edges(self.get_edges())
        return node.id

    def set_edges(self, edges: Dict[str, List[str]]) -> None:
        """
        edges: {source_id: [target_id, ...], ...}
        현재 워크플로우의 노드들을 그대로 사용하고,
        edges에 맞게 edges를 새로 생성하며,
        노드 배치는 arrange_nodes_by_edges로 수행한다.
        """
        node_ids = {node.id for node in self.nodes}
        new_edges = []
        edge_id = 0

        for src, targets in edges.items():
            for tgt in targets:
                if src in node_ids and tgt in node_ids:
                    new_edges.append(Edge(id=f"edge-{edge_id}", source=src, target=tgt))
                    edge_id += 1

        self.edges = new_edges
        self._arrange_nodes_by_edges(edges)

    def _arrange_nodes_by_edges(
        self,
        edges: Dict[str, List[str]],
        x_gap: int = 250,
        y_gap: int = 100,
        start_x: int = 0,
        start_y: int = 0,
    ) -> "Workflow":
        """
        edges를 기반으로 위상정렬하여 노드 위치를 배치한다.
        """
        GraphOperations.topological_sort(self.nodes, edges, x_gap, y_gap, start_x, start_y)
        return self
