"""
配置文件 - 302.AI API配置和模型设置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 302.AI API 配置
API_BASE_URL = "https://api.302.ai/v1"
API_KEY = os.getenv("API_302_KEY", "")

# 支持的模型配置
SUPPORTED_MODELS = {
    "claude": {
        "model_name": "claude-sonnet-4-5-20250929",
        "max_tokens": 200000,
        "temperature": 0.7
    },
    "gemini": {
        "model_name": "gemini-2.5-pro",
        "max_tokens": 1000000,
        "temperature": 0.7
    },
    "gpt": {
        "model_name": "gpt-4o",
        "max_tokens": 400000,
        "temperature": 0.7
    },
    "grok": {
        "model_name": "grok-4-0709",
        "max_tokens": 256000,
        "temperature": 0.7
    },
    "deepseek": {
        "model_name": "deepseek-v3.1",
        "max_tokens": 128000,
        "temperature": 0.7
    },
    "qwen": {
        "model_name": "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "max_tokens": 258048,
        "temperature": 0.7
    },
    "glm": {
        "model_name": "glm-4-0520",
        "max_tokens": 200000,
        "temperature": 0.7
    },
    "kimi": {
        "model_name": "kimi-k2-0905-preview",
        "max_tokens": 256000,
        "temperature": 0.7
    }
}

# 游戏配置
GAME_CONFIG = {
    "max_round": 10,
    "initial_stack": 20000,
    "small_blind_amount": 10,
    "big_blind_amount": 20
}

