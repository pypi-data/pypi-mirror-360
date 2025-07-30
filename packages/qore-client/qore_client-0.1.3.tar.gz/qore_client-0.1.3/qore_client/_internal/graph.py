from collections import defaultdict, deque
from typing import TYPE_CHECKING, Dict, List, Tuple

if TYPE_CHECKING:
    from qore_client.models.workflow_models import Edge

from qore_client.models.workflow_models import Node


class GraphOperations:
    @staticmethod
    def build_adjacency_list(edges: List["Edge"]) -> Dict[str, List[str]]:
        adjacency = defaultdict(list)
        for edge in edges:
            adjacency[edge.source].append(edge.target)
        return dict(adjacency)

    @staticmethod
    def topological_sort(
        nodes: List[Node],
        edges_dict: Dict[str, List[str]],
        x_gap: int = 250,
        y_gap: int = 100,
        start_x: int = 0,
        start_y: int = 0,
    ) -> Dict[str, Tuple[float, float]]:
        indegree: defaultdict[str, int] = defaultdict(int)
        graph: defaultdict[str, List[str]] = defaultdict(list)

        for src, targets in edges_dict.items():
            for target in targets:
                graph[src].append(target)
                indegree[target] += 1
                if src not in indegree:
                    indegree[src] = 0

        node_map = {node.id: node for node in nodes}
        queue = deque([nid for nid in node_map if indegree[nid] == 0])
        visited = set()
        layer = 0
        positions = {}

        while queue:
            layer_size = len(queue)
            for i in range(layer_size):
                node_id = queue.popleft()
                if node_id in visited:
                    continue
                visited.add(node_id)

                if node_id in node_map:
                    node = node_map[node_id]
                    x = start_x + x_gap * layer
                    y = start_y + y_gap * i
                    node.position.x = x
                    node.position.y = y
                    positions[node_id] = (float(x), float(y))

                for next_id in graph[node_id]:
                    indegree[next_id] -= 1
                    if indegree[next_id] == 0:
                        queue.append(next_id)
            layer += 1

        return positions
