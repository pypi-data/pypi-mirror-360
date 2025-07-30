import asyncio
import random
import re
import shutil
import warnings
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import msgspec
from pydantic import AwareDatetime

from daydream.models import LogLine
from daydream.plugins.aptible.logs.processing import LOG_FILENAME_DATETIME_FORMAT
from daydream.plugins.aptible.nodes.base import AptibleNode

from .container import download_container_logs
from .processing import process_log_files
from .s3 import download_s3_logs, get_log_bucket_config

if TYPE_CHECKING:
    from daydream.plugins.aptible.nodes.aptible_container import AptibleContainer


LOGS_DIR = Path.home() / ".daydream" / "logs"
LOG_FILENAME_PATTERN = re.compile(r"^.*\.archived\.gz$")
PROCESSED_LOGS_FILENAME = "logs.jsonl"
PROCESSED_HTTP_LOGS_FILENAME = "http-logs.jsonl"
MAX_CONTAINERS_BEFORE_SAMPLING = 20
INITIAL_DOWNLOAD_ATTEMPTS = 2
MAX_CONCURRENT_CONTAINER_DOWNLOADS = 3
MAX_CONCURRENT_S3_DOWNLOADS = 20
MAX_EMPTY_DOWNLOADS = 2


class DownloadMonitor:
    downloads: int
    none_found: int

    def __init__(self) -> None:
        self.downloads = 0
        self.none_found = 0


async def download_logs_for_time_range(
    stack: str,
    node: AptibleNode,
    containers: list["AptibleContainer"],
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
) -> list[LogLine]:
    """
    Download logs for a given time range.

    Logs are downloaded from S3 and from live containers in parallel. Once
    downloaded, they are processed and cached.

    Returns a list of LogLine objects.
    """
    # Create a directory to store the logs
    log_dir = _log_directory_name(stack, node, start_dt, end_dt)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filename = log_dir / PROCESSED_LOGS_FILENAME
    http_log_filename = log_dir / PROCESSED_HTTP_LOGS_FILENAME

    # Check for cached logs first, which are pre-processed and ready to go.
    # Otherwise, download the logs and process them.
    if not _log_files_downloaded(log_dir):
        tmp_download_dir = await download_s3_and_container_logs(
            stack, containers, start_dt, end_dt, log_dir
        )

        relevant_log_files = _log_files_for_time_range(tmp_download_dir, start_dt, end_dt)
        process_log_files(relevant_log_files, log_filename, http_log_filename, start_dt, end_dt)
        shutil.rmtree(tmp_download_dir)

    # Read processed container & HTTP logs into a list of LogLine objects
    log_lines: list[LogLine] = []

    if log_filename.exists():
        with Path.open(log_filename, "r") as f:
            log_lines.extend(msgspec.json.decode(line, type=LogLine) for line in f)

    if http_log_filename.exists():
        with Path.open(http_log_filename, "r") as f:
            log_lines.extend(msgspec.json.decode(line, type=LogLine) for line in f)

    return log_lines


async def download_s3_and_container_logs(
    stack: str,
    containers: list["AptibleContainer"],
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
    log_dir: Path,
) -> Path:
    """
    Downloads logs from S3 and live containers in parallel into a temporary
    directory. Logs are split into app and proxy (vhost) logs.

    Downloads for a specific (source, container_layer) pair are monitored. If
    there are no logs from a source after MAX_EMPTY_DOWNLOADS, that means the
    logs are probably in another source, so we can stop early.

    The number of parallel downloads are limited by source, ie containers and
    s3 have their own semaphores.

    Returns the path to the temporary directory where logs were downloaded.
    """
    app_containers, proxy_containers = _prepare_containers(containers)
    bucket_config = await get_log_bucket_config(stack)

    # Download unprocessed logs to a temporary directory
    tmp_download_dir = log_dir / "tmp"
    tmp_download_dir.mkdir(parents=True, exist_ok=True)

    # Monitor downloads. If there are no logs from a source after
    # MAX_EMPTY_DOWNLOADS, that means the logs are probably in
    # another source, and we can stop early.
    monitor_app_container_downloads = generate_monitor_fn(DownloadMonitor())
    monitor_proxy_container_downloads = generate_monitor_fn(DownloadMonitor())
    monitor_app_s3_downloads = generate_monitor_fn(DownloadMonitor())
    monitor_proxy_s3_downloads = generate_monitor_fn(DownloadMonitor())

    # Create a semaphore to limit concurrent downloads by source
    container_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CONTAINER_DOWNLOADS)
    s3_semaphore = asyncio.Semaphore(MAX_CONCURRENT_S3_DOWNLOADS)

    # Download all logs in parallel. Concurrency is limited by source, ie
    # containers and s3 have their own semaphores. For each (source, container layer)
    # pair, we monitor for empty downloads and stop when we get > MAX_EMPTY_DOWNLOADS.
    # We do this because sometimes an app's logs are in one source, while its
    # proxy logs are in another, even for the same time range.
    await asyncio.gather(
        *(
            monitor_app_container_downloads(
                download_container_logs(stack, container, start_dt, end_dt, tmp_download_dir),
                container_semaphore,
            )
            for container in app_containers
        ),
        *(
            monitor_proxy_container_downloads(
                download_container_logs(stack, container, start_dt, end_dt, tmp_download_dir),
                container_semaphore,
            )
            for container in proxy_containers
        ),
        *(
            monitor_app_s3_downloads(
                download_s3_logs(
                    stack, container, start_dt, end_dt, tmp_download_dir, bucket_config
                ),
                s3_semaphore,
            )
            for container in app_containers
        ),
        *(
            monitor_proxy_s3_downloads(
                download_s3_logs(
                    stack, container, start_dt, end_dt, tmp_download_dir, bucket_config
                ),
                s3_semaphore,
            )
            for container in proxy_containers
        ),
    )

    return tmp_download_dir


