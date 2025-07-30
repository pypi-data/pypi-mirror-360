import os
from llamate.vectorstore_postgres import PostgresVectorStore

def run_init():
    print("🧠 LLAMate Init")

    backend = input("Choose vector backend (faiss/postgres) [faiss]: ").strip().lower() or "faiss"
    api_key = input("Enter your OpenAI API key: ").strip()

    env_lines = [f"LLAMATE_OPENAI_API_KEY={api_key}", f"LLAMATE_VECTOR_BACKEND={backend}"]

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
