import requests
from app.settings import settings

def hf_generate(prompt: str, max_new_tokens: int, temperature: float, top_p: float) -> dict:
    if not settings.HF_TOKEN:
        raise RuntimeError("HF_TOKEN missing")

    url = f"https://api-inference.huggingface.co/models/{settings.HF_MODEL_ID}"
    headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "return_full_text": False
        }
    }

    r = requests.post(url, headers=headers, json=payload, timeout=settings.HF_TIMEOUT)

    if r.status_code in (401, 403):
        raise RuntimeError(f"HF auth error {r.status_code}")
    if r.status_code == 429:
        raise RuntimeError("HF rate limited (429)")
    if r.status_code >= 500:
        raise RuntimeError(f"HF server error {r.status_code}")

    data = r.json()

    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"HF error: {data.get('error')}")

    text = ""
    if isinstance(data, list) and data and isinstance(data[0], dict):
        text = data[0].get("generated_text", "")
    elif isinstance(data, dict):
        text = data.get("generated_text", "")

    return {
        "mode_used": "hf",
        "model_id": settings.HF_MODEL_ID,
        "output_text": text,
        "meta": {"raw_preview": data if isinstance(data, dict) else data[:1]}
    }
