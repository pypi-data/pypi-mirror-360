import rich

from daydream.cli.client.logs.app import client_logs_app


@client_logs_app.command()
def claude() -> None:
    """Show logs for Claude Desktop Daydream MCP Server"""
    rich.print("Logs are available at:")
    rich.print("~/Library/Logs/Claude/mcp.log")
    rich.print("~/Library/Logs/Claude/mcp-server-daydream.log")
