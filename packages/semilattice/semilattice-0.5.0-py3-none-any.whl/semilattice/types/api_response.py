# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .error import Error
from .._models import BaseModel

__all__ = ["APIResponse", "Data"]


class Data(BaseModel):
    id: str

    created_at: datetime

    name: str

    public: bool

    question_count: int

    simulacrum_count: int

    status: str

    avg_mean_absolute_error: Optional[float] = None

    avg_mean_squared_error: Optional[float] = None

    avg_normalised_kullback_leibler_divergence: Optional[float] = None

    description: Optional[str] = None

    reality_target: Optional[str] = None

    simulation_engine: Optional[str] = None

    test_finished_at: Optional[datetime] = None

    test_started_at: Optional[datetime] = None

    upload_filename: Optional[str] = None


class APIResponse(BaseModel):
    data: Optional[Data] = None
    """Population model data:"""

    errors: Optional[List[Error]] = None
    """List of error messages, if any."""
