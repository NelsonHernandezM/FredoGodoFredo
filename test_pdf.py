"""
test_pdf.py

Script de prueba para el sistema RAG de PDFs.

Uso:
    python test_pdf.py <ruta_pdf>
    python test_pdf.py <ruta_pdf> --query "¿Qué dice sobre X?"

Ejemplos:
    python test_pdf.py documento.pdf
    python test_pdf.py tesis.pdf --query "¿Cuál es la metodología?"
"""

import sys
import os
import time

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEBUG, PDF_TOP_K, MAX_PDF_DISTANCE

from modules.pdf_loader import (
    load_pdf,
    get_chunk_by_id,
    get_document_info,
    list_pdf_documents,
    split_into_chunks,
    extract_text_from_pdf,
)

from modules.vector_memory import search_pdf_chunks
from modules.pdf_answer import answer_from_chunks


def separador(titulo=""):
    linea = "=" * 50
    if titulo:
        print(f"\n{linea}")
        print(f"  {titulo}")
        print(linea)
    else:
        print(linea)


def test_cargar_pdf(filepath):
    """Carga un PDF y muestra estadísticas."""

    separador("CARGA DE PDF")
    print(f"  Archivo: {filepath}")

    t0     = time.time()
    result = load_pdf(filepath)
    elapsed = time.time() - t0

    if not result["success"]:
        print(f"\n[ERROR] {result['error']}")
        return False

    print(f"\n  Resultado: OK")
    print(f"  Nombre:    {result['filename']}")
    print(f"  ID doc:    {result['document_id']}")
    print(f"  Chunks:    {result['chunks']}")
    print(f"  Tiempo:    {elapsed:.2f}s")

    return True


def test_preview_chunks(filepath):
    """Extrae texto y muestra los primeros chunks sin indexar."""

    separador("PREVIEW DE CHUNKS")

    text = extract_text_from_pdf(filepath)

    if text is None:
        print("  [ERROR] El PDF no tiene texto seleccionable.")
        return

    chunks = split_into_chunks(text)

    print(f"  Total de palabras: {len(text.split())}")
    print(f"  Total de chunks:   {len(chunks)}")
    print()

    max_preview = min(3, len(chunks))

    for i in range(max_preview):
        preview = chunks[i][:200].replace("\n", " ")
        print(f"  --- Chunk {i} ---")
        print(f"  {preview}...")
        print()


def test_consulta(query):
    """Realiza una consulta semántica sobre los PDFs cargados."""

    separador(f"CONSULTA")
    print(f"  Pregunta: {query}")
    print()

    t0      = time.time()
    results = search_pdf_chunks(query, k=PDF_TOP_K)
    t_search = time.time() - t0

    print(f"  Candidatos encontrados: {len(results)}")
    print(f"  Tiempo de búsqueda:     {t_search:.4f}s")
    print()

    # Filtrar por umbral
    valid = [
        (cid, dist)
        for cid, dist in results
        if dist <= MAX_PDF_DISTANCE
    ]

    print(f"  Chunks válidos (dist <= {MAX_PDF_DISTANCE}): {len(valid)}")

    if not valid:
        print("\n  No se encontraron chunks relevantes.")
        return

    print()

    # Mostrar chunks recuperados
    chunks_text = []

    for rank, (chunk_id, dist) in enumerate(valid):

        chunk = get_chunk_by_id(chunk_id)

        if chunk is None:
            continue

        doc   = get_document_info(chunk[1])
        doc_name = doc[1] if doc else "?"

        preview = chunk[3][:200].replace("\n", " ")
        chunks_text.append(chunk[3])

        print(f"  Chunk #{rank + 1}")
        print(f"    Documento:  {doc_name}")
        print(f"    Índice:     {chunk[2]}")
        print(f"    Distancia:  {dist:.4f}")
        print(f"    Contenido:  {preview}...")
        print()

    # Generar respuesta
    separador("RESPUESTA")
    print()

    t0     = time.time()
    answer = answer_from_chunks(query, chunks_text)
    t_llm  = time.time() - t0

    print(f"  Fredo: {answer}")
    print()
    print(f"  Tiempo de respuesta (LLM): {t_llm:.2f}s")


def listar_documentos():
    """Lista todos los PDFs cargados."""

    separador("DOCUMENTOS CARGADOS")

    docs = list_pdf_documents()

    if not docs:
        print("  No hay documentos cargados.")
        return

    for doc in docs:
        print(f"  [{doc[0]}] {doc[1]}")
        print(f"       Ruta:    {doc[2]}")
        print(f"       Cargado: {doc[3]}")
        print()


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    args = sys.argv[1:]

    if not args:
        print("Uso:")
        print("  python test_pdf.py <ruta_pdf>")
        print("  python test_pdf.py <ruta_pdf> --query \"tu pregunta\"")
        print("  python test_pdf.py --list")
        sys.exit(0)

    # Listar documentos
    if args[0] == "--list":
        listar_documentos()
        sys.exit(0)

    filepath = args[0]

    # Verificar si hay query
    query = None
    if "--query" in args:
        idx   = args.index("--query")
        if idx + 1 < len(args):
            query = args[idx + 1]

    # Si no hay query: solo cargar y mostrar preview
    if query is None:

        # Mostrar preview sin cargar
        if os.path.exists(filepath):
            test_preview_chunks(filepath)

        # Cargar
        ok = test_cargar_pdf(filepath)

        if ok:
            print()
            listar_documentos()
            print()
            print("Para hacer consultas:")
            print(f'  python test_pdf.py "{filepath}" --query "tu pregunta"')

    else:

        # Cargar si no existe en DB
        if os.path.exists(filepath):
            result = load_pdf(filepath)
            if result["success"]:
                print(f"PDF cargado: {result['filename']} ({result['chunks']} chunks)")
            elif "ya fue cargado" in result.get("error", ""):
                print(f"PDF ya estaba cargado.")
            else:
                print(f"[ERROR] {result['error']}")
                sys.exit(1)

        # Consulta
        test_consulta(query)