def _prepare_containers(
    containers: list["AptibleContainer"],
) -> tuple[list["AptibleContainer"], list["AptibleContainer"]]:
    """
    Split containers into app and proxy containers. If there are too many
    containers, sample them.
    """
    if len(containers) > MAX_CONTAINERS_BEFORE_SAMPLING:
        containers = random.sample(containers, MAX_CONTAINERS_BEFORE_SAMPLING)

    app_containers = [c for c in containers if c.raw_data["layer"] == "app"]
    proxy_containers = [c for c in containers if c.raw_data["layer"] == "proxy"]
    return app_containers, proxy_containers


def generate_monitor_fn(
    monitor: DownloadMonitor,
) -> Callable[[Coroutine, asyncio.Semaphore], Coroutine[None, None, None]]:
    """
    Generate a function that monitors downloads for a given source, watching
    for empty downloads and limiting concurrent downloads with a semaphore.
    """

    async def monitor_downloads(coro: Coroutine, semaphore: asyncio.Semaphore) -> None:
        # Ignore warnings about the coroutine not being awaited when exiting early
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            async with semaphore:
                if (
                    monitor.downloads >= INITIAL_DOWNLOAD_ATTEMPTS
                    and monitor.none_found >= MAX_EMPTY_DOWNLOADS
                ):
                    return

                files_downloaded = await coro
                monitor.downloads += 1
                if files_downloaded == 0:
                    monitor.none_found += 1

    return monitor_downloads


def _log_directory_name(
    stack: str,
    node: AptibleNode,
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
) -> Path:
    return LOGS_DIR / "-".join(
        [
            stack,
            node.raw_data["_type"],
            node.node_id,
            start_dt.strftime(LOG_FILENAME_DATETIME_FORMAT),
            end_dt.strftime(LOG_FILENAME_DATETIME_FORMAT),
        ]
    )


def _log_files_downloaded(log_dir: Path) -> bool:
    return (log_dir / PROCESSED_LOGS_FILENAME).exists() or (
        log_dir / PROCESSED_HTTP_LOGS_FILENAME
    ).exists()


def _log_files_for_time_range(
    log_dir: Path, start_dt: AwareDatetime, end_dt: AwareDatetime
) -> list[Path]:
    """
    Downloads from S3 can only be limited by YYY-MM-DD, and so we have to download
    files for time_range + 1 day to make sure we have full coverage. To avoid
    unnecessary log file parsing, this function uses the time range from the
    filename to check for overlap first.
    """
    filenames = [
        f for f in log_dir.glob("**/*") if f.is_file() and LOG_FILENAME_PATTERN.match(f.name)
    ]
    matching_files = []
    for filename in filenames:
        dt_range = str(filename).split("json.log.")[1].replace(".archived.gz", "")
        dt_range = dt_range.removeprefix("1.")

        log_start, log_end = dt_range.split(".")
        log_start_dt = datetime.strptime(log_start, LOG_FILENAME_DATETIME_FORMAT).replace(
            tzinfo=UTC
        )
        log_end_dt = datetime.strptime(log_end, LOG_FILENAME_DATETIME_FORMAT).replace(tzinfo=UTC)

        # Check if the log file's time range overlaps with our target period
        if (
            (start_dt <= log_start_dt <= end_dt)
            or (start_dt <= log_end_dt <= end_dt)
            or (log_start_dt <= start_dt <= log_end_dt)
        ):
            matching_files.append(filename)

    return matching_files
