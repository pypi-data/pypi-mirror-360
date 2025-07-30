from typing import Any, Dict, List, Literal

from qore_client.api.output_parser import parse_workflow_output


class WorkflowAPI:
    """Workflow operation utilities for QoreClient"""

    def __init__(self, request_method):
        """
        Initialize with the request method from the parent client

        :param request_method: The _request method from QoreClient
        """
        self._request = request_method

    def get_published_workflow_detail(self, workflow_id: str) -> dict:
        """Published 워크플로우 상세 정보를 가져옵니다."""
        response = self._request("GET", f"/api/workflow/{workflow_id}")
        return response

    def get_draft_workflow_detail(self, workflow_id: str) -> dict:
        """Draft 워크플로우 상세 정보를 가져옵니다."""
        response = self._request("GET", f"/api/workflow/{workflow_id}/draft")
        return response

    def get_version_workflow_detail(self, workflow_id: str, version: str) -> dict:
        """Version 워크플로우 상세 정보를 가져옵니다."""
        response = self._request("GET", f"/api/workflow/{workflow_id}/{version}")
        return response

    def create_workflow(self, workspace_id: str, workflow_name: str, description: str = "") -> dict:
        """워크플로우를 생성합니다."""
        response = self._request(
            "POST",
            "/api/workflow/create",
            data={"workspace_id": workspace_id, "name": workflow_name, "description": description},
        )
        return response

    def save_workflow(self, workflow_id: str, workflow_json: dict) -> dict:
        """워크플로우를 저장합니다."""
        response = self._request(
            "PUT", f"/api/workflow/{workflow_id}/draft/save", json=workflow_json
        )
        if response:
            return {"status": "success"}
        else:
            return {"status": "failed"}

    def execute_workflow(
        self,
        workflow_id: str,
        workflow_json: dict,
        format: Literal["raw", "logs", "output"],
    ) -> dict:
        """워크플로우를 실행합니다."""
        response = self._request(
            "POST", f"/api/workflow/{workflow_id}/draft/execute", json=workflow_json
        )
        return parse_workflow_output(response, format)

    def execute_published_workflow(
        self,
        workflow_id: str,
        format: Literal["raw", "logs", "output"],
        version: Literal["latest"] | int = "latest",
        **kwargs,
    ) -> List[str] | Dict[str, Any]:
        """Published 워크플로우를 실행합니다."""
        response_data = self._request(
            "POST", f"/api/workflow/{workflow_id}/{version}/execute", json=kwargs
        )

        if response_data is None:
            raise ValueError("Failed to execute workflow, received None response.")

        return parse_workflow_output(response_data, format)
