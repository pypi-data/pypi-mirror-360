from openai import OpenAI
import numpy as np

class OpenAIEmbedder:
    def __init__(self, model="text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model

    def embed(self, text: str):
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return np.array(response.data[0].embedding).astype("float32")
