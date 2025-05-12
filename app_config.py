# config.py: load env, config logger, parse configs

from dotenv import load_dotenv
from pydantic import BaseModel
import os
import json

load_dotenv()

class AppConfig(BaseModel):
    """Application settings"""
    
    base_url:str = os.getenv('RAG_URL')

app_config = AppConfig()
    