from typing import Any
from ascender.common import BaseResponse


class ALPError(BaseResponse):
    code: int
    details: str | dict[str, Any] | None