import hashlib
import hmac
import json
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from qore_client.settings import ACCESS_KEY, SECRET_KEY


class QoreAuth:
    """Authentication logic for Qore API"""

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize authentication with keys

        :param access_key: Qore API 인증에 사용되는 Access Key
        :param secret_key: Qore API 인증에 사용되는 Secret Key
        """
        self.__access_key = access_key or ACCESS_KEY
        self.__secret_key = secret_key or SECRET_KEY

        if not self.__access_key or not self.__secret_key:
            raise ValueError("access_key and secret_key must be provided")

    def generate_headers(self, credential_source: str) -> Dict[str, Any]:
        """Generate authentication headers for API requests"""
        return {
            "X-API-ACCESS-KEY": self.__access_key,
            "X-API-SIGNATURE": self.generate_signature(credential_source=credential_source),
        }

    def generate_signature(self, credential_source: str) -> str:
        """Generate HMAC signature for authentication"""
        if self.__secret_key is None:
            raise TypeError("Secret key is None, cannot create signature.")
        signature = hmac.new(self.__secret_key.encode(), credential_source.encode(), hashlib.sha256).hexdigest()
        return signature

    def get_credential_source(
        self, method: str, path: str, params: Dict[str, Any], data: Dict[str, Any] | None = None
    ) -> str:
        """Generate credential source string for signing"""
        query_string = urlencode(params)
        if data:
            data_string = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        else:
            data_string = ""
        combined_string = f"{query_string}{data_string}"
        return f"{method}:{path}:{combined_string}"

    @property
    def access_key(self) -> str:
        """Get the access key"""
        if self.__access_key is None:
            raise ValueError("Access key is not set")
        return self.__access_key
