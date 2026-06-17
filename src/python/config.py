import os

OLLAMA_ENDPOINT_URL = "http://localhost:11434"
EMBEDDING_TYPE = "nomic-embed-text"
MODEL_NAME = "gemma4:32k"

os.environ["ANTHROPIC_BASE_URL"] = OLLAMA_ENDPOINT_URL
os.environ["ANTHROPIC_AUTH_TOKEN"] = "ollama"
os.environ["ANTHROPIC_API_KEY"] = ""