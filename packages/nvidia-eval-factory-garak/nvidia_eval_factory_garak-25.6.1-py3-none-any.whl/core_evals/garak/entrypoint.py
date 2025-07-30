import argparse
import json
import logging
import multiprocessing
import os
import sys
import threading
import time
from pathlib import Path

import psutil
import yaml

from .adapters.adapter_config import AdapterConfig

# NOTE(dfridman): will be removed once all benchmarks comply with updated output format
from .api_dataclasses import EvaluationConfig, EvaluationResult, EvaluationTarget
from .evaluate import evaluate_accuracy
from .input import (
    get_available_evaluations,
    load_run_config,
    parse_cli_args,
    validate_evaluation,
)
from .utils import MisconfigurationError, deep_update, get_token_usage_from_cache_db

# Note: When using spawn, Python cannot pickle certain objects including:
# - Lambda functions
# - Local functions
# - Functions defined in __main__
# - Functions with closures
# - Objects with unpicklable attributes
# The default start method for multiprocessing on macOS is spawn, which is why we explicitly
# set the start method to "fork" to avoid these limitations when running on macOS.
multiprocessing.set_start_method("fork")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="Debug the core_evals script"
    )
    subparsers = parser.add_subparsers(help="Functions")
    parser_ls = subparsers.add_parser("ls", help="List available evaluation types")
    parser_ls.set_defaults(command="ls")

    parser_run = subparsers.add_parser("run_eval", help="Run the evaluation")
    parser_run.add_argument("--eval_type", type=str, help="Run config.: task name")
    parser_run.add_argument("--model_id", type=str, help="Run config.: model name")
    parser_run.add_argument(
        "--model_type",
        type=str,
        help="Run config.: endpoint type",
        choices=["chat", "completions", "vlm", "embedding"],
    )
    parser_run.add_argument("--model_url", type=str, help="Run config.: model URI")
    parser_run.add_argument(
        "--output_dir", type=str, help="Run config.: results output dir."
    )
    parser_run.add_argument(
        "--api_key_name",
        type=str,
        help="Run config.: API key env variable name (optional)",
        default=None,
    )
    parser_run.add_argument(
        "--run_config",
        type=str,
        help="Load the run configuration from the YAML file (optional and overridden by the cli arguments)",
        default=None,
    )
    parser_run.add_argument(
        "--overrides",
        type=str,
        help="Comma-separated dot-style parameters to override config values (overriding values from run_config and CLI args)",
        default=None,
    )
    parser_run.add_argument(
        "--dry_run",
        action="store_true",
        help="Shows rendered config and command instead of running",
        default=False,
    )
    parser_run.set_defaults(command="run_eval")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if "command" not in args:
        parser.print_help()
        sys.exit(0)
    return args


def show_available_tasks() -> None:
    _, eval_name_mapping, _ = get_available_evaluations()
    print("Available tasks:")
    for evaluation in sorted(
        eval_name_mapping.values(), key=lambda task: task.config.type
    ):
        print(f"* {evaluation.config.type} (in {evaluation.framework_name})")


def get_token_usage_from_cache(cache_dir: str) -> dict:
    """Extract token usage metrics from the cache database."""
    cache_db_path = Path(cache_dir) / "responses" / "cache.db"
    if not cache_db_path.exists():
        return {}

    return get_token_usage_from_cache_db(cache_db_path)


def monitor_memory_usage(func, *args, interval_ms, **kwargs):
    """
    Run func(*args, **kwargs) while polling RSS via psutil.
    Returns (func_return_value, peak_rss_bytes, peak_tree_rss_bytes) where:
    - peak_rss_bytes: peak memory usage of the main process
    - peak_tree_rss_bytes: peak memory usage of the entire process tree (main + children)
    """
    proc = psutil.Process(os.getpid())
    peak = 0
    peak_tree = 0
    stop = False
    ret = None

    def get_tree_memory(process):
        """Get total memory usage of process and all its children."""
        try:
            memory = process.memory_info().rss
            for child in process.children(recursive=True):
                try:
                    memory += child.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return memory
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0

    def sampler():
        nonlocal peak, peak_tree
        while not stop:
            # Get memory for current process
            rss = proc.memory_info().rss
            peak = max(peak, rss)

            # Get memory for entire process tree
            tree_rss = get_tree_memory(proc)
            peak_tree = max(peak_tree, tree_rss)

            time.sleep(interval_ms / 1000.0)

    th = threading.Thread(target=sampler, daemon=True)
    th.start()
    try:
        ret = func(*args, **kwargs)
    finally:
        stop = True  # thread safe
        th.join()

    return ret, peak, peak_tree


