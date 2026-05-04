MODELS = {
    "meta/llama-3.1-8b-instruct": {
        "provider":    "nvidia",
        "input_cost":  0.000,
        "output_cost": 0.000,
        "context":     128000
    },
    "nvidia/llama-3.1-nemotron-70b-instruct": {
        "provider":    "nvidia",
        "input_cost":  0.000,
        "output_cost": 0.000,
        "context":     32768
    },
    "gemini-2.5-flash-lite": {
        "provider":    "google",
        "input_cost":  0.000,
        "output_cost": 0.000,
        "context":     1000000
    },
    "gemini-2.0-flash-exp": {
        "provider":    "google",
        "input_cost":  0.000,
        "output_cost": 0.000,
        "context":     1000000
    },
    "gemini-1.5-flash": {
        "provider":    "google",
        "input_cost":  0.000000075,
        "output_cost": 0.0000003,
        "context":     1000000
    },
    "gemini-1.5-pro": {
        "provider":    "google",
        "input_cost":  0.00000125,
        "output_cost": 0.000005,
        "context":     2000000
    },
}
DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"