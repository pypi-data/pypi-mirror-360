from abc import ABC, abstractmethod
from typing import List
import numpy as np

class MemoryStore(ABC):
    @abstractmethod
    def add(self, text: str, vector: np.ndarray):
        pass

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int) -> List[str]:
        pass
