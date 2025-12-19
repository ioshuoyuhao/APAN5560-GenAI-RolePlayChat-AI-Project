from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    max_new_tokens: int = Field(160, ge=1, le=512)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(0.95, ge=0.0, le=1.0)
    mode: str = Field("auto", pattern="^(auto|hf|local)$")  # auto:优先hf,失败就local

class GenerateResponse(BaseModel):
    mode_used: str
    model_id: str
    output_text: str
    meta: dict
