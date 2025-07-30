import time
from io import BytesIO
from typing import Any, Callable, Dict, List, Literal, Optional

import pandas as pd
from requests import HTTPError, Response, request

from qore_client._internal.module import ModuleImportManager
from qore_client.api import (
    DriveAPI,
    FileAPI,
    FolderAPI,
    OrganizationAPI,
    WebhookAPI,
    WorkflowAPI,
    WorkspaceAPI,
)
from qore_client.auth import QoreAuth
from qore_client.models import Params, Workflow
from qore_client.settings import API_ENDPOINT


class QoreClient:
    """
    Qore API Client
    ~~~~~~~~~~~~~~~

    Qore 서비스에 접근할 수 있는 파이썬 Client SDK 예시입니다.
    """

    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ) -> None:
        """
        :param access_key: Qore API 인증에 사용되는 Access Key
        :param secret_key: Qore API 인증에 사용되는 Secret Key
        """
        self.auth = QoreAuth(access_key, secret_key)

        self.organization_api = OrganizationAPI(self._request)
        self.drive_api = DriveAPI(self._request)
        self.folder_api = FolderAPI(self._request)
        self.file_api = FileAPI(self._request)
        self.module_api = ModuleImportManager(self.get_file, self.upload_file)
        self.workflow_api = WorkflowAPI(self._request)
        self.workspace_api = WorkspaceAPI(self._request)
        self.webhook_api = WebhookAPI(self._request)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | list[tuple[str, Any]] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        내부적으로 사용하는 공통 요청 메서드

        :param method: HTTP 메서드 (GET, POST, PATCH, DELETE 등)
        :param path: API 엔드포인트 경로 (ex: "/d/12345")
        :param params: query string으로 전송할 딕셔너리
        :param data: 폼데이터(form-data) 등으로 전송할 딕셔너리
        :param json: JSON 형태로 전송할 딕셔너리
        :param files: multipart/form-data 요청 시 사용할 파일(dict)
        :return: 응답 JSON(dict) 또는 raw 데이터
        """
        url = f"{API_ENDPOINT}{path}"

        # method, path, params를 문자열로 결합하여 서명 생성
        if params is None:
            params = {
                "timestamp": time.time(),
            }
        else:
            params["timestamp"] = time.time()

        credential_source = self.auth.get_credential_source(method=method, path=path, params=params, data=json)
        headers = self.auth.generate_headers(credential_source=credential_source)

        response: Response = request(
            method=method,
            headers=headers,
            url=url,
            params=params,
            data=data,
            json=json,
            files=files,
        )

        try:
            response.raise_for_status()
        except HTTPError as e:
            try:
                return e.response.json()

            except Exception:
                print(e.response.text)
                raise e from None

        # 일부 DELETE 요청은 204(No Content)일 수 있으므로, 이 경우 JSON 파싱 불가
        if response.status_code == 204 or not response.content:
            print("NO CONTENT")
            return None

        return response.json()

    def ping(self) -> bool:
        """
        서버가 살아있는지 확인합니다.

        :return: 서버가 정상적으로 응답하면 True, 그렇지 않으면 False
        """
        try:
            response = request("GET", self.domain)
            return response.status_code == 200
        except Exception:
            return False

    # Organization operations delegate methods
    # ------------------------------------------

    def get_organization_list(self) -> pd.DataFrame:
        """조직 목록을 가져옵니다."""
        return self.organization_api.get_organization_list()

    def get_drive_list(self, organization_id: str) -> pd.DataFrame:
        """조직 내 드라이브 목록을 가져옵니다."""
        return self.organization_api.get_drive_list(organization_id)

    def get_organization_detail(self, organization_id: str) -> Dict[str, Any]:
        """조직 상세 정보를 가져옵니다."""
        return self.organization_api.get_organization_detail(organization_id)

    def get_workspace_list(self, organization_id: str) -> pd.DataFrame:
        """워크스페이스 목록을 가져옵니다."""
        return self.organization_api.get_workspace_list(organization_id)

    # Workspace operations delegate methods
    # ------------------------------------------
    def get_workspace_detail(self, workspace_id: str) -> dict:
        """워크스페이스 상세 정보를 가져옵니다."""
        return self.workspace_api.get_workspace_detail(workspace_id)

    # Workflow operations delegate methods
    # ------------------------------------------
    def create_workflow(
        self,
        workspace_id: str,
        workflow_name: str,
        description: str = "",
    ) -> dict:
        """워크플로우를 생성합니다."""
        return self.workflow_api.create_workflow(workspace_id, workflow_name, description)

    def get_workflow(
        self,
        workflow_id: str,
        version: Literal["latest", "draft"] | str = "draft",
        diagram: bool = False,
    ) -> dict:
        """워크플로우 상세 정보를 가져옵니다."""
        if version == "latest":
            response = self.workflow_api.get_published_workflow_detail(workflow_id)
        elif version == "draft":
            response = self.workflow_api.get_draft_workflow_detail(workflow_id)
        else:
            response = self.workflow_api.get_version_workflow_detail(workflow_id, version)

        if diagram and "diagram" in response:
            return response["diagram"]
        else:
            return response

    def save_workflow(self, workflow_id: str, workflow: Workflow):
        """워크플로우를 저장합니다."""
        workflow.validate_workflow(is_execute=False)
        return self.workflow_api.save_workflow(workflow_id, workflow.to_dict())

    def execute_workflow(
        self,
        workflow_id: str,
        workflow: Workflow,
        format: Literal["raw", "logs", "output"] = "output",
        **kwargs,
    ) -> dict:
        """워크크플로우를 실행합니다."""
        workflow.params = Params(**kwargs)
        workflow.validate_workflow(is_execute=True)
        return self.workflow_api.execute_workflow(workflow_id, workflow.to_dict(), format=format)

    # Published workflow operations delegate methods
    # ------------------------------------------

    def execute_published_workflow(
        self,
        workflow_id: str,
        version: Literal["latest"] | int = "latest",
        format: Literal["raw", "logs", "output"] = "output",
        **kwargs,
    ) -> List[str] | Dict[str, Any]:
        """Published 워크플로우를 실행합니다."""
        return self.workflow_api.execute_published_workflow(
            workflow_id, version=version, format=format, **kwargs
        )

    # Webhook operations delegate methods
    # ------------------------------------------
    def execute_webhook(
        self,
        webhook_id: str,
        format: Literal["raw", "logs", "output"] = "output",
        **kwargs,
    ) -> dict | List[str]:
        """Webhook을 실행합니다."""
        return self.webhook_api.execute_webhook(webhook_id, format=format, **kwargs)

    # Drive operations delegate methods
    # ------------------------------------------
    def get_drive_info(self, drive_id: str) -> Dict[str, Any]:
        """드라이브 정보를 가져옵니다."""
        return self.drive_api.get_drive_info(drive_id)

    # Folder operations delegate methods
    # ------------------------------------------
    def get_file_list(self, folder_id: str) -> pd.DataFrame:
        """폴더 내 파일 목록을 가져옵니다."""
        return self.folder_api.get_file_list(folder_id)

    def get_folder_list(self, drive_id: str) -> pd.DataFrame:
        """드라이브 내 폴더 목록을 가져옵니다."""
        return self.folder_api.get_folder_list(drive_id)

    # File operations delegate methods
    # ------------------------------------------
    def upload_file(self, file_path: str, *, folder_id: str) -> Dict[str, Any]:
        """파일을 업로드합니다."""
        return self.file_api.upload_file(file_path, folder_id=folder_id)

    def put_file(self, file_content: BytesIO, file_name: str, *, folder_id: str) -> Dict[str, Any]:
        """파일 내용을 직접 메모리에서 업로드합니다."""
        return self.file_api.put_file(file_content, file_name=file_name, folder_id=folder_id)

    def get_file(self, file_id: str) -> BytesIO:
        """파일을 다운로드합니다."""
        return self.file_api.get_file(file_id)

    def get_file_url(self, file_id: str) -> str:
        """파일 다운로드 URL을 가져옵니다."""
        return self.file_api.get_file_url(file_id)

    def get_dataframe(self, dataframe_id: str) -> pd.DataFrame:
        """데이터프레임을 다운로드합니다."""
        return self.file_api.get_dataframe(dataframe_id)

    def cache_result(
        self,
        file_name: str,
        folder_id: str,
        *,
        function: Callable,
        force_update: bool = False,
    ) -> Any:
        """파일이 존재하면 불러오고, 없으면 함수를 실행하여 pickle로 직렬화하여 저장합니다."""
        return self.file_api.cache_result(
            file_name, folder_id, function=function, force_update=force_update
        )

    # Module operations delegate methods
    # ------------------------------------------

    def get_module(self, wheel_file_id: str):
        """드라이브에서 wheel 파일을 다운로드하여 임시로 설치 (컨텍스트 종료 후 자동 삭제)"""
        return self.module_api.get_module(wheel_file_id)

    def upload_module(
        self,
        module_path: str,
        folder_id: str,
        version: str = "0.1.0",
    ) -> Dict[str, Any]:
        """단일 파일 또는 디렉토리를 wheel 패키지로 빌드하여 Qore 드라이브에 업로드"""
        return self.module_api.build_and_upload_module(module_path, folder_id, version)
