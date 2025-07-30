import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_api_key():
    return os.getenv("LLAMATE_OPENAI_API_KEY")

def get_vector_backend():
    return os.getenv("LLAMATE_VECTOR_BACKEND", "postgres")

def get_database_url():
    return os.getenv("LLAMATE_DATABASE_URL", "postgresql://llamate:llamate@localhost:5432/llamate")
