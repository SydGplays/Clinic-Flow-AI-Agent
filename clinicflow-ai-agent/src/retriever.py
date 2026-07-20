"""Recuperación semántica mediante Sentence Transformers y FAISS."""

from __future__ import annotations

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class ClinicRetriever:
    """Índice vectorial en memoria para documentos breves de la clínica."""

    def __init__(
        self,
        documents: list[dict[str, str]],
        model_name: str = DEFAULT_MODEL,
    ) -> None:
        if not documents:
            raise ValueError("Se requiere al menos un documento para crear el índice.")

        self.documents = documents
        self.model = SentenceTransformer(model_name)
        texts = [document["embedding_text"] for document in documents]
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype("float32")
        faiss.normalize_L2(embeddings)

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        """Devuelve los documentos más próximos por similitud coseno."""
        clean_query = query.strip()
        if not clean_query:
            return []

        query_embedding = self.model.encode(
            [clean_query],
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype("float32")
        faiss.normalize_L2(query_embedding)

        limit = min(max(top_k, 1), len(self.documents))
        scores, indices = self.index.search(query_embedding, limit)
        results: list[dict] = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue
            document = {
                key: value
                for key, value in self.documents[index].items()
                if key != "embedding_text"
            }
            document["score"] = float(np.clip(score, 0.0, 1.0))
            results.append(document)
        return results
