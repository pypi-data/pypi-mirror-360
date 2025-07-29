# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["AnswerParam", "QuestionOptions"]


class QuestionOptions(TypedDict, total=False):
    question_type: Required[Literal["single-choice", "multiple-choice", "open-ended"]]

    limit: Optional[int]

    question_number: Optional[int]


class AnswerParam(TypedDict, total=False):
    question: Required[str]

    question_options: Required[QuestionOptions]

    answer_options: Optional[List[str]]

    ground_answer_counts: Union[str, object, None]

    ground_answer_sample_size: Optional[int]
