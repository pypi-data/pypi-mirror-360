import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o")

MODEL_TOKEN_LEN = {
    # GPT-3.5 family
    "gpt-3.5-turbo": {
        "max_in": 16385,
        "max_out": 4096
    },
    "gpt-3.5-turbo-0125": {
        "max_in": 16385,
        "max_out": 4096
    },
    "gpt-3.5-turbo-1106": {
        "max_in": 16385,
        "max_out": 4096
    },

    # GPT-3.5 turbo 16k variants (historical, but technically still supported)
    "gpt-3.5-turbo-16k": {
        "max_in": 16385,
        "max_out": 16385
    },
    "gpt-3.5-turbo-16k-0613": {
        "max_in": 16385,
        "max_out": 16385
    },

    # GPT-4 standard
    "gpt-4": {
        "max_in": 8192,
        "max_out": 8192
    },
    "gpt-4-0314": {
        "max_in": 8192,
        "max_out": 8192
    },
    "gpt-4-0613": {
        "max_in": 8192,
        "max_out": 8192
    },

    # GPT-4-32k (these were specialized, higher-capacity versions)
    "gpt-4-32k": {
        "max_in": 32768,
        "max_out": 32768
    },
    "gpt-4-32k-0314": {
        "max_in": 32768,
        "max_out": 32768
    },
    "gpt-4-32k-0613": {
        "max_in": 32768,
        "max_out": 32768
    },

    # GPT-4 turbo / preview variants
    "gpt-4-1106-preview": {
        "max_in": 128000,
        "max_out": 4096
    },
    "gpt-4-1106-vision-preview": {
        "max_in": 128000,
        "max_out": 4096
    },
    "gpt-4-0125-preview": {
        "max_in": 128000,
        "max_out": 4096
    },
    "gpt-4-turbo-preview": {
        "max_in": 128000,
        "max_out": 4096
    },
    "gpt-4-vision-preview": {
        "max_in": 128000,
        "max_out": 4096
    },

    # GPT-4o (latest GPT-4 series, multimodal)
    "gpt-4o": {
        "max_in": 128000,
        "max_out": 4096
    },
    "gpt-4o-mini": {
        "max_in": 128000,
        "max_out": 4096
    }
}
