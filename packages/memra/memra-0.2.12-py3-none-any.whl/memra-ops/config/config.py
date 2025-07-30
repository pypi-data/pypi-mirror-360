"""
Configuration for Memra SDK examples
Contains LLM configurations for different agent types
"""

# Default LLM configuration for general use
DEFAULT_LLM_CONFIG = {
    "model": "llama-3.2-11b-vision-preview",
    "temperature": 0.1,
    "max_tokens": 2000
}

# Specialized LLM configurations for different agent types
AGENT_LLM_CONFIG = {
    "parsing": {
        "model": "llama-3.2-11b-vision-preview",
        "temperature": 0.0,
        "max_tokens": 4000
    },
    "manager": {
        "model": "llama-3.2-11b-vision-preview", 
        "temperature": 0.2,
        "max_tokens": 1000
    }
} 