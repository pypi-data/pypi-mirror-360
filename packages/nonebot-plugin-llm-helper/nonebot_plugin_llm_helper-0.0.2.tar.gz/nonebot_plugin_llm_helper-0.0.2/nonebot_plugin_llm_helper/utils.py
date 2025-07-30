from typing import AsyncGenerator, Optional

from .plugin import Plugin


async def generator_to_string(generator: AsyncGenerator[str, None]) -> str:
    result = []
    async for line in generator:
        result.append(line)
    return '\n'.join(result)


def get_plugin_by_name(plugins: set[Plugin], plugin_name: str) -> Optional[Plugin]:
    return next((plugin for plugin in plugins if plugin.name == plugin_name), None)
