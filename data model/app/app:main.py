from fastapi import FastAPI, HTTPException
from app.schemas import GenerateRequest, GenerateResponse
from app.hf_inference import hf_generate
from app.local_gpt2 import local_generate
from app.settings import settings

app = FastAPI(title="APAN5560 GPT-2 FastAPI (HF+Local Fallback)", version="1.0.0")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "hf_model": settings.HF_MODEL_ID,
        "has_hf_token": bool(settings.HF_TOKEN),
        "local_model": settings.LOCAL_MODEL_ID
    }

@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        if req.mode == "hf":
            return GenerateResponse(**hf_generate(req.prompt, req.max_new_tokens, req.temperature, req.top_p))

        if req.mode == "local":
            return GenerateResponse(**local_generate(req.prompt, req.max_new_tokens, req.temperature, req.top_p))

        # auto: 优先 HF（如果有token），失败 fallback 本地
        if settings.HF_TOKEN:
            try:
                return GenerateResponse(**hf_generate(req.prompt, req.max_new_tokens, req.temperature, req.top_p))
            except Exception as e:
                fallback = local_generate(req.prompt, req.max_new_tokens, req.temperature, req.top_p)
                fallback["meta"]["hf_error"] = str(e)
                return GenerateResponse(**fallback)

        return GenerateResponse(**local_generate(req.prompt, req.max_new_tokens, req.temperature, req.top_p))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
