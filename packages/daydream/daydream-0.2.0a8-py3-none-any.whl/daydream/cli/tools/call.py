import json
from typing import Annotated

import anyio
import typer
from fastmcp import Client
from mcp.types import TextContent

from daydream.cli.options import PROFILE_OPTION
from daydream.cli.tools._app import tools_app
from daydream.config import load_config
from daydream.config.utils import get_config_dir
from daydream.knowledge import Graph
from daydream.mcp import Context, build_mcp_server
from daydream.plugins import PluginManager


@tools_app.command()
def call(
    tool: str,
    arguments: Annotated[list[str] | None, typer.Argument()] = None,
    profile: str = PROFILE_OPTION,
) -> None:
    """Call an MCP tool from the command line."""

    async def _call_tool() -> None:
        config = load_config(profile)
        plugins = PluginManager(config=config)
        context = Context(
            profile=profile,
            config=config,
            plugins=plugins,
            graph=Graph(get_config_dir(profile) / "graph.json"),
        )
        mcp = await build_mcp_server(context)

        tools = await mcp.get_tools()
        if tool not in tools:
            raise typer.Abort(f"Tool {tool} not found")

        tool_def = tools[tool]
        tool_args = {}
        if arguments:
            # Convert a list of arguments into a dict
            for k, v in zip(tool_def.parameters["properties"].keys(), arguments, strict=True):
                # Try decoding as JSON to handle complex arguments (lists, dicts, etc.)
                try:
                    tool_args[k] = json.loads(v)
                except json.JSONDecodeError:
                    tool_args[k] = v

        client = Client(mcp)
        async with client:
            result = await client.call_tool(tool, tool_args)
            try:
                print(next(r.text for r in result.content if isinstance(r, TextContent)))
            except StopIteration:
                print(f"{tool} returned no printable results")

    anyio.run(_call_tool)
