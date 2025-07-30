from pathlib import Path

from pydantic import AwareDatetime
from pydantic_core import to_json

from daydream.knowledge.nodes.mixins.logs import HasLogs
from daydream.lib.log_anomalies import LogAnomaly, detect_log_anomalies
from daydream.plugins.base import Plugin
from daydream.plugins.mixins import McpServerMixin, tool
from daydream.utils import print


class LogsPlugin(Plugin, McpServerMixin):
    @tool()
    async def get_log_file_anomalies(
        self,
        node_id: str,
        time_range_start: AwareDatetime,
        time_range_end: AwareDatetime,
    ) -> list[LogAnomaly] | str:
        """Get anomalies from the log files of a resource using its node ID.

        Limit the time range to an hour or so.

        Get metrics first. Then, find a time in the metrics where it looks
        like an incident started happening. Call this tool with a time range
        30 mins before through 30 mins after the incident start time.

        This tool will return possible log anomaly patterns, but they may not
        all be relevant (they might not be related to the incident, and they
        might not even be errors).

        When using results from log anomalies, always show the user the
        example log entries so that they can make a judgement call.
        """
        node = await self.context.graph.get_node(node_id)

        if not node:
            return f"Resource with node ID {node_id} not found"

        if not isinstance(node, HasLogs):
            return f"Resource with node ID {node_id} does not support logs"

        print(f"Getting logs for {node.nid}")

        node_logs = await node.get_logs(time_range_start, time_range_end)

        print(f"Found {len(node_logs)} logs")

        log_anomalies = detect_log_anomalies(node_logs, window_minutes=1)

        if log_anomalies:
            anomalies_file = (
                Path.home()
                / ".daydream"
                / "logs"
                / f"{node_id.replace(':', '-')}-{time_range_start.date()}-{time_range_end.date()}.json"
            )
            anomalies_file.write_bytes(to_json(log_anomalies, indent=2))

            return f"""STOP HERE, DO NOT CALL OTHER TOOLS YET.

            Log anomalies written to {anomalies_file}. Ask the user to look through that
            file and make sure there is no sensitive data. If there is nothing
            sensitive, ask the user to paste the anomalies back in to this
            conversation so you can interpret the results.
            """
        else:
            return "No log anomalies found."
