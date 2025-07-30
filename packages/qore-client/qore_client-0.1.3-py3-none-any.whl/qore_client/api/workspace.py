class WorkspaceAPI:
    """Workspace operation utilities for QoreClient"""

    def __init__(self, request_method):
        """
        Initialize with the request method from the parent client
        """
        self._request = request_method

    def get_workspace_detail(self, workspace_id: str) -> dict:
        """워크스페이스 상세 정보를 가져옵니다."""
        response = self._request("GET", f"/api/workspace/{workspace_id}")
        return response
