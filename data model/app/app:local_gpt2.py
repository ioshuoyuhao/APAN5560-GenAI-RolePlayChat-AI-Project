from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from app.settings import settings

_tokenizer = None
_model = None

def _load_once():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(settings.LOCAL_MODEL_ID)
        _model = AutoModelForCausalLM.from_pretrained(settings.LOCAL_MODEL_ID)
        if settings.DEVICE == "cuda" and torch.cuda.is_available():
            _model = _model.to("cuda")
        _model.eval()

def local_generate(prompt: str, max_new_tokens: int, temperature: float, top_p: float) -> dict:
    _load_once()

    inputs = _tokenizer(prompt, return_tensors="pt")
    if settings.DEVICE == "cuda" and torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

    with torch.no_grad():
        out = _model.generate(
            **inputs,
            do_sample=True,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            pad_token_id=_tokenizer.eos_token_id
        )

    text = _tokenizer.decode(out[0], skip_special_tokens=True)

    if text.startswith(prompt):
        text = text[len(prompt):].lstrip()

    return {
        "mode_used": "local",
        "model_id": settings.LOCAL_MODEL_ID,
        "output_text": text,
        "meta": {"device": settings.DEVICE}
    }
