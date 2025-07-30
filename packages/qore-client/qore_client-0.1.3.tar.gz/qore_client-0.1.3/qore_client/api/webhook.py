from typing import Literal

from qore_client.api.output_parser import parse_workflow_output


class WebhookAPI:
    """Webhook operation utilities for QoreClient"""

    def __init__(self, request_method):
        """
        Initialize with the request method from the parent client
        """
        self._request = request_method

    def execute_webhook(
        self, webhook_id: str, format: Literal["raw", "logs", "output"], **kwargs
    ) -> dict | list[str]:
        """Webhook을 실행합니다."""

        json = {"params": kwargs}
        response = self._request("POST", f"/webhook/{webhook_id}", json=json)

        return parse_workflow_output(response, format)
