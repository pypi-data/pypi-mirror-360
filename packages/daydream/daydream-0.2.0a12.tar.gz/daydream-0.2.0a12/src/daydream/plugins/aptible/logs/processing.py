import gzip
import re
from datetime import UTC, datetime
from functools import partial
from multiprocessing import Pool, cpu_count
from pathlib import Path

import msgspec
from pydantic import AwareDatetime

from daydream.models import LogLine

LOG_FILENAME_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_log_line_timestamp(ts: str) -> AwareDatetime:
    ts_parts = ts.split(".")

    if len(ts_parts) == 2:
        base, nanos = ts_parts
        micros = (nanos[:-1] + "000000")[:6]  # Remove Z, pad/truncate to 6 digits
        ts_fixed = f"{base}.{micros}Z"
        dt = datetime.strptime(ts_fixed, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

    # Make the datetime timezone-aware by assuming UTC
    return dt.replace(tzinfo=UTC)


def process_log_files(
    input_log_filenames: list[Path],
    output_log_filename: Path,
    output_http_log_filename: Path,
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
) -> None:
    """
    Processes a list of log files, in parallel, and writes them to the
    output files.
    """
    process_fn = partial(
        process_single_log_file,
        output_log_filename=output_log_filename,
        output_http_log_filename=output_http_log_filename,
        start_dt=start_dt,
        end_dt=end_dt,
    )

    # Process log files in parallel using all but one CPU core
    num_processes = max(1, cpu_count() - 1)
    with Pool(num_processes) as pool:
        pool.map(process_fn, input_log_filenames)


def process_single_log_file(
    log_filename: Path,
    output_log_filename: Path,
    output_http_log_filename: Path,
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
) -> None:
    """
    Determines the type of log and parses it accordingly. Writes the parsed
    log lines to the output file.
    """
    if "proxy" in str(log_filename):
        parse_fn = parse_http_log_line
        output_filename = output_http_log_filename
    else:
        parse_fn = parse_log_line
        output_filename = output_log_filename

    with (
        gzip.open(log_filename, "rt") as input_file,
        Path.open(output_filename, "a") as output_file,
    ):
        for line in input_file:
            parsed = parse_fn(line, start_dt, end_dt)
            if parsed:
                output_file.write(msgspec.json.encode(parsed).decode() + "\n")


def parse_log_line(line: str, start_dt: AwareDatetime, end_dt: AwareDatetime) -> LogLine | None:
    """
    Container logs are already in the correct LogLine format, so parse them
    using msgspec and return them if they are within the time range desired.
    """
    try:
        parsed: LogLine = msgspec.json.decode(line, type=LogLine)
        if start_dt <= parsed.time <= end_dt:
            return parsed
    except (msgspec.DecodeError, ValueError):
        return None


def parse_http_log_line(
    line: str, start_dt: AwareDatetime, end_dt: AwareDatetime
) -> LogLine | None:
    """
    HTTP logs are processed further to extract the method and path, while
    ignoring the rest of the log line (things like IP, user agent, etc) which
    can confuse the template miner.
    """
    try:
        parsed: LogLine = msgspec.json.decode(line, type=LogLine)
        if start_dt <= parsed.time <= end_dt:
            quoted_strings = re.findall(r'"([^"]*)"', parsed.log)
            method_path = quoted_strings[0].lower().split(" http")[0]
            parsed.log = method_path
            return parsed
    except (msgspec.DecodeError, ValueError):
        return None
