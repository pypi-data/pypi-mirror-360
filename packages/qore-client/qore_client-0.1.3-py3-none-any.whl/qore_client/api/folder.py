from typing import Any, Dict

import pandas as pd


class FolderAPI:
    """Folder operation utilities for QoreClient"""

    def __init__(self, request_method):
        """
        Initialize with the request method from the parent client
        """
        self._request = request_method

    def _get_folder_info(self, folder_id: str) -> Dict[str, Any]:
        """
        폴더 정보를 가져옵니다.
        """
        response = self._request("GET", f"/api/folder/{folder_id}")
        return response

    def is_file_exists(self, file_name: str, folder_id: str) -> str:
        """
        파일 존재 여부를 확인하고 존재하면 file_id를 반환합니다.
        존재하지 않으면 빈 문자열을 반환합니다.

        :param file_name: 파일 이름
        :param folder_id: 폴더 ID
        :return: 파일이 존재하면 file_id, 없으면 빈 문자열
        """
        file_list = self.get_file_list(folder_id)
        if file_name in file_list["name"].values:
            return file_list[file_list["name"] == file_name]["id"].iloc[0]
        return ""

    def get_file_list(self, folder_id: str) -> pd.DataFrame:
        """
        폴더 내 파일 목록을 가져옵니다.
        Returns a list of files in the folder, each containing:
        - id: 파일 ID
        - name: 파일 이름
        - size: 파일 크기 (bytes)
        - mime_type: 파일 MIME 타입
        """
        response = self._get_folder_info(folder_id)
        return pd.DataFrame(response.get("files", []))

    def get_folder_list(self, drive_id: str) -> pd.DataFrame:
        """
        드라이브 내 폴더 목록을 가져옵니다.
        """
        response = self._get_folder_info(drive_id)
        return pd.DataFrame(response.get("folders", []))
