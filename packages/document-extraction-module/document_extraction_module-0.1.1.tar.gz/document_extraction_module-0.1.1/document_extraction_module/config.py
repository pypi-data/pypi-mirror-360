import os

# Load defaults from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
VISION_AGENT_API_KEY = os.getenv("VISION_AGENT_API_KEY",None)
OPEN_AI_EXTRACTION_MODEL = os.getenv("OPEN_AI_EXTRACTION_MODEL", "gpt-4.1")
OPEN_AI_PARSE_FORMATING_MODEL = os.getenv("OPEN_AI_PARSE_FORMATING_MODEL", "gpt-4o-mini")

MAX_RETRY = int(os.getenv("MAX_RETRY", 5))
ASYNC_OPENAI_RATE_LIMIT = int(os.getenv("ASYNC_OPENAI_RATE_LIMIT", 25))
ASYNC_OPEN_AI_TIME_PERIOD = int(os.getenv("ASYNC_OPEN_AI_TIME_PERIOD", 60))
ASYNC_CONCURRENCY_LIMIT = int(os.getenv("ASYNC_CONCURRENCY_LIMIT", 10))


# Allow runtime overrides
def set_openai_api_key(val: str):
    global OPENAI_API_KEY
    OPENAI_API_KEY = val

def set_llm_provider(val: str):
    global LLM_PROVIDER
    LLM_PROVIDER = val

def set_vision_agent_api_key(val: str):
    global VISION_AGENT_API_KEY
    VISION_AGENT_API_KEY = val

def set_openai_extraction_model(val: str):
    global OPEN_AI_EXTRACTION_MODEL
    OPEN_AI_EXTRACTION_MODEL = val

def set_openai_parse_formatting_model(val: str):
    global OPEN_AI_PARSE_FORMATING_MODEL
    OPEN_AI_PARSE_FORMATING_MODEL = val

def set_async_openai_rate_limit(val: int):
    global ASYNC_OPENAI_RATE_LIMIT
    ASYNC_OPENAI_RATE_LIMIT = val

def set_async_openai_time_period(val: int):
    global ASYNC_OPEN_AI_TIME_PERIOD
    ASYNC_OPEN_AI_TIME_PERIOD = val

def set_async_concurrency_limit(val: int):
    global ASYNC_CONCURRENCY_LIMIT
    ASYNC_CONCURRENCY_LIMIT = val

