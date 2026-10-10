from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    _model: Optional[SentenceTransformer] = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return cls._model

    @classmethod
    def get_embedding(cls, text: str) -> np.ndarray:
        model = cls.get_model()
        if not text or not text.strip():
            dim = model.get_sentence_embedding_dimension()
            return np.zeros(dim, dtype=np.float32)
        return model.encode(text, convert_to_numpy=True, normalize_embeddings=True)

    @classmethod
    def compute_similarity(cls, text_a: str, text_b: str) -> float:
        emb_a = cls.get_embedding(text_a)
        emb_b = cls.get_embedding(text_b)
        
        # When both or either embedding is a zero-vector
        norm_a = np.linalg.norm(emb_a)
        norm_b = np.linalg.norm(emb_b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        # Embeddings are normalized; dot product equals cosine similarity
        sim = float(np.dot(emb_a, emb_b))
        # Rescale [-1.0, 1.0] to [0.0, 1.0]
        return max(0.0, min(1.0, (sim + 1.0) / 2.0))