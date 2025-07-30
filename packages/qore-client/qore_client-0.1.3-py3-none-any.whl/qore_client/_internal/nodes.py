import time
from typing import Optional

from qore_client.models.workflow_models import CodeNodeData, Node, NodeData, StartNodeData


class NodeFactory:
    @staticmethod
    def create_node(
        data: NodeData | CodeNodeData | StartNodeData, node_id: Optional[str] = None
    ) -> Node:
        if node_id is None:
            node_id = str(int(time.time() * 1000))

        return Node(id=node_id, data=data)

    @staticmethod
    def create_code_node(
        code: str,
        label: str = "Code",
        description: Optional[str] = None,
        inputs: Optional[list[dict]] = None,
        outputs: Optional[list[str]] = None,
        node_id: Optional[str] = None,
    ) -> Node:
        data = CodeNodeData(
            code=code,
            label=label,
            description=description,
            inputs=inputs or [],
            outputs=outputs or [],
        )
        return NodeFactory.create_node(data, node_id)

    @staticmethod
    def create_start_node(request_bodies: list[dict], description: Optional[str] = None) -> Node:
        from qore_client.models.workflow_models import StartNodeRequestBody

        data = StartNodeData(
            request_body=[StartNodeRequestBody(**rb) for rb in request_bodies],
            description=description,
        )
        return NodeFactory.create_node(data, "start-node")

    @staticmethod
    def create_end_node(inputs: list[dict], description: Optional[str] = None) -> Node:
        from qore_client.models.workflow_models import EndNodeData

        data = EndNodeData(
            inputs=inputs,
            description=description,
        )
        return NodeFactory.create_node(data, "end-node")
