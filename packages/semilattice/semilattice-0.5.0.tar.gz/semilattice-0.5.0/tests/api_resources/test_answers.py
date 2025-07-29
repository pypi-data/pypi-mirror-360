# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from semilattice import Semilattice, AsyncSemilattice
from tests.utils import assert_matches_type
from semilattice.types import AnswerGetResponse, APIResponseListAnswers

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAnswers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_benchmark(self, client: Semilattice) -> None:
        answer = client.answers.benchmark(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_benchmark_with_all_params(self, client: Semilattice) -> None:
        answer = client.answers.benchmark(
            answers={
                "question": "question",
                "question_options": {
                    "question_type": "single-choice",
                    "limit": 0,
                    "question_number": 0,
                },
                "answer_options": ["string"],
                "ground_answer_counts": "string",
                "ground_answer_sample_size": 0,
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_benchmark(self, client: Semilattice) -> None:
        response = client.answers.with_raw_response.benchmark(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_benchmark(self, client: Semilattice) -> None:
        with client.answers.with_streaming_response.benchmark(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            answer = response.parse()
            assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Semilattice) -> None:
        answer = client.answers.get(
            "question_id",
        )
        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Semilattice) -> None:
        response = client.answers.with_raw_response.get(
            "question_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = response.parse()
        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Semilattice) -> None:
        with client.answers.with_streaming_response.get(
            "question_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            answer = response.parse()
            assert_matches_type(AnswerGetResponse, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Semilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `question_id` but received ''"):
            client.answers.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_simulate(self, client: Semilattice) -> None:
        answer = client.answers.simulate(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_simulate_with_all_params(self, client: Semilattice) -> None:
        answer = client.answers.simulate(
            answers={
                "question": "question",
                "question_options": {
                    "question_type": "single-choice",
                    "limit": 0,
                    "question_number": 0,
                },
                "answer_options": ["string"],
                "ground_answer_counts": "string",
                "ground_answer_sample_size": 0,
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_simulate(self, client: Semilattice) -> None:
        response = client.answers.with_raw_response.simulate(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_simulate(self, client: Semilattice) -> None:
        with client.answers.with_streaming_response.simulate(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            answer = response.parse()
            assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAnswers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_benchmark(self, async_client: AsyncSemilattice) -> None:
        answer = await async_client.answers.benchmark(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_benchmark_with_all_params(self, async_client: AsyncSemilattice) -> None:
        answer = await async_client.answers.benchmark(
            answers={
                "question": "question",
                "question_options": {
                    "question_type": "single-choice",
                    "limit": 0,
                    "question_number": 0,
                },
                "answer_options": ["string"],
                "ground_answer_counts": "string",
                "ground_answer_sample_size": 0,
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_benchmark(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.answers.with_raw_response.benchmark(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = await response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_benchmark(self, async_client: AsyncSemilattice) -> None:
        async with async_client.answers.with_streaming_response.benchmark(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            answer = await response.parse()
            assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncSemilattice) -> None:
        answer = await async_client.answers.get(
            "question_id",
        )
        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.answers.with_raw_response.get(
            "question_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = await response.parse()
        assert_matches_type(AnswerGetResponse, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSemilattice) -> None:
        async with async_client.answers.with_streaming_response.get(
            "question_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            answer = await response.parse()
            assert_matches_type(AnswerGetResponse, answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSemilattice) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `question_id` but received ''"):
            await async_client.answers.with_raw_response.get(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_simulate(self, async_client: AsyncSemilattice) -> None:
        answer = await async_client.answers.simulate(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_simulate_with_all_params(self, async_client: AsyncSemilattice) -> None:
        answer = await async_client.answers.simulate(
            answers={
                "question": "question",
                "question_options": {
                    "question_type": "single-choice",
                    "limit": 0,
                    "question_number": 0,
                },
                "answer_options": ["string"],
                "ground_answer_counts": "string",
                "ground_answer_sample_size": 0,
            },
            population_id="population_id",
        )
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_simulate(self, async_client: AsyncSemilattice) -> None:
        response = await async_client.answers.with_raw_response.simulate(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        answer = await response.parse()
        assert_matches_type(APIResponseListAnswers, answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_simulate(self, async_client: AsyncSemilattice) -> None:
        async with async_client.answers.with_streaming_response.simulate(
            answers={
                "question": "question",
                "question_options": {"question_type": "single-choice"},
            },
            population_id="population_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            answer = await response.parse()
            assert_matches_type(APIResponseListAnswers, answer, path=["response"])

        assert cast(Any, response.is_closed) is True
