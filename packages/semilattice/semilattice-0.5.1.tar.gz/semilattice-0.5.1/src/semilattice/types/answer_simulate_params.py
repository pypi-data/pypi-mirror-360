# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from .answer_param import AnswerParam

__all__ = ["AnswerSimulateParams", "Answers"]


class AnswerSimulateParams(TypedDict, total=False):
    answers: Required[Answers]

    population_id: Required[str]


Answers: TypeAlias = Union[AnswerParam, Iterable[AnswerParam]]
