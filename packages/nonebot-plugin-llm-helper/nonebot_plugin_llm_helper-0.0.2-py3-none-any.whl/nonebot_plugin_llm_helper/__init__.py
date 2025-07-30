import asyncio
from nonebot import get_driver, require
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
require('nonebot_plugin_alconna')
from nonebot.rule import T
from nonebot_plugin_alconna import Command, Arparma

from .config import Config
from .generate import generate_plugins_help, generate_plugin_help
from .plugin import Plugin, search_plugins
from .data import load_helper
from .utils import get_plugin_by_name, generator_to_string

__plugin_meta__ = PluginMetadata(
    name='LLM-Helper',
    description='一个支持多平台的帮助插件，基于 LLM 解析 Github 仓库或代码。',
    usage='可以通过命令 /help 或 /llm-help 进行查询。',
    homepage='https://github.com/Lonely-Sails/nonebot-plugin-llm-helper',
    type='application',
    config=Config,
)

plugins: set[Plugin] = set()
adapter = get_driver()

alconna_command = Command('llm-help [plugin:str]')
alconna_command.alias('help')
alconna_command.subcommand('list')
alconna_command.subcommand('regenerate regen')
alconna_command.subcommand('search [keyword:str]')
matcher = alconna_command.build(use_cmd_start=True)

async def list_plugins():
    yield '所有插件列表：'
    for plugin in plugins:
        print(plugin)
        if plugin.meta:
            yield f'\n  {("☑️", "✅")[bool(plugin.helper)]} {plugin.name}：'
            yield f'    - {plugin.meta.description}'
            continue
        yield f'\n  ☑️ {plugin.name}：未找到元数据。'


async def list_plugin_commands(plugin: Plugin):
    if (not plugin.name) or (plugin is None):
        yield f'插件 {plugin.name} 不存在，请检查你的输入是否正确。'
        return
    yield f'插件 {plugin.name} 的命令如下：'
    for command in plugin.helper:
        yield f'\n  {command.name}：{command.description}'
        if command.alias:
            yield f'    - 别名：{" ".join(command.alias)}'
        yield f'    - 用法：{command.name} {" ".join([f"[{param_name}]" if param_info.optional else f"<{param_name}>" for param_name, param_info in command.params.items()])}'
        for param_name, param_info in command.params.items():
            yield f'      {"*" if param_info.optional else "+"} {param_name}：{param_info.description}'
            yield f'        参数值描述：{param_info.value}'

    
async def regenerate_plugin(plugin: Plugin):
    if await generate_plugin_help(plugin):
        yield f'插件 {plugin.name} 的帮助已重新生成。'
        return
    yield f'插件 {plugin.name} 的帮助重新生成失败，请稍后再试。'


async def search_commands(keyword: str):
    count = 0
    yield f'搜索关键词 {keyword} 的结果：\n'
    keyword = keyword.lower()
    for plugin in plugins:
        if not plugin.name:
            continue
        if keyword in plugin.name.lower():
            yield f'  插件 {plugin.name} -> {plugin.meta.description if plugin.meta else "暂无简介"}'
            count += 1
        for command in plugin.helper:
            search_string = command.name + command.description + ' '.join(command.alias)
            if keyword in search_string.lower():
                yield f'  命令 {plugin.name}：{command.name} -> {command.description}'
                count += 1
    if count == 0:
        yield f'  暂未找到与之相关的命令或插件。'
        return
    yield f'\n共找到 {count} 个结果。'


@adapter.on_startup
async def _():
    global plugins
    plugins = search_plugins()
    all_count = len(plugins)
    none_meta_count = sum(plugin.meta is None for plugin in plugins)
    logger.info(f'搜索插件完毕：共 {all_count} 个有效的用户插件，{none_meta_count} 个插件未找到元数据与路径已忽略。')
    load_helper(plugins)
    asyncio.create_task(generate_plugins_help(plugins))


@matcher.handle()
async def _(result: Arparma):
    if 'list' in result.subcommands:
        await matcher.finish(await generator_to_string(list_plugins()))
    elif search_result := result.subcommands.get('search', None):
        keyword = search_result.args.get('keyword', None)
        if keyword is None:
            await matcher.finish(f'请输入搜索的关键词。')
        await matcher.finish(await generator_to_string(search_commands(keyword)))
    plugin_name = result.query[str]('main_args.plugin')
    if plugin_name is None:
        await matcher.finish(f'请输入插件名称。')
    plugin = get_plugin_by_name(plugins, plugin_name)
    if not plugin:
        await matcher.finish(f'插件 {plugin_name} 不存在，请检查你的输入是否正确。')
    if 'regenerate' in result.subcommands:
        await matcher.send(f'正在重新生成插件 {plugin.name} 的帮助，请耐心等待……')
        await matcher.finish(await generator_to_string(regenerate_plugin(plugin)))
    await matcher.finish(await generator_to_string(list_plugin_commands(plugin)))