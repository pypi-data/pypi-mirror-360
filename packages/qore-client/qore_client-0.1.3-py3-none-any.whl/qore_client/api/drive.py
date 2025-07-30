from typing import Any, Dict


class DriveAPI:
    """Drive operation utilities for QoreClient"""

    def __init__(self, request_method):
        """
        Initialize with the request method from the parent client
        """
        self._request = request_method

    def get_drive_info(self, drive_id: str) -> Dict[str, Any]:
        """
        드라이브 정보를 가져옵니다.
        """
        response = self._request("GET", f"/api/drive/{drive_id}")
        return response
