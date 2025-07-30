import os
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import AwareDatetime, BaseModel
from sh import Command, ErrorReturnCode

from daydream.utils import print

if TYPE_CHECKING:
    from daydream.plugins.aptible.nodes.aptible_container import AptibleContainer

S3_LOGS_DATE_FORMAT = "%Y-%m-%d"
SWEETNESS_LOG_BUCKET_NAME_SETTING = "sweetness/nonsensitive/DOCKER_LOGS_BUCKET_NAME"
SWEETNESS_LOG_ENCRYPTION_KEYS_SETTING = "sweetness/sensitive/LOG_ENCRYPTION_KEYS"
NO_FILES_FOUND_ERROR = "No files found that matched all criteria"


class LogBucketConfig(BaseModel):
    bucket_name: str
    region: str
    decryption_keys: str


async def get_log_bucket_config(stack: str) -> LogBucketConfig:
    log_bucket = await get_pancake_setting(stack, SWEETNESS_LOG_BUCKET_NAME_SETTING)
    log_encryption_keys = await get_pancake_setting(stack, SWEETNESS_LOG_ENCRYPTION_KEYS_SETTING)

    return LogBucketConfig(
        bucket_name=log_bucket,
        region=log_bucket.replace("aptible-docker-logs-", ""),
        decryption_keys=log_encryption_keys,
    )


async def download_s3_logs(
    stack: str,
    container: "AptibleContainer",
    start_dt: AwareDatetime,
    end_dt: AwareDatetime,
    download_dir: Path,
    bucket_config: LogBucketConfig,
) -> int:
    print(
        f"Downloading s3 logs for {container.raw_data['docker_name']} ({container.raw_data['layer']})"
    )

    # S3 logs can only be filtered by day, not time - so add 1 day to end_dt
    # to make sure we get all logs for the last day
    start_date = start_dt.date()
    end_date = (end_dt + timedelta(days=1)).date()

    try:
        aptible_cli = Command("aptible")
        output = await aptible_cli.logs_from_archive(
            stack=stack,
            container_id=container.raw_data["docker_name"],
            start_date=start_date.strftime(S3_LOGS_DATE_FORMAT),
            end_date=end_date.strftime(S3_LOGS_DATE_FORMAT),
            region=bucket_config.region,
            bucket=bucket_config.bucket_name,
            decryption_keys=bucket_config.decryption_keys,
            download_location=str(download_dir),
            _async=True,
            _err_to_out=True,
        )

        files_downloaded = 0
        output_lines = output.splitlines()
        for line in output_lines:
            if download_dir.as_posix() in line:
                files_downloaded += 1

        return files_downloaded
    except ErrorReturnCode as e:
        if NO_FILES_FOUND_ERROR not in str(e):
            print(f"Error running command: {e}")
        return 0


async def get_pancake_setting(stack: str, setting: str) -> str:
    pancake = Command(os.getenv("PANCAKE_PATH"))

    try:
        result = await pancake(  # pyright: ignore [reportGeneralTypeIssues]
            "stack:settings:view_single",
            stack,
            setting,
            _async=True,
        )
        return result.strip()
    except ErrorReturnCode as e:
        print(f"Error running command: {e}")

    return ""
