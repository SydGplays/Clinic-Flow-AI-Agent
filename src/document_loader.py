"""Carga y validación de la base de conocimiento clínica."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"id", "category", "title", "content", "source"}


def load_knowledge_base(csv_path: str | Path) -> list[dict[str, str]]:
    """Carga un CSV UTF-8 y devuelve documentos limpios y validados."""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró la base de conocimiento: {path}")

    frame = pd.read_csv(path, encoding="utf-8")
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(
            "Faltan columnas requeridas en el CSV: " + ", ".join(sorted(missing))
        )

    frame = frame[list(REQUIRED_COLUMNS)].fillna("")
    frame = frame.drop_duplicates(subset=["id"]).reset_index(drop=True)
    if frame.empty:
        raise ValueError("La base de conocimiento está vacía.")
    if (frame["content"].str.strip() == "").any():
        raise ValueError("Todos los registros deben tener contenido.")

    documents: list[dict[str, str]] = []
    for row in frame.to_dict(orient="records"):
        document = {key: str(value).strip() for key, value in row.items()}
        document["embedding_text"] = (
            f"Categoría: {document['category']}. "
            f"Título: {document['title']}. "
            f"Información: {document['content']}"
        )
        documents.append(document)
    return documents
