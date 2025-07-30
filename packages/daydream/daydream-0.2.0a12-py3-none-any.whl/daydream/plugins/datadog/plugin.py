import os
from typing import Any

import anyio
import questionary

from daydream.config.utils import Config, PluginSettings
from daydream.knowledge import Graph
from daydream.plugins.base import Plugin
from daydream.plugins.datadog.client import DatadogClient
from daydream.plugins.datadog.nodes.datadog_api import DatadogApi
from daydream.plugins.datadog.nodes.datadog_service import DatadogService
from daydream.plugins.datadog.nodes.datadog_system import DatadogSystem
from daydream.plugins.datadog.nodes.datadog_team import DatadogTeam
from daydream.plugins.mixins import KnowledgeGraphMixin


class DatadogPlugin(Plugin, KnowledgeGraphMixin):
    """A plugin for Datadog."""

    _client: DatadogClient

    def __init__(
        self,
        *args: Any,
        api_key: str | None = None,
        application_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._api_key = api_key
        self._application_key = application_key
        self._client = DatadogClient(
            api_key=api_key or os.getenv("DATADOG_API_KEY", ""),
            application_key=application_key or os.getenv("DATADOG_APP_KEY", ""),
        )

    async def interactive_configure(self, cfg: Config) -> PluginSettings:
        """Interactive wizard for configuring the settings of this plugin."""
        return {
            "api_key": await questionary.text("Enter your Datadog API key").unsafe_ask_async(),
            "application_key": await questionary.text(
                "Enter your Datadog application key"
            ).unsafe_ask_async(),
        }

    async def populate_graph(self, graph: Graph) -> None:
        """Populate the graph with Datadog entities."""
        async with anyio.create_task_group() as tg:
            tg.start_soon(self._populate_teams, graph)
            tg.start_soon(self._populate_software_catalog_entities, graph)

    async def _populate_teams(self, graph: Graph) -> None:
        async for team in self._client.iter_teams():
            await graph.add_node(
                DatadogTeam(
                    node_id=f"team:default/{team['attributes']['handle']}",
                    raw_data=team.to_dict(),
                    _graph=graph,
                )
            )

    async def _populate_software_catalog_entities(self, graph: Graph) -> None:
        async for entity in self._client.iter_software_catalog_entities():
            entity_kind = entity["attributes"]["kind"]

            if entity_kind == "service":
                node = DatadogService(
                    node_id=f"service:default/{entity['attributes']['name']}",
                    raw_data=entity.to_dict(),
                    _graph=graph,
                )
            elif entity_kind == "api":
                node = DatadogApi(
                    node_id=f"api:default/{entity['attributes']['name']}",
                    raw_data=entity.to_dict(),
                    _graph=graph,
                )
            else:
                raise ValueError(f"Unknown entity kind: {entity_kind}")

            await graph.add_node(node)

            # HACK: There doesn't seem to be a way to list systems directly in datadog, so we'll fake it for now.
            for (
                related_entity_reference,
                _,
            ) in await node._get_related_entity_reference_identifiers():
                if related_entity_reference.startswith("system:"):
                    await graph.add_node(
                        DatadogSystem(
                            node_id=related_entity_reference,
                            raw_data={
                                "attributes": {
                                    "name": related_entity_reference.split("/")[-1],
                                },
                            },
                            _graph=graph,
                        )
                    )
