import os
import time
from typing import final

import flask

try:
    import requests
    from flask import request
except ImportError:
    raise ImportError(
        "Please install requests, werkzeug, and flask to use the adapter! pip install requests flask werkzeug"
    )

from .types import AdapterRequest, AdapterResponse, RequestInterceptor


@final
class NvcfEndpointInterceptor(RequestInterceptor):
    """Adapter for NVIDIA Cloud Function (NVCF) API."""

    _fetch_retries: int
    _nvcf_status_url: str

    api_url: str

    def __init__(self, api_url: str):
        """
        Initialize the NVCF adapter.

        Number of retries is controlled via env variables

        """

        # TODO(agronskiy): is it existing usecase that we set these parameters anywhere?
        self._fetch_retries = int(os.environ.get("NVCF_FETCH_RETRIES", 10))
        self._nvcf_status_url = os.environ.get(
            "NVCF_STATUS_URL", "https://api.nvcf.nvidia.com/v2/nvcf/pexec/status"
        )
        self.api_url = api_url

    @final
    def intercept_request(self, ar: AdapterRequest) -> AdapterResponse:
        """
        Handle the NVCF request with polling logic.

        Args:
            request_data: Preprocessed request data

        Returns:
            Response from NVCF API
        """
        try:
            headers = {k: v for k, v in ar.r.headers if k.lower() != "host"}
            # NOTE(dfridman): setting a higher nvcf-poll-seconds allows to reduce/avoid 202 and
            # later 408 after the maximum number of retries (e.g. self._fetch_retries)
            headers["NVCF-POLL-SECONDS"] = os.environ.get("NVCF_POLL_SECONDS", "60")
            response = requests.request(
                method=ar.r.method,
                url=self.api_url.rstrip(
                    "/"
                ),  # NVCF specifics: it does not work with `/` trailiing. We have to trim them
                headers=headers,
                json=ar.r.json,
                cookies=ar.r.cookies,
                allow_redirects=False,
            )

            # If not a 202 status code, return the response directly
            if response.status_code != 202:
                return AdapterResponse(
                    r=response,
                    meta=ar.meta,
                )

            # Handle polling logic
            fetch_retry_count = 0
            delay_seconds = 0.2
            multiplier = 1

            while (
                response.status_code == 202 and fetch_retry_count <= self._fetch_retries
            ):
                request_id = response.headers.get("NVCF-REQID")

                headers = {
                    "Authorization": ar.r.headers.get("Authorization"),
                    "Content-Type": "application/json",
                }
                if "NVCF-POLL-SECONDS" in ar.r.headers:
                    headers["NVCF-POLL-SECONDS"] = ar.r.headers.get("NVCF-POLL-SECONDS")

                response = requests.get(
                    url=f"{self._nvcf_status_url}/{request_id}",
                    headers=headers,
                )

                time.sleep(delay_seconds * multiplier)
                multiplier *= 2
                fetch_retry_count += 1

            if fetch_retry_count > self._fetch_retries:
                error_response = requests.Response()
                error_response.status_code = 408
                error_response._content = b"Request timed out"
                return AdapterResponse(r=error_response, meta=ar.meta)

            return AdapterResponse(
                r=response,
                meta=ar.meta,
            )

        except Exception as e:
            print(f"Error in handle_request: {e}")
            raise
