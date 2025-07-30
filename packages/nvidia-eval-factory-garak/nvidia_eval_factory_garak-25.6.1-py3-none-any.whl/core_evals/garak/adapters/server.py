"""Main server holding entry-point to all the interceptors.

The arch is as follows:


         ┌─────────────────────┐
         │                     │
         │  core-eval harness  │
         │                     │
         └───▲──────┬──────────┘
             │      │
     returns │      │
             │      │ calls
             │      │
             │      │
         ┌───┼──────┼──────────────────────────────────────────────────┐
         │   │      ▼                                                  │
         │ AdapterServer (@ localhost:3825)                            │
         │                                                             │
         │   ▲      │       chain of RequestInterceptors:              │
         │   │      │       flask.Request                              │
         │   │      │       is passed on the way up                    │
         │   │      │                                                  │   ┌──────────────────────┐
         │   │ ┌────▼───────────────────────────────────────────────┐  │   │                      │
         │   │ │intcptr_1─────►intcptr_2───►...───►intcptr_N────────┼──┼───►                      │
         │   │ │                     │                              │  │   │                      │
         │   │ └─────────────────────┼──────────────────────────────┘  │   │                      │
         │   │                       │(e.g. for caching interceptors,  │   │  upstream endpoint   │
         │   │                       │ this "shortcut" will happen)    │   │   with actual model  │
         │   │                       │                                 │   │                      │
         │   │                       └─────────────┐                   │   │                      │
         │   │                                     │                   │   │                      │
         │ ┌─┼─────────────────────────────────────▼────┐              │   │                      │
         │ │intcptr'_M◄──intcptr'_2◄──...◄───intcptr'_1 ◄──────────────┼───┤                      │
         │ └────────────────────────────────────────────┘              │   └──────────────────────┘
         │                                                             │
         │              Chain of ResponseInterceptors:                 │
         │              requests.Response is passed on the way down    │
         │                                                             │
         │                                                             │
         └─────────────────────────────────────────────────────────────┘

In other words, interceptors are pieces of independent logic which should be
relatively easy to add separately.



"""

import json
import os
from pathlib import Path

import flask
import requests
import structlog
import werkzeug.serving

from .adapter_config import AdapterConfig
from .interceptors import (
    AdapterMetadata,
    AdapterRequest,
    AdapterResponse,
    CachingInterceptor,
    CohereEndpointInterceptor,
    EndpointInterceptor,
    NvcfEndpointInterceptor,
    OmniInfoInterceptor,
    PayloadParamsModifierInterceptor,
    ProgressTrackingInterceptor,
    RequestInterceptor,
    RequestLoggingInterceptor,
    ResponseInterceptor,
    ResponseLoggingInterceptor,
    ResponseReasoningInterceptor,
    SystemMessageInterceptor,
)
from .interceptors.logging_interceptor import _get_safe_headers
from .reports.report_generator import ReportGenerator

logger = structlog.get_logger(__name__)


