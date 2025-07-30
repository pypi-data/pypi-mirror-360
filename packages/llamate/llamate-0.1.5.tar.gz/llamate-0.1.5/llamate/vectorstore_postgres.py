import numpy as np
from llamate.store import MemoryStore
from typing import List
import psycopg2
import psycopg2.extras

class PostgresVectorStore(MemoryStore):
    def __init__(self, db_url: str, table: str = "memory"):
        self.conn = psycopg2.connect(db_url)
        self.table = table
        self._ensure_table()

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            # Create pgvector extension if it doesn't exist
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self.conn.commit()
            except Exception as e:
                # Check if pgvector extension exists despite the error
                try:
                    cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                    extension_exists = cur.fetchone() is not None
                    if extension_exists:
                        # Extension exists, we can continue
                        print("✅ pgvector extension is already installed.")
                    else:
                        print(f"❌ Error: Could not create or find the 'vector' extension: {e}")
                        print("\nTo fix this issue, please try one of the following:")
                        print("1. Make sure you're using a PostgreSQL database with pgvector installed")
                        print("2. Connect with a superuser account to create the extension")
                        print("3. Run this SQL command as a superuser: CREATE EXTENSION vector;")
                        print("\nNote: The ankane/pgvector Docker image has this extension pre-installed.")
                except Exception:
                    # Couldn't even check for the extension
                    print(f"❌ Error: Could not create 'vector' extension: {e}")

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    text TEXT NOT NULL,
                    embedding VECTOR(1536)
                );
            """)
            self.conn.commit()

    def add(self, text: str, vector_or_embedder):
        with self.conn.cursor() as cur:
            # Handle the case where an embedder is passed instead of a vector
            from llamate.embedder import OpenAIEmbedder
            if isinstance(vector_or_embedder, OpenAIEmbedder):
                vector = vector_or_embedder.embed(text)
            else:
                vector = vector_or_embedder
                
            # Format vector as string for pgvector, e.g., '[0.1, 0.2, ...]'
            vector_str = f"[{','.join(map(str, vector.tolist()))}]"
            cur.execute(f"""
                INSERT INTO {self.table} (text, embedding)
                VALUES (%s, %s::vector)
            """, (text, vector_str))
            self.conn.commit()

    def search(self, query: str, top_k: int = 3) -> List[str]:
        from llamate.embedder import OpenAIEmbedder
        embedder = OpenAIEmbedder()
        query_vector = embedder.embed(query)
        
        # Format vector as string for pgvector, e.g., '[0.1, 0.2, ...]'
        vector_str = f"[{','.join(map(str, query_vector.tolist()))}]"
        
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(f"""
                SELECT text FROM {self.table}
                ORDER BY embedding <-> %s::vector
                LIMIT %s
            """, (vector_str, top_k))
            return [row["text"] for row in cur.fetchall()]

