import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL_ANTHROPIC", "claude-sonnet-4-20250514")

MODEL_TOKEN_LEN = {
    # Legacy Claude models (discontinued/deprecated)
    "claude-instant-1": {
        "max_in": 100000,
        "max_out": 8192
    },
    "claude-instant-1.2": {
        "max_in": 100000,
        "max_out": 8192
    },
    "claude-2": {
        "max_in": 100000,
        "max_out": 8192
    },
    "claude-2.0": {
        "max_in": 100000,
        "max_out": 8192
    },
    "claude-2.1": {
        "max_in": 200000,
        "max_out": 8192
    },

    # Claude 3 models
    "claude-3-haiku-20240307": {
        "max_in": 200000,
        "max_out": 4096
    },
    "claude-3-sonnet-20240229": {
        "max_in": 200000,
        "max_out": 4096
    },
    "claude-3-opus-20240229": {
        "max_in": 200000,
        "max_out": 4096
    },

    # Claude 3.5 models
    "claude-3-5-sonnet-20240620": {
        "max_in": 200000,
        "max_out": 8192
    },
    "claude-3-5-sonnet-20241022": {
        "max_in": 200000,
        "max_out": 8192
    },
    "claude-3-5-haiku-20241022": {
        "max_in": 200000,
        "max_out": 8192
    },

    # Claude 3.7 models (available with beta header)
    "claude-3-7-sonnet-20250119": {
        "max_in": 200000,
        "max_out": 8192,  # 128k with beta header "output-128k-2025-02-19"
        "max_out_beta": 128000
    },

    # Claude 4 models (current generation)
    "claude-sonnet-4-20250514": {
        "max_in": 200000,
        "max_out": 64000
    },
    "claude-opus-4-20250514": {
        "max_in": 200000,
        "max_out": 32000
    }
}