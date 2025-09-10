from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

class Embedding:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._model = SentenceTransformer(EMBEDDING_MODEL)
    
    def embed_text(self, text: str) -> list[float]:
        """将文本转换为向量"""
        return self._model.encode(text).tolist()
    
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将多个文本转换为向量"""
        return self._model.encode(texts).tolist()
