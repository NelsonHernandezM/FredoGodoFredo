"""
pdf_loader.py

Carga PDFs con texto seleccionable, los divide en chunks,
guarda metadatos en SQLite y genera embeddings en FAISS.

NO soporta OCR ni PDFs escaneados.
"""

import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DB_PATH,
    DEBUG,
    PDF_CHUNK_SIZE,
    PDF_CHUNK_OVERLAP,
)

from modules.vector_memory import add_memory

import fitz  # PyMuPDF


# ==================================================
# EXTRACCIÓN DE TEXTO
# ==================================================

def extract_text_from_pdf(filepath):
    """
    Extrae texto de un PDF con texto seleccionable.

    Retorna el texto completo como string.
    Retorna None si el PDF no tiene texto (posiblemente escaneado).
    """

    doc = fitz.open(filepath)

    pages_text = []

    for page_num, page in enumerate(doc):

        text = page.get_text()

        if text:
            pages_text.append(text)

    doc.close()

    if not pages_text:
        return None

    full_text = "\n".join(pages_text)

    # Verificar que el texto tiene contenido real (no solo espacios)
    if len(full_text.strip()) < 50:
        return None

    return full_text


# ==================================================
# CHUNKING
# ==================================================

def split_into_chunks(text, chunk_size=PDF_CHUNK_SIZE, overlap=PDF_CHUNK_OVERLAP):
    """
    Divide texto en chunks por palabras con solapamiento.

    chunk_size: número aproximado de palabras por chunk.
    overlap: número de palabras de solapamiento entre chunks.
    """

    words = text.split()

    if len(words) == 0:
        return []

    chunks = []
    start  = 0

    while start < len(words):

        end   = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


# ==================================================
# PERSISTENCIA EN SQLITE
# ==================================================

def save_pdf_document(filename, filepath):
    """
    Guarda un documento PDF en la tabla pdf_documents.
    Si el filepath ya existe, devuelve el ID existente.
    """

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificar si ya fue cargado
    cursor.execute(
        "SELECT id FROM pdf_documents WHERE filepath = ? LIMIT 1",
        (filepath,)
    )
    row = cursor.fetchone()

    if row is not None:
        conn.close()
        return row[0], True  # (id, ya_existía)

    cursor.execute(
        """
        INSERT INTO pdf_documents(filename, filepath, created_at)
        VALUES(?, ?, ?)
        """,
        (filename, filepath, str(datetime.now()))
    )

    doc_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return doc_id, False  # (id, nuevo)


def save_pdf_chunk(document_id, chunk_index, content):
    """
    Guarda un chunk en la tabla pdf_chunks.
    Devuelve el ID del chunk.
    """

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pdf_chunks(document_id, chunk_index, content, created_at)
        VALUES(?, ?, ?, ?)
        """,
        (document_id, chunk_index, content, str(datetime.now()))
    )

    chunk_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return chunk_id


def get_chunk_by_id(chunk_id):
    """Devuelve un chunk por su ID."""

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, document_id, chunk_index, content
        FROM pdf_chunks
        WHERE id = ?
        """,
        (chunk_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row


def get_document_info(document_id):
    """Devuelve info del documento PDF."""

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, filename, filepath, created_at FROM pdf_documents WHERE id = ?",
        (document_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row


def list_pdf_documents():
    """Lista todos los documentos PDF cargados."""

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, filename, filepath, created_at FROM pdf_documents ORDER BY created_at"
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


# ==================================================
# CARGA COMPLETA
# ==================================================

def load_pdf(filepath):
    """
    Proceso completo:
    1. Verificar que el archivo existe.
    2. Extraer texto.
    3. Detectar si es escaneado (sin texto).
    4. Dividir en chunks.
    5. Guardar en SQLite.
    6. Generar embeddings y guardar en FAISS.

    Retorna dict con resultado.
    """

    # 1. Verificar existencia
    if not os.path.exists(filepath):
        return {
            "success": False,
            "error":   f"Archivo no encontrado: {filepath}"
        }

    if not filepath.lower().endswith(".pdf"):
        return {
            "success": False,
            "error":   "El archivo no es un PDF."
        }

    filename = os.path.basename(filepath)

    # 2. Verificar si ya fue cargado
    doc_id, ya_existia = save_pdf_document(filename, filepath)

    if ya_existia:
        return {
            "success":    False,
            "error":      f"El PDF '{filename}' ya fue cargado anteriormente.",
            "document_id": doc_id
        }

    # 3. Extraer texto
    if DEBUG:
        print(f"[PDF] Extrayendo texto de: {filename}")

    text = extract_text_from_pdf(filepath)

    if text is None:
        # Eliminar el registro recién creado
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pdf_documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()

        return {
            "success": False,
            "error":   (
                "El PDF no contiene texto seleccionable. "
                "Posiblemente es un documento escaneado. "
                "OCR aún no está implementado."
            )
        }

    # 4. Dividir en chunks
    chunks = split_into_chunks(text)

    if DEBUG:
        print(f"[PDF] Chunks generados: {len(chunks)}")
        for i, c in enumerate(chunks):
            preview = c[:80].replace("\n", " ")
            print(f"  Chunk {i}: {preview}...")

    # 5. Guardar chunks en SQLite y embeddings en FAISS
    chunk_ids = []

    for i, chunk_text in enumerate(chunks):

        chunk_id = save_pdf_chunk(doc_id, i, chunk_text)
        chunk_ids.append(chunk_id)

        # Insertar en FAISS con tipo "pdf_chunk"
        add_memory(chunk_id, chunk_text, memory_type="pdf_chunk")

        if DEBUG:
            print(f"  [FAISS] Chunk {i} indexado (ID {chunk_id})")

    return {
        "success":     True,
        "filename":    filename,
        "document_id": doc_id,
        "chunks":      len(chunks),
        "chunk_ids":   chunk_ids
    }
