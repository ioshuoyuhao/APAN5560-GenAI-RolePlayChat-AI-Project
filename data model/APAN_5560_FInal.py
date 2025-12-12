#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os

os.makedirs("app", exist_ok=True)
open("app/__init__.py", "w").close()

print("app/ directory ready.")


# In[2]:


gpt2_code = '''
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class GPT2RoleplayModel:
    """
    Wrapper around a fine-tuned GPT-2 model for short, single-turn Q&A.
    Loads from Hugging Face (e.g. "Jingzong/APAN5560") or a local folder.
    """

    def __init__(self, model_dir: str = "Jingzong/APAN5560", max_new_tokens: int = 40):
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(model_dir)

        # Device selection: MPS (Apple), then CUDA, then CPU
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        self.model.to(self.device)
        self.model.eval()
        self.max_new_tokens = max_new_tokens

        # Ensure pad token exists
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

    # ---------- cleaning helpers ----------

    @staticmethod
    def _strip_special_tokens(text: str) -> str:
        bad_tokens = [
            "<s>", "</s>",
            "<|user|>", "<|assistant|>",
            "<user>", "</user>",
            "<assistant>", "</assistant>",
            "<sub>", "</sub>",
        ]
        for t in bad_tokens:
            text = text.replace(t, "")
        return text

    @staticmethod
    def _shorten(text: str, max_chars: int = 220) -> str:
        """
        Keep at most 1–2 sentences and hard-limit character length.
        """
        # Remove line breaks and extra spaces
        text = text.replace("\\r", " ").replace("\\n", " ")
        text = re.sub(r"\\s+", " ", text).strip()

        sentences = re.split(r"(?<=[.!?])\\s+", text)
        if not sentences:
            return text[:max_chars]

        short = " ".join(sentences[:2])

        if len(short) > max_chars:
            short = short[:max_chars].rsplit(" ", 1)[0] + "..."

        return short

    def _clean_answer(self, raw_answer: str) -> str:
        text = self._strip_special_tokens(raw_answer)
        # Remove surrounding quotes if present
        text = text.strip().strip('"').strip("'")
        text = self._shorten(text)
        return text

    # ---------- public API ----------

    def answer(self, question: str) -> str:
        """
        Single-turn answer: takes a question string and returns a short reply.
        """
        prompt = f"User: {question}\\nAssistant:"

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=False,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.1,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        decoded = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=False,
        )

        # Keep only the part after the prompt
        raw_answer = decoded[len(prompt):]
        clean_answer = self._clean_answer(raw_answer)
        return clean_answer
'''

with open("app/gpt2_roleplay_model.py", "w", encoding="utf-8") as f:
    f.write(gpt2_code)

print("app/gpt2_roleplay_model.py written.")


# In[3]:


schemas_code = '''
from pydantic import BaseModel


class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    answer: str
'''

with open("app/schemas.py", "w", encoding="utf-8") as f:
    f.write(schemas_code)

print("app/schemas.py written.")


# In[4]:


api_code = '''
from fastapi import APIRouter
from .schemas import QARequest, QAResponse
from .gpt2_roleplay_model import GPT2RoleplayModel

router = APIRouter()

# Load the fine-tuned model once at startup
# You can change model_dir to a local folder if needed.
qa_model = GPT2RoleplayModel(model_dir="Jingzong/APAN5560")


@router.post("/answer", response_model=QAResponse)
def answer(request: QARequest) -> QAResponse:
    """
    Single-turn Q&A endpoint.
    """
    reply = qa_model.answer(request.question)
    return QAResponse(answer=reply)
'''

with open("app/api.py", "w", encoding="utf-8") as f:
    f.write(api_code)

print("app/api.py written.")


# In[5]:


main_code = '''
from fastapi import FastAPI
from .api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="RPGChat.AI API",
        description="Persona-based roleplay chatbot API using fine-tuned GPT-2",
        version="1.0.0",
    )
    # attach routes
    app.include_router(api_router)
    return app


app = create_app()
'''

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

print("app/main.py written.")


# In[ ]:




