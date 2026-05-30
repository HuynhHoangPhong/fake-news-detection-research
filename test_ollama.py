# test_ollama.py

import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5-coder:7b",
        "prompt": "Explain Fake News Detection in 3 sentences.",
        "stream": False
    }
)

print(response.json()["response"])