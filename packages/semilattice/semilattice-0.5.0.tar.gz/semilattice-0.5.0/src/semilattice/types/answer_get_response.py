# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .error import Error
from .._models import BaseModel
from .answer_response import AnswerResponse

__all__ = ["AnswerGetResponse"]


class AnswerGetResponse(BaseModel):
    data: Optional[AnswerResponse] = None
    """Answer data:"""

    errors: Optional[List[Error]] = None
    """List of error messages, if any."""
