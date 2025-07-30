import re
import json
import asyncio
from pathlib import Path
from nonebot.log import logger

from .plugin import Plugin, Command
from .network import request_openai, fetch_github
from .data import save_helper
from .config import config
from .prompt import PROMPT


def list_dir(base_path: Path) -> str:
    # 列出所有目录，使用平铺的格式，并且不需要按层级，每个文件都是插件目录的相对路径
    children = []
    for path in base_path.rglob('*'):
        text_path = str(path.relative_to(base_path))
        if not '__pycache__' in text_path:
            children.append(text_path)
    return '\n'.join(children)


def read_file(base_path: Path, path: str) -> str:
    if '..' in path:
        return '你想要读取的文件路径不合法，请重新输入。'
    file_path = base_path / Path(path)
    return file_path.read_text(encoding='Utf-8')


async def generate_plugin_help(plugin: Plugin) -> bool:
    retry_count = 0
    readme = None
    if plugin.meta.homepage:
        # 先得到插件的README.md
        repo_name = plugin.meta.homepage.split('github.com/')[1]
        response = await fetch_github(f'https://raw.githubusercontent.com/{repo_name}/master/README.md')
        if response is not None:
            readme = response.text
            logger.debug(f'成功获取 {plugin.name} 的 README，文件内容：{readme}')
    readme_input = '以下为此项目的 README 文件内容：\n\n' + readme if readme else '暂时无法获取到 README 文件，请你通过把阅读代码来生成插件使用方法和说明文档。'
    messages = [
        {'role': 'system', 'content': PROMPT},
        {'role': 'user', 'content': readme_input}
    ]
    while True:
        if retry_count > config.llm_helper_max_retries:
            logger.error(f'{plugin.name} 的 LLM 响应失败！重试次数过多，跳过！')
            return False
        response = await request_openai(messages)
        if response is None:
            retry_count += 1
            logger.warning(f'{plugin.name} 的 LLM 响应失败！重试……')
            continue
        messages.append({'role': 'assistant', 'content': response})
        response = response.split('</think>')[-1].strip()
        if result_match := re.match(r'<result>(.*)</result>', response, re.DOTALL):
            string_result = result_match.group(1)
            logger.debug(f'{plugin.name} 的 LLM 生成帮助结果：{string_result}')
            try:
                result = json.loads(string_result.replace('\'', '"'))
                plugin.helper = [Command(**command) for command in result]
            except json.JSONDecodeError:
                retry_count += 1
                logger.error(f'{plugin.name} 的 LLM 生成帮助结果格式错误！重试……')
                messages.append({'role': 'user', 'content': '你的输出的 Json 格式错误，请重新检查并输出。请注意要将格式正确的 Json 输出在 <result> 标签内，否则我无法解析。'})
                continue
            logger.success(f'{plugin.name} 的 LLM 生成帮助成功！')
            logger.debug(f'{plugin.name} 的 LLM 生成帮助结果：{result}')
            return True
        if re.match(r'<list_dir>(.*)</list_dir>', response, re.DOTALL):
            list_dir_content = list_dir(plugin.path)
            messages.append({'role': 'user', 'content': '以下为此项目的目录结构：\n\n' + list_dir_content})
            continue
        if read_file_match := re.match(r'<read_file>(.*)</read_file>', response, re.DOTALL):
            read_file_content = read_file(plugin.path, read_file_match.group(1))
            messages.append({'role': 'user', 'content': '以下为你想要读取的代码文件内容：\n\n' + read_file_content})
            continue
        retry_count += 1
        logger.warning(f'{plugin.name} 的 LLM 响应格式错误！重试……')
        messages.append({'role': 'user', 'content': '请你输出一个工具，否则我无法与你继续对话。'})


async def generate_plugins_help(plugins: set[Plugin]) -> None:
    tasks = []
    logger.info('正在生成插件帮助……')
    for plugin in plugins:
        if plugin.helper:
            logger.debug(f'{plugin.name} 已存在帮助，直接使用缓存。')
            continue
        if plugin.meta is None or plugin.path is None:
            logger.info(f'{plugin.name} 未找到元数据与路径，跳过！')
            continue
        tasks.append(asyncio.create_task(generate_plugin_help(plugin)))
    success_count = sum(await asyncio.gather(*tasks))
    logger.success(f'插件帮助生成完毕！成功生成 {success_count} 个插件的帮助，失败 {len(tasks) - success_count} 个插件。')
    save_helper(plugins)
