# Memra SDK Configuration
# LLM API Configuration for agent processing

API_CONFIG = {
    "huggingface": {
        "api_key": "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",
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
        "max_tokens": 2000
    }
}

# Default LLM settings for agents
DEFAULT_LLM_CONFIG = {
    "provider": "huggingface",
    "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    "temperature": 0.1,
    "max_tokens": 2000
}

# Agent-specific LLM configurations
AGENT_LLM_CONFIG = {
    "parsing": {
        "provider": "huggingface", 
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
        "temperature": 0.0,  # More deterministic for data extraction
        "max_tokens": 2000
    },
    "manager": {
        "provider": "huggingface",
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct", 
        "temperature": 0.3,  # More flexible for decision making
        "max_tokens": 1500
    }
} 