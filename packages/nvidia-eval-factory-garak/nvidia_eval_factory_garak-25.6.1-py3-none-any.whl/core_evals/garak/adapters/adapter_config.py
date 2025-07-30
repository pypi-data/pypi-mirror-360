"""Submodule responsible for the configuration related specifically to adapters.

For the visibility reasons, we don't expose adapter configuration via CLI. All the
adaptor config comes from the framework configuration yaml under
```yaml
target:
  api_endpoint:
    adapter_config:
      use_response_logging: true
      use_reasoning: true
      use_nvcf: true
      use_request_caching: true
      caching_dir: /some/dir
```

This module merely takes such a dict and translates it into a typed dataclass.
"""

from typing import Any

from pydantic import BaseModel, Field


class AdapterConfig(BaseModel):

    @staticmethod
    def get_validated_config(run_config: dict[str, Any]) -> "AdapterConfig | None":
        """Factory. Shall return `None` if the adapter_config is not passed, or validate the schema.

        Args:
            run_config: is the main dict of a configuration run, see `api_dataclasses`.
        """
        # TODO(agronskiy, jira/COML1KNX-475), CAVEAT: adaptor will be bypassed alltogether in a rare
        # case when streaming is requested. See https://nvidia.slack.com/archives/C06QX6WQ30U/p1742451700506539 and
        # jira issue.
        if run_config.get("target", {}).get("api_endpoint", {}).get("stream", False):
            return None

        adapter_config = (
            run_config.get("target", {}).get("api_endpoint", {}).get("adapter_config")
        )
        if not adapter_config:
            return None

        adapter_config["endpoint_type"] = (
            run_config.get("target", {}).get("api_endpoint", {}).get("type", "")
        )

        return AdapterConfig.model_validate(adapter_config)

    endpoint_type: str = Field(
        description="Type of the endpoint to run the adapter for",
        default="chat",
    )

    use_response_logging: bool = Field(
        description="Whether to log endpoint responses",
        default=False,
    )

    max_logged_responses: int | None = Field(
        description="Maximum number of responses to log. If None, all responses will be logged.",
        default=None,
    )

    use_reasoning: bool = Field(
        description="Whether to use the reasoning adapter",
        default=False,
    )

    end_reasoning_token: str = Field(
        description="Token that singifies the end of reasoning output",
        default="</think>",
    )

    use_nvcf: bool = Field(
        description="Whether to use the NVCF endpoint adapter",
        default=False,
    )

    reuse_cached_responses: bool = Field(
        description="Whether to reuse cached responses. When enabled, it cache responses and will return cached responses",
        default=False,
    )

    save_responses: bool = Field(
        description="Whether to save responses to cache. When enabled, successful responses will be cached.",
        default=True,
    )

    caching_dir: str | None = Field(
        description="Directory for adapter cache storage (optional)",
        default=None,
    )

    save_requests: bool = Field(
        description="Whether to save requests.",
        default=False,
    )

    max_saved_requests: int | None = Field(
        description="Maximum number of requests to save. If None, no limit is applied. Thi",
        default=5,
    )

    max_saved_responses: int | None = Field(
        description="Maximum number of responses to save. If None, no limit is applied. This limit is only applied when save_requests is True",
        default=None,
    )

    generate_html_report: bool = (
        Field(
            description="Whether to generate an HTML report of cached requests and responses",
            default=False,
        ),
    )
    use_system_prompt: bool = Field(
        description="Whether to use custom system prompt adapter", default=False
    )

    custom_system_prompt: str = Field(
        description="A custom system prompt to replace original one", default=""
    )

    use_omni_info: bool = Field(
        description="Whether to collect the /omni/info information"
        " (if endpoint inoperative, the interceptor will not crash)",
        default=True,
    )

    custom_api_format: str = Field(
        description="Convert from 3P API format to NIM-compatible if applicable",
        default="nim",
    )

    params_to_remove: list[str] | None = Field(
        description="list of parameters to remove from the request payload",
        default=None,
    )

    params_to_add: dict[str, Any] | None = Field(
        description="dictionary of parameters to add to the request payload. Values must be JSON serializable.",
        default=None,
    )

    params_to_rename: dict[str, str] | None = Field(
        description="dictionary mapping old parameter names to new ones", default=None
    )

    use_request_logging: bool = Field(
        description="Whether to log requests",
        default=False,
    )

    progress_tracking_url: str = Field(
        description="URL for the POST endpoint to send the progress status to",
        default="",
    )

    progress_tracking_interval: int = Field(
        description="The progress tracking information should be sent every n steps defined by this param",
        default=50,
    )

    max_logged_requests: int | None = Field(
        description="Maximum number of requests to log. If None, all requests will be logged.",
        default=2,
    )

    log_failed_requests: bool = Field(
        description="Whether to log failed request-response pairs (status code >= 400)",
        default=True,
    )
