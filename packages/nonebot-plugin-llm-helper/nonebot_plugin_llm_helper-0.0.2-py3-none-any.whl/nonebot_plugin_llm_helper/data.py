import json
from dataclasses import asdict

from nonebot import require
require('nonebot_plugin_localstore')
from nonebot_plugin_localstore import get_data_file

from .plugin import Plugin, Command

data_file_path = get_data_file('LLM-Helper', 'helper.json')

def default_serializer(dump_object):
    if hasattr(dump_object, 'as_posix'):
        return dump_object.as_posix()
    return str(dump_object)


def save_helper(plugins: set[Plugin]) -> None:
    data = {
        plugin.name: [asdict(command) for command in plugin.helper]
        for plugin in plugins if plugin.helper
    }
    data_file_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=default_serializer),
        encoding='utf-8'
    )


def load_helper(plguins: set[Plugin]) -> None:
    if not data_file_path.exists():
        return None
    data = json.loads(data_file_path.read_text(encoding='Utf-8'))
    for plugin in plguins:
        if plugin.name in data:
            plugin.helper = [Command(**command) for command in data[plugin.name]]
