import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HF_TOKEN: str = os.getenv("HF_TOKEN", "").strip()
    HF_MODEL_ID: str = os.getenv("HF_MODEL_ID", "Jingzong/APAN5560").strip()
    HF_TIMEOUT: int = int(os.getenv("HF_TIMEOUT", "60"))

    LOCAL_MODEL_ID: str = os.getenv("LOCAL_MODEL_ID", "Jingzong/APAN5560").strip()
    DEVICE: str = os.getenv("DEVICE", "cpu").strip()
    MAX_NEW_TOKENS_DEFAULT: int = int(os.getenv("MAX_NEW_TOKENS_DEFAULT", "160"))

settings = Settings()
