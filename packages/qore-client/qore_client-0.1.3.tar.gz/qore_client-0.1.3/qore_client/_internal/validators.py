from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from qore_client.models.workflow_models import Edge, Node


class WorkflowValidator:
    @staticmethod
    def validate_node_exists(node_id: str, nodes: List[Node]) -> None:
        is_exists = any(node.id == node_id for node in nodes)
        if not is_exists:
            raise ValueError(f"Node with id {node_id} not found")

    @staticmethod
    def validate_node_can_be_deleted(node_id: str) -> None:
        if node_id in ["start-node", "end-node"]:
            raise ValueError(f"Cannot delete {node_id}")

    @staticmethod
    def validate_params(params: dict, input_fields: list[dict]) -> None:
        input_field_map: Dict[str, Dict[str, Any]] = {
            field["name"]: field for field in input_fields if "name" in field
        }

        param_names = set(params.keys())
        input_field_names = set(input_field_map.keys())

        # 1. Check for extraneous parameters not in input_fields
        extra_params = param_names - input_field_names
        if extra_params:
            raise ValueError(f"Unknown parameters provided: {', '.join(extra_params)}")

        type_map: Dict[str, Union[Type[Any], Tuple[Type[Any], ...]]] = {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": bool,
        }

        for field_name, field_def in input_field_map.items():
            # 3. Check for missing required parameters
            if field_def.get("required") and field_name not in param_names:
                raise ValueError(f"Missing required parameter: {field_name}")

            # 2. Check for correct parameter types
            if field_name in params:
                param_value = params[field_name]
                expected_type_str: Optional[str] = field_def.get("type")

                if expected_type_str and expected_type_str in type_map:
                    expected_type = type_map[expected_type_str]
                    if not isinstance(param_value, expected_type):
                        raise TypeError(
                            f"Parameter '{field_name}' has incorrect type. "
                            f"Expected {expected_type_str}, but got {type(param_value).__name__}."
                        )

    @staticmethod
    def validate_edges(edges: List[Edge], node_ids: Set[str]) -> None:
        for edge in edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                raise ValueError(f"Edge {edge} has invalid node ids")

        source_ids = {edge.source for edge in edges}
        target_ids = {edge.target for edge in edges}
        union_ids = source_ids | target_ids

        for node_id in node_ids:
            if node_id not in union_ids:
                raise ValueError(f"Node {node_id} is isolated")
