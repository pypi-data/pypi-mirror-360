import time
from collections import Counter

import anyio
import typer

from daydream.cli._app import app
from daydream.cli.options import PROFILE_OPTION
from daydream.config import load_config
from daydream.config.utils import get_config_dir
from daydream.knowledge import Graph
from daydream.plugins import PluginManager
from daydream.plugins.mixins import KnowledgeGraphMixin
from daydream.telemetry import client as telemetry


@app.command()
def build_graph(
    profile: str = PROFILE_OPTION,
    interval: int | None = typer.Option(
        None,
        "--interval",
        help="Rebuild the graph continuously, pausing for the specified interval between builds",
    ),
) -> None:
    """Build a knowledge graph for your cloud infrastructure"""

    async def _build_graph() -> None:
        print("Building graph...")

        start_time = time.perf_counter()

        graph = Graph()
        config = load_config(profile, create=True)
        output_path = (get_config_dir(profile) / "graph.json").resolve()
        plugin_manager = PluginManager(config)

        async with anyio.create_task_group() as tg:
            for plugin in plugin_manager.get_plugins_with_capability(KnowledgeGraphMixin):
                print(f"Populating graph with the {plugin.name} plugin...")
                tg.start_soon(plugin.populate_graph, graph)

        await graph.infer_edges()

        print(f"Saving graph to {output_path!s}...")
        await graph.save(output_path)

        end_time = time.perf_counter()
        total_time = end_time - start_time
        edge_counts = Counter(
            [edge.properties["relationship_type"] async for edge in graph.iter_edges()]
        )
        node_counts = Counter([node.node_type async for node in graph.iter_nodes()])

        print("=== Summary ===")

        print("Edges:")
        for relationship_type, count in edge_counts.items():
            print(f"  {relationship_type}: {count}")
        print("Nodes:")
        for node_type, count in node_counts.items():
            print(f"  {node_type}: {count}")

        print(f"Graph built in {total_time:.2f} seconds")
        print(f"Graph saved to {output_path!s}")
        print("=== End Summary ===")

        await telemetry.send_event(
            {
                "command": "build_graph",
                "profile": profile,
                "duration_seconds": total_time,
                "node_counts": node_counts,
                "edge_counts": edge_counts,
            }
        )

    if interval:
        while True:
            anyio.run(_build_graph)
            print(f"Sleeping for {interval} seconds before next build...")
            time.sleep(interval)
    else:
        anyio.run(_build_graph)
