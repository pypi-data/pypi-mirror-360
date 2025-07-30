import gzip
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import AwareDatetime
from sh import Command, ErrorReturnCode

from daydream.plugins.aptible.logs.processing import (
    LOG_FILENAME_DATETIME_FORMAT,
    parse_log_line_timestamp,
)
from daydream.plugins.aptible.nodes.aptible_aws_instance import AptibleAwsInstance
from daydream.utils import print

if TYPE_CHECKING:
    from daydream.plugins.aptible.nodes.aptible_container import AptibleContainer


async def download_container_logs(
    stack: str,
    container: "AptibleContainer",
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
    download_dir: Path,
) -> int:
    # Stop if the container is no longer running - its logs will be in s3
    if container.raw_data["deleted_at"]:
        return 0

    # AWS Instance has the hostname of the container
    try:
        aws_instance = await anext(container.iter_neighboring(AptibleAwsInstance))
    except StopAsyncIteration:
        raise ValueError("Container has no parent AWS instance") from None

    print(
        f"Downloading container logs for {container.raw_data['docker_name']} "
        f"({aws_instance.raw_data['runtime_data']['hostname']} - {container.raw_data['layer']})"
    )

    # Download logs using pancake stack:ssh
    output_lines = await _log_lines_from_pancake(stack, container, aws_instance, start_dt, end_dt)
    if not output_lines:
        return 0

    # Write the log lines in the same format as s3 logs
    log_filename = _log_filename(container, download_dir, start_dt, end_dt)
    with gzip.open(log_filename, "wt") as f:
        for line in output_lines:
            try:
                dt, msg = line.split(" ", maxsplit=1)
                dt = parse_log_line_timestamp(dt)
                f.write(
                    json.dumps(
                        {
                            "time": dt.isoformat(),
                            "log": msg,
                        }
                    )
                    + "\n"
                )
            except ValueError:
                pass

    return 1


async def _log_lines_from_pancake(
    stack: str,
    container: "AptibleContainer",
    aws_instance: "AptibleAwsInstance",
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
) -> list[str]:
    output_lines = []
    try:
        pancake = Command(os.getenv("PANCAKE_PATH"))
        pancake_env = os.environ.copy().update(
            {
                "THOR_SILENCE_DEPRECATION": "1",
            }
        )

        output = await pancake(  # pyright: ignore [reportGeneralTypeIssues]
            "stack:ssh",
            stack,
            "--instance",
            aws_instance.raw_data["runtime_data"]["hostname"],
            "sudo",
            "docker",
            "container",
            "logs",
            container.raw_data["docker_name"],
            "--timestamps",
            "--since",
            start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "--until",
            end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            _async=True,
            _env=pancake_env,
        )
        output_lines = output.splitlines()
    except ErrorReturnCode as e:
        print(f"Error running command: {e}")

    if len(output_lines) > 0:
        # The first line is always "Executing '...'"
        del output_lines[0]

    return output_lines


def _log_filename(
    container: "AptibleContainer",
    download_dir: Path,
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
) -> Path:
    filename_tokens = [
        f"{container.raw_data['docker_name']}-json.log",
        start_dt.strftime(LOG_FILENAME_DATETIME_FORMAT),
        end_dt.strftime(LOG_FILENAME_DATETIME_FORMAT),
        "archived.gz",
    ]

    if container.raw_data["layer"] == "proxy":
        filename_tokens.insert(0, "proxy")

    return download_dir / ".".join(filename_tokens)
