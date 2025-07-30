import numpy as np
from llamate.embedder import OpenAIEmbedder


def test_embedder_vector_shape():
    embedder = OpenAIEmbedder()
    vector = embedder.embed("test input")
    assert vector.shape == (1536,)
    assert isinstance(vector[0], (float, np.floating))
