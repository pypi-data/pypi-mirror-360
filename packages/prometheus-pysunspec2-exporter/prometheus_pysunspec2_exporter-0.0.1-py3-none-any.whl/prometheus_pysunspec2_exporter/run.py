import sys
from argparse import ArgumentParser, FileType
import signal

import yaml

from prometheus_client.core import REGISTRY
from prometheus_client import (
    start_http_server,
    PROCESS_COLLECTOR,
    PLATFORM_COLLECTOR,
    GC_COLLECTOR,
)

from prometheus_pysunspec2_exporter.config import parse_config, ConfigError
from prometheus_pysunspec2_exporter.collector import SunSpecCollector


def run_exporter_until_terminated(*args, **kwargs) -> None:
    """
    Wrapper around :py:func:`prometheus_client.start_http_server` which runs
    the server until sigint (Ctrl+C) or sigterm at which point it shuts down
    the gracefully and returns.
    """
    server, thread = start_http_server(*args, **kwargs)
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda *_: server.shutdown())
    thread.join()


def main() -> None:
    parser = ArgumentParser(
        description="""
            A Sunspec Prometheus exporter.
        """
    )
    parser.add_argument(
        "config_file",
        type=FileType("r"),
        help="""
            YAML config file to read enumerating all the devices to poll.
        """,
    )
    parser.add_argument(
        "--address",
        "-a",
        type=str,
        default="0.0.0.0",
        help="""
            The Prometheus listen address. Default: %(default)s.
        """,
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=9502,
        help="""
            The Prometheus listen port. Default: %(default)s.
        """,
    )
    args = parser.parse_args()

    try:
        config = yaml.safe_load(args.config_file)
        clients = parse_config(config)
    except (ConfigError, yaml.error.YAMLError) as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        sys.exit(1)

    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.register(SunSpecCollector(clients))

    run_exporter_until_terminated(port=args.port, addr=args.address)
