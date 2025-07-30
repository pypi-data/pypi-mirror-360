from llamate.vectorstore import FAISSVectorStore
from llamate.vectorstore_postgres import PostgresVectorStore
from llamate.embedder import OpenAIEmbedder
from llamate.config import get_vector_backend, get_database_url
import os

def get_vectorstore_from_env(user_id: str):
    backend = get_vector_backend()
    
    # Create embedder with configured model
    model = os.environ.get("LLAMATE_EMBEDDING_MODEL", "text-embedding-3-small")
    embedder = OpenAIEmbedder(model=model)

    if backend == "postgres":
        db_url = get_database_url()
        if not db_url:
            raise ValueError("LLAMATE_DATABASE_URL is not set in environment")
        return PostgresVectorStore(db_url=db_url, table=f"memory_{user_id}", embedder=embedder)

    return FAISSVectorStore(user_id=user_id, embedder=embedder)
