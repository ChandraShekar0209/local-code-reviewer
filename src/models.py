# src/models.py
# Model configurations for local code reviewer

MODELS = {
    "llama3.2:3b": {
        "name": "LLaMA 3.2 (3B)",
        "description": "Fast, lightweight general purpose model by Meta",
        "size": "2.0 GB",
        "strengths": "Speed, general reasoning",
        "color": "#1D9E75"
    },
    "codellama:7b": {
        "name": "CodeLlama (7B)",
        "description": "Specialised code model by Meta — trained on billions of lines of code",
        "size": "3.8 GB",
        "strengths": "Code understanding, bug detection, security",
        "color": "#378ADD"
    },
    "mistral:7b": {
        "name": "Mistral (7B)",
        "description": "Strong instruction following model by Mistral AI",
        "size": "4.4 GB",
        "strengths": "Structured output, detailed explanations",
        "color": "#7F77DD"
    }
}

# review categories
REVIEW_CATEGORIES = [
    "bugs",
    "security",
    "performance",
    "style"
]

# default models to run
DEFAULT_MODELS = list(MODELS.keys())