import os
from typing import Optional
import qore_client.config as config

# 빌드 환경 설정
BUILD_ENV = config.__env__
BUILD_DATE = config.__build_date__
API_ENDPOINT = config.__api_endpoint__

# 인증 정보
ACCESS_KEY: Optional[str] = os.getenv("QORE_ACCESS_KEY")
SECRET_KEY: Optional[str] = os.getenv("QORE_SECRET_KEY")
