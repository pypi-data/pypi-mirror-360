from .embedder import OpenAIEmbedder
from .vectorstore import FAISSVectorStore


class MemoryAgent:
    def __init__(self, user_id: str, vectorstore, embedder: OpenAIEmbedder = None):
        self.user_id = user_id
        self.vectorstore = vectorstore
        self.embedder = embedder or OpenAIEmbedder()

    def chat(self, user_input: str) -> str:
        # First, add the user's message to the vector store
        self.vectorstore.add(user_input, self.embedder)
        
        # Then search for relevant memories
        memories = self.vectorstore.search(user_input)
        
        # Filter out the current query from results
        memories = [m for m in memories if m != user_input]
        
        # Format response
        if memories:
            context = "\n".join(memories)
            return f"{context}"
        else:
            return f"I don't recall anything related to that."
