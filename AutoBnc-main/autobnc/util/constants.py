import os


OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY",None)
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY",None)
