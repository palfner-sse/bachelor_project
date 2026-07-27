import os

# Provider configuration
# Anthropic (default): set ANTHROPIC_API_KEY and leave ANTHROPIC_BASE_URL unset.
# Ollama via LiteLLM:  start `litellm --model ollama/<model> --port 4000`,
#                      then set ANTHROPIC_BASE_URL and use "ollama" as the key.

os.environ.setdefault("ANTHROPIC_API_KEY", "ollama")
os.environ.setdefault("ANTHROPIC_BASE_URL", "http://147.172.177.104:11434")

# Selected model for the Agents
AGENT_MODEL = "qwen3.5:122b"

# Selected model for the routing
ROUTING_MODEL = "qwen3.5:122b"

# Folder the System expects the codebase to be in
AGENT_CWD = ""
