from pydantic import BaseModel
from nonebot.plugin import get_plugin_config


class Config(BaseModel):
    github_proxy: str = 'https://gh-proxy.com/'

    llm_helper_api_key: str
    llm_helper_model: str
    llm_helper_base_url: str

    llm_helper_timeout: int = 600 # 请求 LLM 的等待时间
    llm_helper_max_retries: int = 3 # 请求 Github 仓库的最大重试次数
    llm_helper_retry_delay: int = 10 # 请求 Github 仓库的重试间隔时间


config = get_plugin_config(Config)