class AdapterServer:
    """Main server which serves on a local port and holds chain of interceptors"""

    DEFAULT_ADAPTER_HOST: str = "localhost"
    DEFAULT_ADAPTER_PORT: int = 3825

    adapter_host: str
    adapter_port: int

    request_interceptors: list[RequestInterceptor]
    response_interceptors: list[ResponseInterceptor]

    app: flask.Flask

    api_url: str
    output_dir: str

    def __init__(
        self,
        api_url: str,
        output_dir: str,
        adapter_config: AdapterConfig,
    ):
        """
        Initializes the app, creates server and adds interceptors

        Args:
            adapter_config: should be obtained from the main framework config, see `adapter_config.py`
        """

        self.request_interceptors = []
        self.response_interceptors = []

        self.app = flask.Flask(__name__)
        self.app.route("/", defaults={"path": ""}, methods=["POST"])(self._handler)
        self.app.route("/<path:path>", methods=["POST"])(self._handler)

        self.adapter_host: str = os.environ.get(
            "ADAPTER_HOST", self.DEFAULT_ADAPTER_HOST
        )
        self.adapter_port: int = int(
            os.environ.get("ADAPTER_PORT", self.DEFAULT_ADAPTER_PORT)
        )

        self.api_url = api_url
        self.adapter_config = adapter_config
        self.output_dir = output_dir

        logger.info("Using the following adapter config: %s", adapter_config)

        self._build_interceptor_chains(
            endpoint_type=adapter_config.endpoint_type,
            reuse_cached_responses=adapter_config.reuse_cached_responses,
            caching_dir=adapter_config.caching_dir,
            use_reasoning=adapter_config.use_reasoning,
            end_reasoning_token=adapter_config.end_reasoning_token,
            use_response_logging=adapter_config.use_response_logging,
            use_request_logging=adapter_config.use_request_logging,
            use_nvcf=adapter_config.use_nvcf,
            save_requests=adapter_config.save_requests,
            save_responses=adapter_config.save_responses,
            max_saved_requests=adapter_config.max_saved_requests,
            max_saved_responses=adapter_config.max_saved_responses,
            use_custom_system_prompt=adapter_config.use_system_prompt,
            custom_system_prompt=adapter_config.custom_system_prompt,
            custom_api_format=adapter_config.custom_api_format,
            use_omni_info=adapter_config.use_omni_info,
            progress_tracking_url=adapter_config.progress_tracking_url,
            progress_tracking_interval=adapter_config.progress_tracking_interval,
            max_logged_requests=adapter_config.max_logged_requests,
            max_logged_responses=adapter_config.max_logged_responses,
        )

    def _build_interceptor_chains(
        self,
        endpoint_type: str,
        reuse_cached_responses: bool,
        caching_dir: str,
        use_reasoning: bool,
        end_reasoning_token: str,
        use_response_logging: bool,
        use_request_logging: bool,
        use_nvcf: bool,
        use_custom_system_prompt: bool,
        custom_system_prompt: str,
        custom_api_format: str,
        use_omni_info: bool,
        progress_tracking_url: str,
        progress_tracking_interval: int,
        save_requests: bool = False,
        save_responses: bool = True,
        max_saved_requests: int | None = None,
        max_saved_responses: int | None = None,
        max_logged_requests: int | None = None,
        max_logged_responses: int | None = None,
    ):

        if endpoint_type == "embedding":
            if custom_api_format == "cohere":
                self.request_interceptors.append(
                    CohereEndpointInterceptor(api_url=self.api_url)
                )
            else:
                self.request_interceptors.append(
                    EndpointInterceptor(api_url=self.api_url)
                )
        else:
            if use_custom_system_prompt:
                self.request_interceptors.append(
                    SystemMessageInterceptor(new_system_message=custom_system_prompt)
                )
            if use_omni_info:
                self.request_interceptors.append(
                    OmniInfoInterceptor(
                        api_url=self.api_url, output_dir=self.output_dir
                    )
                )

            if (
                self.adapter_config.params_to_remove
                or self.adapter_config.params_to_add
                or self.adapter_config.params_to_rename
            ):
                self.request_interceptors.append(
                    PayloadParamsModifierInterceptor(
                        params_to_remove=self.adapter_config.params_to_remove,
                        params_to_add=self.adapter_config.params_to_add,
                        params_to_rename=self.adapter_config.params_to_rename,
                    )
                )

            if use_request_logging:
                self.request_interceptors.append(
                    RequestLoggingInterceptor(
                        output_dir=self.output_dir, max_requests=max_logged_requests
                    )
                )
            cache_interceptor = None
            if reuse_cached_responses or save_requests or save_responses:
                cache_interceptor = CachingInterceptor(
                    cache_dir=caching_dir,
                    reuse_cached_responses=reuse_cached_responses,
                    save_requests=save_requests,
                    save_responses=save_responses or reuse_cached_responses,
                    max_saved_requests=max_saved_requests,
                    max_saved_responses=(
                        max_saved_responses if not reuse_cached_responses else None
                    ),
                )
                self.request_interceptors.append(cache_interceptor)
            if use_nvcf:
                self.request_interceptors.append(
                    NvcfEndpointInterceptor(api_url=self.api_url)
                )
            else:
                self.request_interceptors.append(
                    EndpointInterceptor(api_url=self.api_url)
                )

            # reverse
            if cache_interceptor:
                self.response_interceptors.append(cache_interceptor)
            if use_response_logging:
                self.response_interceptors.append(
                    ResponseLoggingInterceptor(max_responses=max_logged_responses)
                )
            if use_reasoning:
                self.response_interceptors.append(
                    ResponseReasoningInterceptor(
                        end_reasoning_token=end_reasoning_token
                    )
                )
            if progress_tracking_url:
                self.response_interceptors.append(
                    ProgressTrackingInterceptor(
                        progress_tracking_url=progress_tracking_url,
                        progress_tracking_interval=progress_tracking_interval,
                    )
                )

    def run(self) -> None:
        """Start the Flask server."""
        werkzeug.serving.run_simple(
            hostname=self.adapter_host,
            port=self.adapter_port,
            application=self.app,
            threaded=True,
        )

    # The headers we don't want to let out
    _EXCLUDED_HEADERS = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]

    @classmethod
    def _process_response_headers(
        cls, response: requests.Response
    ) -> list[tuple[str, str]]:
        """Process response headers, removing excluded ones."""
        return [
            (k, v)
            for k, v in response.headers.items()
            if k.lower() not in cls._EXCLUDED_HEADERS
        ]

    def _handler(self, path: str) -> flask.Response:
        adapter_request = AdapterRequest(
            r=flask.request,
            meta=AdapterMetadata(),
        )
        adapter_response = None
        for interceptor in self.request_interceptors:
            output = interceptor.intercept_request(adapter_request)

            if isinstance(output, AdapterResponse):
                adapter_response = output
                break
            if isinstance(output, AdapterRequest):
                adapter_request = output

        # TODO(agronskiy): asserts in prod are bad, make this more elegant.
        assert adapter_response is not None, "There should be a response to process"

        # Log failed responses if enabled
        if (
            self.adapter_config.log_failed_requests
            and adapter_response.r.status_code >= 400
        ):
            log_data = {
                "error": {
                    "request": {
                        "url": self.api_url,
                        "body": adapter_request.r.get_json(),
                        "headers": _get_safe_headers(adapter_request.r.headers),
                    },
                    "response": {
                        "status_code": adapter_response.r.status_code,
                        "headers": _get_safe_headers(adapter_response.r.headers),
                        "body": adapter_response.r.content.decode(
                            "utf-8", errors="ignore"
                        ),
                    },
                }
            }
            logger.error("failed_request_response_pair", data=log_data)

        for interceptor in self.response_interceptors:
            try:
                adapter_response = interceptor.intercept_response(adapter_response)
            except Exception as e:
                self._log_response_interceptor_error(interceptor, adapter_response, e)
                raise

        return flask.Response(
            response=adapter_response.r.content,
            status=adapter_response.r.status_code,
            headers=self._process_response_headers(adapter_response.r),
        )

    def generate_report(self) -> None:
        """Generate HTML report of cached requests and responses."""
        if (
            not (
                self.adapter_config.reuse_cached_responses
                or self.adapter_config.save_requests
                or self.adapter_config.save_responses
            )
            or not self.adapter_config.generate_html_report
        ):
            return

        report_generator = ReportGenerator(
            self.adapter_config.caching_dir, self.api_url
        )
        report_path = Path(self.adapter_config.caching_dir) / "cache_report.html"
        report_generator.generate_report(str(report_path))
        if report_path.exists():
            print(f"Cache report generated at: {report_path}")

    def _log_response_interceptor_error(
        self,
        interceptor: ResponseInterceptor,
        adapter_response: AdapterResponse,
        error: Exception,
    ) -> None:
        error_message = (
            f"❌ Error in Response Interceptor ❌\n"
            f"Interceptor: {interceptor.__class__.__name__}\n"
            f"Adapter Response Status Code: {adapter_response.r.status_code}\n"
            f"Adapter Response Status Text: {adapter_response.r.reason}\n"
            f"Adapter Response Content: {adapter_response.r.content.decode('utf-8', errors='ignore')}\n"
            f"Error Details: {repr(error)}\n"
        )
        logger.error(error_message)
