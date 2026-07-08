import os
import json
import faiss
import numpy as np
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEBUG, EMBEDDING_MODEL, EMBEDDING_DIMENSION

from sentence_transformers import SentenceTransformer


# ==================================================
# RUTAS
# ==================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAISS_DIR  = os.path.join(BASE_DIR, "data", "faiss")
os.makedirs(FAISS_DIR, exist_ok=True)

INDEX_PATH = os.path.join(FAISS_DIR, "memory.index")
MAP_PATH   = os.path.join(FAISS_DIR, "memory_map.json")


# ==================================================
# MODELO — se carga UNA SOLA VEZ al importar el módulo
# ==================================================

model = SentenceTransformer(EMBEDDING_MODEL)


# ==================================================
# ÍNDICE
# ==================================================

def load_index():

    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)

    return faiss.IndexFlatL2(EMBEDDING_DIMENSION)


# ==================================================
# MAPA — formato: [{"id": X, "type": "preference"}, ...]
# Migración automática desde formato antiguo [int, int, ...]
# ==================================================

def load_map():

    if not os.path.exists(MAP_PATH):
        return []

    with open(MAP_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Migración: si el mapa contiene enteros (formato antiguo),
    # convertir a dicts con type="memory" como marcador genérico.
    if data and isinstance(data[0], int):
        data = [{"id": entry, "type": "memory"} for entry in data]
        _save_map(data)  # persistir migración

    return data


def _save_map(memory_map):
    with open(MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(memory_map, f, ensure_ascii=False, indent=4)


def save_index(index):
    faiss.write_index(index, INDEX_PATH)


# ==================================================
# INSERTAR MEMORIA
# ==================================================

def add_memory(memory_id, text, memory_type="memory"):
    """
    Agrega un vector al índice FAISS.

    memory_type: tipo de memoria para filtrado posterior.
    Ejemplos: "preference", "object_location", "task",
              "person", "fact", "pdf_chunk"
    """

    index      = load_index()
    memory_map = load_map()

    vector = model.encode(text, normalize_embeddings=True)
    vector = np.array([vector], dtype=np.float32)

    index.add(vector)
    memory_map.append({"id": memory_id, "type": memory_type})

    save_index(index)
    _save_map(memory_map)


# ==================================================
# BÚSQUEDA GENERAL
# ==================================================

def search_memory(query, k=5):
    """
    Busca en el índice FAISS.
    Devuelve lista de (id, distance) para todos los tipos.
    """

    index      = load_index()
    memory_map = load_map()

    if len(memory_map) == 0:
        return []

    vector = model.encode(query, normalize_embeddings=True)
    vector = np.array([vector], dtype=np.float32)

    k = min(k, len(memory_map))

    distances, indices = index.search(vector, k)

    if DEBUG:
        print()
        print("===================================")
        print("QUERY:", query)
        print("DISTANCIAS:", distances)
        print("INDICES:", indices)
        print("===================================")
        print()

    results = []

    for distance, idx in zip(distances[0], indices[0]):

        if 0 <= idx < len(memory_map):
            entry = memory_map[idx]
            results.append((entry["id"], float(distance), entry["type"]))

    return results


# ==================================================
# BÚSQUEDA FILTRADA POR TIPO
# ==================================================

def search_memory_by_type(query, memory_type, k=5):
    """
    Busca en FAISS y devuelve solo resultados del tipo indicado.
    Recupera k*3 candidatos para compensar el filtrado.
    Devuelve lista de (id, distance).
    """

    all_results = search_memory(query, k=k * 3)

    filtered = [
        (mid, dist)
        for mid, dist, mtype in all_results
        if mtype == memory_type
    ]

    return filtered[:k]


# ==================================================
# BÚSQUEDA ESPECÍFICA PDF
# ==================================================

def search_pdf_chunks(query, k=5):
    """
    Búsqueda semántica limitada a chunks de PDF.
    Devuelve lista de (chunk_id, distance).
    """
    return search_memory_by_type(query, "pdf_chunk", k=k)


# ==================================================
# RESET
# ==================================================

def reset_memory():

    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)

    if os.path.exists(MAP_PATH):
        os.remove(MAP_PATH)
