"""
프로젝트명 패키지
"""

from importlib.metadata import version

__version__ = version("qore_client")

from qore_client.client import QoreClient

__all__ = ["QoreClient"]
