import pickle
from io import BytesIO
from typing import Any, Callable, Dict

import pandas as pd
from requests import Response, request

from qore_client.api.folder import FolderAPI


class FileAPI:
    """File operation utilities for QoreClient"""

    def __init__(self, request_method):
        """
        Initialize with the request method from the parent client

        :param request_method: The _request method from QoreClient
        """
        self._request = request_method
        self._folder_api = FolderAPI(request_method)

    def _get_file_response(self, file_id: str) -> Response:
        """
        파일 다운로드 URL을 가져와서 HTTP 응답 객체를 반환합니다.

        :param file_id: 다운로드할 파일의 ID
        :return: 다운로드된 파일에 대한 HTTP 응답 객체
        """
        response = self._request("GET", f"/api/file/{file_id}/download_url")

        if response is None:
            raise ValueError("Failed to get download info, received None response.")

        file_response = request("GET", response["download_url"])
        file_response.raise_for_status()

        return file_response

    def upload_file(
        self,
        file_path: str,
        *,
        folder_id: str,
    ) -> Dict[str, Any]:
        """
        파일 업로드 URL을 가져와서 HTTP 응답 객체를 반환합니다.

        :param file_name: 업로드할 파일의 이름
        :param folder_id: 업로드할 폴더의 ID
        :return: 업로드된 파일에 대한 HTTP 응답 객체
        """
        data = {
            "folder_id": folder_id,
        }

        with open(file_path, "rb") as f:
            files = {"file": f}
            response_data = self._request("POST", "/api/file/create", data=data, files=files)
            # _request for POST /api/file/create should always return a dict on success
            if response_data is None:
                raise ValueError("Failed to upload file, received None response.")

        return response_data

    def put_file(
        self,
        file_content: BytesIO,
        file_name: str,
        *,
        folder_id: str,
    ) -> Dict[str, Any]:
        """
        파일 내용을 직접 메모리에서 업로드합니다.

        :param file_content: 업로드할 파일 내용 (BytesIO 객체)
        :param file_name: 업로드할 파일의 이름
        :param folder_id: 업로드할 폴더의 ID
        :return: 업로드된 파일에 대한 HTTP 응답 객체
        """
        data = {
            "folder_id": folder_id,
        }

        file_content.name = file_name

        files = {"file": file_content}
        response_data = self._request("POST", "/api/file/create", data=data, files=files)

        if response_data is None:
            raise ValueError("Failed to put file, received None response.")

        return response_data

    def get_file(self, file_id: str) -> BytesIO:
        response = self._get_file_response(file_id)
        file_content = BytesIO(response.content)
        return file_content

    def get_file_url(self, file_id: str) -> str:
        response = self._request("GET", f"/api/file/{file_id}/download_url")
        return response["download_url"]

    def get_dataframe(self, dataframe_id: str) -> pd.DataFrame:
        response = self._get_file_response(dataframe_id)
        content_type = response.headers["Content-Type"]
        content = response.content

        if content_type == "application/vnd.quantit.parquet":
            return pd.read_parquet(BytesIO(content))
        else:
            raise ValueError(
                f"Only files saved using the 'Save Dataframe' node in Workspace can be converted to dataframe. File content type: {content_type}"
            )

    def cache_result(
        self,
        file_name: str,
        folder_id: str,
        *,
        function: Callable,
        force_update: bool = False,
    ) -> Any:
        """
        파일이 존재하면 불러오고, 없으면 함수를 실행하여 pickle로 직렬화하여 저장합니다.

        :param file_name: 파일 이름
        :param folder_id: 폴더 ID
        :param func: 파일이 없을 경우 실행할 함수, 반환값이 저장됨
        :param force_update: 파일이 존재하더라도 강제로 업데이트할지 여부
        :return: 불러오거나 저장된 Python 객체
        """
        if not callable(function):
            raise TypeError(
                "function 매개변수는 호출 가능한 함수여야 합니다. 제공된 타입: {}".format(
                    type(function).__name__
                )
            )

        file_id = self._folder_api.is_file_exists(file_name, folder_id)
        if file_id and not force_update:
            # 파일이 있을 경우 불러와서 역직렬화
            file_content = self.get_file(file_id)
            return pickle.load(file_content)
        else:
            # 파일이 없거나 강제 업데이트 옵션이 켜진 경우 함수 실행 후 직렬화하여 저장
            variable = function()
            file_content = BytesIO()
            pickle.dump(variable, file_content)
            file_content.seek(0)
            self.put_file(file_content, file_name, folder_id=folder_id)
            return variable
