import requests

URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b-instruct-q4_K_M"


def query_ollama(prompt):
    res = requests.post(
        URL,
        json={
            "model": MODEL,
            "prompt": f"You are a helpful assistant. Keep answers short.\nUser: {prompt}\nAssistant:",
            "options": {"num_predict": 5120},
            "stream": False,
        },
        timeout=120,
    )
    res.raise_for_status()
    data = res.json()
    return data.get("response", "").strip()
