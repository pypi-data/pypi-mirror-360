import asyncio

from pydantic import BaseModel, Field

from daydream.plugins.base import Plugin
from daydream.plugins.mixins import McpServerMixin, tool


class ShellCommand(BaseModel):
    description: str
    command: str
    args: dict[str, str] = Field(default_factory=dict)


class ShellPluginSettings(BaseModel):
    commands: list[ShellCommand] = Field(default_factory=list)


class ShellPlugin(Plugin, McpServerMixin):
    shell_settings: ShellPluginSettings = Field(default_factory=ShellPluginSettings)

    def init_plugin(self) -> None:
        self.shell_settings = ShellPluginSettings(**self._settings)

    @tool()
    async def list_available_shell_commands(self) -> list[ShellCommand]:
        """List the available shell commands."""
        return self.shell_settings.commands

    @tool()
    async def run_shell_command(self, command_name: str, args: dict[str, str] | None = None) -> str:
        """Run a shell command as defined in the config.yaml file."""
        command = next((c for c in self.shell_settings.commands if c.command == command_name), None)
        if command is None:
            return f"Command {command_name} not configured in config.yaml"

        command_str = command.command
        if args:
            command_str = command_str.format(**args)

        process = await asyncio.create_subprocess_shell(
            command_str, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        stdout, _ = await process.communicate()
        result = stdout.decode("utf-8") if stdout else ""

        if process.returncode != 0:
            return f"Command returned non-zero code {process.returncode}: {result}"

        return result
