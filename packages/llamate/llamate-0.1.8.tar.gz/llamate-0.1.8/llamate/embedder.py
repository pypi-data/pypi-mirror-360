from openai import OpenAI
import numpy as np
import os

class OpenAIEmbedder:
    # Supported embedding models
    SUPPORTED_MODELS = ["text-embedding-3-small", "text-embedding-3-large"]
    
    def __init__(self, model=None):
        self.client = OpenAI()
        
        # Use provided model, env var, or default to text-embedding-3-large
        if model is not None:
            self.model = model
        else:
            env_model = os.environ.get("LLAMATE_EMBEDDING_MODEL", "text-embedding-3-small")
            # Validate the model
            if env_model not in self.SUPPORTED_MODELS:
                print(f"Warning: Unsupported model '{env_model}'. Falling back to text-embedding-3-small.")
                env_model = "text-embedding-3-small"
            self.model = env_model

    def embed(self, text: str):
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return np.array(response.data[0].embedding).astype("float32")
