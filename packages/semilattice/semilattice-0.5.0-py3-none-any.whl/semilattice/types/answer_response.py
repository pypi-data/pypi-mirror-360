# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["AnswerResponse"]


class AnswerResponse(BaseModel):
    id: str

    accuracy: Optional[float] = None

    created_at: datetime

    population: str

    population_name: str

    question: str

    root_mean_squared_error: Optional[float] = None

    status: str

    answer_options: Optional[List[object]] = None

    benchmark_id: Optional[str] = None

    ground_answer_counts: Union[object, object, None] = None

    ground_answer_percentages: Union[object, object, None] = None

    kullback_leibler_divergence: Optional[float] = None

    mean_absolute_error: Optional[float] = None

    mean_squared_error: Optional[float] = None

    normalised_kullback_leibler_divergence: Optional[float] = None

    prediction_finished_at: Optional[datetime] = None

    prediction_started_at: Optional[datetime] = None

    public: Optional[bool] = None

    question_options: Union[object, object, None] = None

    simulated_answer_percentages: Union[object, object, None] = None

    simulation_engine: Optional[str] = None

    test_finished_at: Optional[datetime] = None

    test_started_at: Optional[datetime] = None