def run_evaluation(args) -> None:
    run_config = load_run_config(args.run_config) if args.run_config else {}
    # CLI args take precedence over YAML run config
    run_config = deep_update(run_config, parse_cli_args(args), skip_nones=True)

    # TODO: these checks should FIRST complete a merge with the benchmark defaults, and THEN check for the missing fields
    if run_config["config"].get("type") is None:
        raise MisconfigurationError(
            f"Missing required argument: config.type (cli: --eval_type)"
        )
    if args.dry_run:
        evaluation = validate_evaluation(run_config)
        print("Rendered config:\n")
        config = evaluation.model_dump()
        print(yaml.dump(config, sort_keys=False, default_flow_style=False, indent=2))
        print("\nRendered command:\n")
        cmd = evaluation.render_command()
        print(cmd)
        exit(0)

    # If adapter is not configured either via yaml or --overrides, it's disabled
    adapter_config: AdapterConfig | None = AdapterConfig.get_validated_config(
        run_config
    )
    adapter = None

    if run_config["config"].get("output_dir") is None:
        raise MisconfigurationError(
            f"Missing required argument: config.output_dir (cli: --output_dir)"
        )
    output_dir = run_config["config"]["output_dir"]

    if adapter_config:
        if run_config["target"].get("api_endpoint") is None:
            raise MisconfigurationError(
                f"You need to define target.api_endpoint in order to use an adapter (cli: --model_id, --model_url, --model_type)"
            )
        if run_config["target"]["api_endpoint"].get("url") is None:
            raise MisconfigurationError(
                f"You need to define target.api_endpoint.url in order to use an adapter (cli: --model_url)"
            )

        # Set caching_dir based on output_dir if not explicitly set
        if adapter_config.caching_dir is None:
            adapter_config.caching_dir = os.path.join(output_dir, "cache")

        from .adapters.server import AdapterServer

        adapter = AdapterServer(
            api_url=run_config["target"]["api_endpoint"]["url"],
            output_dir=output_dir,
            adapter_config=adapter_config,
        )
        p: multiprocessing.Process | None = multiprocessing.Process(target=adapter.run)
        # This will be unhooked below
        run_config["target"]["api_endpoint"][
            "url"
        ] = f"http://{adapter.adapter_host}:{adapter.adapter_port}"
        p.start()

    eval_cfg = EvaluationConfig(**run_config["config"])
    target_cfg = EvaluationTarget(**run_config["target"])

    def run_evaluation_core():
        result = None
        try:
            result = evaluate_accuracy(eval_cfg, target_cfg)
        finally:
            # TODO(agronskiy): remove this logic once the streaming based disable works (see jira/COML1KNX-475)
            if adapter_config and p.is_alive():
                if adapter_config.generate_html_report:
                    adapter.generate_report()
                p.terminate()
        return result

    start_time = time.time()
    evaluation_result, peak_memory_bytes, peak_tree_memory_bytes = monitor_memory_usage(
        run_evaluation_core, interval_ms=100
    )

    end_time = time.time()
    runtime_seconds = end_time - start_time

    # Save runtime metrics
    metrics = {
        "runtime_seconds": runtime_seconds,
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime(start_time)),
        "end_time": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime(end_time)),
        "token_usage": None,  # Default to None
        "peak_memory_bytes": peak_memory_bytes,  # Memory of main process
        "peak_tree_memory_bytes": peak_tree_memory_bytes,  # Memory of entire process tree
    }

    if adapter_config and adapter_config.caching_dir:
        # Get token usage from cache if it exists
        token_usage = get_token_usage_from_cache(adapter_config.caching_dir)
        metrics["token_usage"] = token_usage if token_usage else None

    metrics_path = os.path.join(eval_cfg.output_dir, "eval_factory_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    if isinstance(evaluation_result, EvaluationResult):
        evaluation_result_dict = evaluation_result.model_dump(exclude_none=True)
    else:
        logging.warning("Deprecated output API is used. Will be updated soon.")
        evaluation_result_dict = evaluation_result

    run_command = validate_evaluation(
        {"config": eval_cfg.model_dump(), "target": target_cfg.model_dump()}
    ).render_command()

    # NOTE(agronskiy): for result logging purposes and for keepiing the config intact, we hook the
    # actual upstream api endpoint back, to avoid logging useless `localhost:xxxx`.
    if adapter:
        run_config["target"]["api_endpoint"]["url"] = adapter.api_url

    evaluation_result_dict = {
        "git_hash": os.getenv("CORE_EVALS_GIT_HASH"),
        "command": run_command,
        **run_config,
        "results": evaluation_result_dict,
    }
    with open(os.path.join(eval_cfg.output_dir, "results.yml"), "w") as f:
        yaml.dump(evaluation_result_dict, f)

    print("========== RESULTS ==========")
    print(yaml.dump(evaluation_result_dict))


def run_eval() -> None:
    args = get_args()

    if args.command == "ls":
        show_available_tasks()
    elif args.command == "run_eval":
        run_evaluation(args)


if __name__ == "__main__":
    run_eval()
