import asyncio
from typing import Optional
from httpx import AsyncClient, Response
from nonebot.log import logger

from .config import config

client = AsyncClient(timeout=config.llm_helper_timeout)
llm_headers = {'Authorization': f'Bearer {config.llm_helper_api_key}', 'Content-Type': 'application/json'}


async def fetch_github(url: str, count: int = 0) -> Optional[Response]:
    try:
        response = await client.get(config.github_proxy + url, timeout=30)
        response.raise_for_status()
        return response
    except Exception as error:
        logger.warning(f'第 {count + 1} 次请求 {url} 失败：{error}')
        await asyncio.sleep(config.llm_helper_retry_delay)
        if count < config.llm_helper_max_retries:
            return await fetch_github(url, count + 1)
        return None


async def request_openai(messages: list[dict]) -> Optional[str]:
    json = {
        'model': config.llm_helper_model,
        'messages': messages,
    }
    try:
        logger.debug(f'OpenAI 请求：{json}')
        response = await client.post(
            f'{config.llm_helper_base_url}/chat/completions',
            headers=llm_headers, json=json,
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    except Exception as error:
        logger.warning(f'OpenAI 请求失败：{error}')
        return None