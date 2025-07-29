# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["PopulationCreateParams"]


class PopulationCreateParams(TypedDict, total=False):
    name: Required[str]

    seed_data: Required[FileTypes]

    simulation_engine: Required[str]

    simulation_options: Required[str]

    description: Optional[str]

    reality_target: Optional[str]

    run_test: Optional[bool]
