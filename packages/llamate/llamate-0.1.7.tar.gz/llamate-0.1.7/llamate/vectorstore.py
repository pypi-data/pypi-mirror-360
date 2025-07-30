import faiss
import numpy as np
import os
import uuid
import json
from llamate.store import MemoryStore
from llamate.embedder import OpenAIEmbedder
from typing import List

class FAISSVectorStore(MemoryStore):
    def __init__(self, user_id: str, embedder: OpenAIEmbedder):
        self.user_id = user_id
        self.embedder = embedder
        self.embedding_dim = int(os.environ.get("LLAMATE_EMBEDDING_DIM", 3072))
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.texts = []
        self.memory_store = []
        self.memory_path = f"{user_id}_memory.json"
        self._load()

    def add(self, text: str, vector_or_embedder):
        # Handle both vector and embedder cases for consistency with PostgreSQL store
        from llamate.embedder import OpenAIEmbedder
        if isinstance(vector_or_embedder, OpenAIEmbedder):
            vector = vector_or_embedder.embed(text)
        else:
            vector = vector_or_embedder
            
        # Check for similar existing memories to avoid duplicates
        if len(self.memory_store) > 0:
            # Use the vector we just created to search for similar existing memories
            D, I = self.index.search(np.array([vector], dtype=np.float32), 1)
            
            # If we found a close match and the distance is small enough, skip adding
            if I[0][0] != -1 and D[0][0] < 0.1:  # Smaller distance = more similar
                return
            
        self._add_vector(text, vector)

    def _add_vector(self, text: str, vector: np.ndarray):
        self.index.add(np.array([vector]))
        self.memory_store.append({"id": str(uuid.uuid4()), "text": text, "vector": vector.tolist()})
        self._save()

    def search(self, query: str, top_k: int = 3) -> List[str]:
        query_vector = self.embedder.embed(query)
        D, I = self.index.search(np.array([query_vector], dtype=np.float32), top_k)
        # Return the stored text entries for the found indices (if valid)
        return [self.memory_store[i]["text"] for i in I[0] if i != -1 and i < len(self.memory_store)]

    def _save(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.memory_store, f)

    def _load(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r") as f:
                self.memory_store = json.load(f)
                vectors = [np.array(m["vector"]).astype("float32") for m in self.memory_store]
                if vectors:
                    self.index.add(np.array(vectors))
