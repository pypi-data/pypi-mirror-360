import os
from llamate.vectorstore_postgres import PostgresVectorStore
from llamate.embedder import OpenAIEmbedder

def run_init():
    print("🧠 LLAMate Init")

    backend = input("Choose vector backend (postgres/faiss) [postgres]: ").strip().lower() or "postgres"
    api_key = input("Enter your OpenAI API key: ").strip()
    
    # Prompt for embedding model choice
    print(f"\nSupported embedding models: {', '.join(OpenAIEmbedder.SUPPORTED_MODELS)}")
    embedding_model = input(f"Choose embedding model [text-embedding-3-small]: ").strip() or "text-embedding-3-small"
    
    # Validate embedding model choice
    if embedding_model not in OpenAIEmbedder.SUPPORTED_MODELS:
        print(f"⚠️ Warning: '{embedding_model}' is not in the list of supported models.")
        embedding_model = "text-embedding-3-large"
        print(f"Using default model: {embedding_model}")

    env_lines = [
        f"LLAMATE_OPENAI_API_KEY={api_key}",
        f"LLAMATE_VECTOR_BACKEND={backend}",
        f"LLAMATE_EMBEDDING_MODEL={embedding_model}"
    ]

    if backend == "postgres":
        db_url = input("Enter your Postgres URL (e.g. postgresql://user:pass@host:5432/db): ").strip()
        env_lines.append(f"LLAMATE_DATABASE_URL={db_url}")

        # Bootstrap table
        table = input("Postgres table name [memory_default]: ").strip() or "memory_default"
        try:
            store = PostgresVectorStore(db_url=db_url, table=table)
            print(f"✅ Postgres table '{table}' initialized.")
        except Exception as e:
            print(f"❌ Failed to init Postgres table: {e}")

    with open(".env", "w") as f:
        f.write("\n".join(env_lines))
    print("✅ .env file created.")
