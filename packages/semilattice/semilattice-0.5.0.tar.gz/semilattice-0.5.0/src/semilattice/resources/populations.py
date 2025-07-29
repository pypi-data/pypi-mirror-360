# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, Optional, cast

import httpx

from ..types import population_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.api_response import APIResponse

__all__ = ["PopulationsResource", "AsyncPopulationsResource"]


class PopulationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PopulationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PopulationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PopulationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return PopulationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        seed_data: FileTypes,
        simulation_engine: str,
        simulation_options: str,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        reality_target: Optional[str] | NotGiven = NOT_GIVEN,
        run_test: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponse:
        """
        Creates a new population model.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "name": name,
                "seed_data": seed_data,
                "simulation_engine": simulation_engine,
                "simulation_options": simulation_options,
                "description": description,
                "reality_target": reality_target,
                "run_test": run_test,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["seed_data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/v1/populations",
            body=maybe_transform(body, population_create_params.PopulationCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponse,
        )

    def get(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponse:
        """
        Fetches a population, along with its status, accuracy metrics, and other
        metadata.

        Args:
          population_id: ID of the population to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return self._get(
            f"/v1/populations/{population_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponse,
        )

    def test(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponse:
        """
        Triggers an accuracy test for a population model, if not yet tested.

        Args:
          population_id: ID of the population to test.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return self._post(
            f"/v1/populations/{population_id}/test",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponse,
        )


class AsyncPopulationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPopulationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPopulationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPopulationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/semilattice-research/semilattice-sdk-python#with_streaming_response
        """
        return AsyncPopulationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        seed_data: FileTypes,
        simulation_engine: str,
        simulation_options: str,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        reality_target: Optional[str] | NotGiven = NOT_GIVEN,
        run_test: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponse:
        """
        Creates a new population model.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "name": name,
                "seed_data": seed_data,
                "simulation_engine": simulation_engine,
                "simulation_options": simulation_options,
                "description": description,
                "reality_target": reality_target,
                "run_test": run_test,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["seed_data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/v1/populations",
            body=await async_maybe_transform(body, population_create_params.PopulationCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponse,
        )

    async def get(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponse:
        """
        Fetches a population, along with its status, accuracy metrics, and other
        metadata.

        Args:
          population_id: ID of the population to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return await self._get(
            f"/v1/populations/{population_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponse,
        )

    async def test(
        self,
        population_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIResponse:
        """
        Triggers an accuracy test for a population model, if not yet tested.

        Args:
          population_id: ID of the population to test.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not population_id:
            raise ValueError(f"Expected a non-empty value for `population_id` but received {population_id!r}")
        return await self._post(
            f"/v1/populations/{population_id}/test",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIResponse,
        )


class PopulationsResourceWithRawResponse:
    def __init__(self, populations: PopulationsResource) -> None:
        self._populations = populations

        self.create = to_raw_response_wrapper(
            populations.create,
        )
        self.get = to_raw_response_wrapper(
            populations.get,
        )
        self.test = to_raw_response_wrapper(
            populations.test,
        )


class AsyncPopulationsResourceWithRawResponse:
    def __init__(self, populations: AsyncPopulationsResource) -> None:
        self._populations = populations

        self.create = async_to_raw_response_wrapper(
            populations.create,
        )
        self.get = async_to_raw_response_wrapper(
            populations.get,
        )
        self.test = async_to_raw_response_wrapper(
            populations.test,
        )


class PopulationsResourceWithStreamingResponse:
    def __init__(self, populations: PopulationsResource) -> None:
        self._populations = populations

        self.create = to_streamed_response_wrapper(
            populations.create,
        )
        self.get = to_streamed_response_wrapper(
            populations.get,
        )
        self.test = to_streamed_response_wrapper(
            populations.test,
        )


class AsyncPopulationsResourceWithStreamingResponse:
    def __init__(self, populations: AsyncPopulationsResource) -> None:
        self._populations = populations

        self.create = async_to_streamed_response_wrapper(
            populations.create,
        )
        self.get = async_to_streamed_response_wrapper(
            populations.get,
        )
        self.test = async_to_streamed_response_wrapper(
            populations.test,
        )
