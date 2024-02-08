import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

API_TOKEN = config["Telegram"]["token"]


ComradeAIToken = config["ComradeAI"]["token"]

requestAgentConfigs = {
    "GPT-3.5": {"model": "gpt-3.5-turbo-1106", "max_tokens": 4096, "temperature": 0.8},
    "Gemini Pro": {"model": "gemini-pro", "max_output_tokens": 1000, "temperature": 0.8},
    "GPT-4": {"model": "gpt-4-1106-preview", "max_tokens": 4096, "temperature": 0.8},
    "LLaMa 2": {"max_tokens": 4096, "max_response_words": 500, "temperature": 0.8},
    "YandexGPT v2": {"temperature": 0.8},
    "Claude-2.1": {}
}

model_mapping = {
    "GPT-3.5": "OpenAI_GPT_Completions",
    "Gemini Pro": "Google_GeminiProVision",
    "GPT-4": "OpenAI_GPT_Completions",
    "LLaMa 2": "Meta_LLaMa2",
    "YandexGPT v2": "YandexGPT2-FULL",
    "Claude-2.1": "Anthropic_CLAUDE2.1"
}

token_limits = {
    "GPT-3.5": 12000,
    "GPT-4": 128000,
    "Gemini Pro": 25000,
    "LLaMa 2": 25000,
    "YandexGPT v2": 100,
    "Claude-2.1": 128000,
}
