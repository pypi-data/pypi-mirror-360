import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from nonebot.plugin import PluginMetadata, _managers


@dataclass
class Param:
    value: str
    optional: bool
    description: str


@dataclass
class Command:
    name: str
    description: str
    example: str
    alias: list[str] = field(default_factory=list)
    params: dict[str, Param] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.params = {
            key: Param(**param) if not isinstance(param, Param) else param
            for key, param in self.params.items()
        }


@dataclass
class Plugin:
    id: str
    name: Optional[str] = None
    path: Optional[Path] = None
    meta: Optional[PluginMetadata] = None
    helper: list[Command] = field(default_factory=list)

    def __hash__(self):
        return hash(self.id)

    def __post_init__(self) -> None:
        self.helper = [
            Command(**command) if not isinstance(command, Command) else command
            for command in self.helper
        ]


def search_plugins() -> set[Plugin]:
    plugins = set()
    for manager in _managers:
        for plugin_id in manager.plugins:
            if plugin_module := sys.modules.get(plugin_id, None):
                plugin_meta: PluginMetadata | None = getattr(plugin_module, '__plugin_meta__', None)
                if (not plugin_meta) or plugin_meta.type == 'library':
                    continue
                if plugin_module.__file__:
                    path = Path(plugin_module.__file__)
                    plugin_name = plugin_meta.name.replace(' ', '-')
                    plugins.add(Plugin(id=plugin_id, name=plugin_name, meta=plugin_meta, path=path.parent))
                continue
            plugins.add(Plugin(id=plugin_id))
    return plugins
