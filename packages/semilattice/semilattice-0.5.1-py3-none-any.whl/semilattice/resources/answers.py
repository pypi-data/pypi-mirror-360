# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import answer_simulate_params, answer_benchmark_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.answer_get_response import AnswerGetResponse
from ..types.api_response_list_answers import APIResponseListAnswers

__all__ = ["AnswersResource", "AsyncAnswersResource"]


class AnswersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AnswersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AnswersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AnswersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return AnswersResourceWithStreamingResponse(self)

    def benchmark(
        self,
        *,
        answers: answer_benchmark_params.Answers,
        population_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a known question to evaluate population model accuracy.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/answers/benchmark",
            body=maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                },
                answer_benchmark_params.AnswerBenchmarkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )

    def get(
        self,
        question_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AnswerGetResponse:
        """
        Retrieves an answer simulation, along with its status and accuracy metrics if
        it's a benchmark simulation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not question_id:
            raise ValueError(f"Expected a non-empty value for `question_id` but received {question_id!r}")
        return self._get(
            f"/v1/answers/{question_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnswerGetResponse,
        )

    def simulate(
        self,
        *,
        answers: answer_simulate_params.Answers,
        population_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a new question.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/answers",
            body=maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                },
                answer_simulate_params.AnswerSimulateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )


class AsyncAnswersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAnswersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAnswersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAnswersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return AsyncAnswersResourceWithStreamingResponse(self)

    async def benchmark(
        self,
        *,
        answers: answer_benchmark_params.Answers,
        population_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a known question to evaluate population model accuracy.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/answers/benchmark",
            body=await async_maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                },
                answer_benchmark_params.AnswerBenchmarkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )

    async def get(
        self,
        question_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AnswerGetResponse:
        """
        Retrieves an answer simulation, along with its status and accuracy metrics if
        it's a benchmark simulation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not question_id:
            raise ValueError(f"Expected a non-empty value for `question_id` but received {question_id!r}")
        return await self._get(
            f"/v1/answers/{question_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnswerGetResponse,
        )

    async def simulate(
        self,
        *,
        answers: answer_simulate_params.Answers,
        population_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponseListAnswers:
        """
        Simulates the answer to a new question.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/answers",
            body=await async_maybe_transform(
                {
                    "answers": answers,
                    "population_id": population_id,
                },
                answer_simulate_params.AnswerSimulateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponseListAnswers,
        )


class AnswersResourceWithRawResponse:
    def __init__(self, answers: AnswersResource) -> None:
        self._answers = answers

        self.benchmark = to_raw_response_wrapper(
            answers.benchmark,
        )
        self.get = to_raw_response_wrapper(
            answers.get,
        )
        self.simulate = to_raw_response_wrapper(
            answers.simulate,
        )


class AsyncAnswersResourceWithRawResponse:
    def __init__(self, answers: AsyncAnswersResource) -> None:
        self._answers = answers

        self.benchmark = async_to_raw_response_wrapper(
            answers.benchmark,
        )
        self.get = async_to_raw_response_wrapper(
            answers.get,
        )
        self.simulate = async_to_raw_response_wrapper(
            answers.simulate,
        )


class AnswersResourceWithStreamingResponse:
    def __init__(self, answers: AnswersResource) -> None:
        self._answers = answers

        self.benchmark = to_streamed_response_wrapper(
            answers.benchmark,
        )
        self.get = to_streamed_response_wrapper(
            answers.get,
        )
        self.simulate = to_streamed_response_wrapper(
            answers.simulate,
        )


class AsyncAnswersResourceWithStreamingResponse:
    def __init__(self, answers: AsyncAnswersResource) -> None:
        self._answers = answers

        self.benchmark = async_to_streamed_response_wrapper(
            answers.benchmark,
        )
        self.get = async_to_streamed_response_wrapper(
            answers.get,
        )
        self.simulate = async_to_streamed_response_wrapper(
            answers.simulate,
        )
