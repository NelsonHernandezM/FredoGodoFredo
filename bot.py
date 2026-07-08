from datetime import datetime

from config import DEBUG, MAX_MEMORY_DISTANCE, MAX_TASK_COMPLETE_DISTANCE, PDF_TOP_K, MAX_PDF_DISTANCE

from modules.memory_answer import answer_from_memory
from modules.ai import ask_ai
from modules.parser import parse_response
from modules.reminders import save_reminder
from modules.datetime_parser import parse_datetime

from modules.memory_store import (
    save_memory,
    get_memory,
    get_memories_by_type,
    get_memory_type,
    complete_task_by_id,
    get_pending_tasks,
    memory_exists,
)

from modules.vector_memory import (
    add_memory,
    search_memory,
    search_pdf_chunks,
)

from modules.pdf_loader import (
    load_pdf,
    get_chunk_by_id,
    get_document_info,
    list_pdf_documents,
)

from modules.pdf_answer import answer_from_chunks

pending_action = None


while True:

    texto = input("Tu: ")

    if texto.lower() == "salir":
        break

    # ==========================================
    # ACCIÓN PENDIENTE
    # ==========================================

    if pending_action is not None:

        if pending_action["action"] == "reminder":

            remind_at = parse_datetime(texto)

            if remind_at is None:

                print("\nFredo: No entendí la fecha.")
                print("Ejemplos:")
                print("- mañana a las 8pm")
                print("- miércoles a las 6pm")
                print("- en 30 minutos")
                continue

            save_reminder(pending_action["message"], remind_at)
            print(f"\nFredo: Recordatorio guardado para {remind_at}")
            pending_action = None
            continue

    # ==========================================
    # IA
    # ==========================================

    raw = ask_ai(texto)

    if DEBUG:
        print("\nJSON:")
        print(raw)

    data = parse_response(raw)

    action = data.get("action")

    # ==========================================
    # MEMORY
    # ==========================================

    if action == "memory":

        fact        = data.get("fact")
        memory_type = data.get("memory_type", "fact")

        # Verificar duplicado antes de insertar
        existing_id = memory_exists(memory_type, fact)

        if existing_id is not None:
            print(f"\nFredo: Ya tenía eso guardado.")

        else:
            memory_id = save_memory(
                memory_type,
                fact,
                str(datetime.now())
            )

            add_memory(memory_id, fact)

            print(f"\nFredo: Memoria guardada.")

            if DEBUG:
                print(f"  (ID {memory_id}, tipo: {memory_type})")

    # ==========================================
    # SEARCH MEMORY
    # ==========================================

    elif action == "search_memory":

        query       = data.get("query")
        memory_type = data.get("memory_type")

        if DEBUG:
            print(f"\nBuscando tipo: {memory_type} | query: {query}")

        # Tareas: listado directo desde SQLite
        if memory_type == "task":

            tasks = get_pending_tasks()

            if len(tasks) == 0:
                print("\nFredo: No tienes tareas pendientes.")
            else:
                print("\nFredo: Tus tareas pendientes:")
                for task in tasks:
                    print(f"  - [{task[0]}] {task[2]}")

            print()
            continue

        # Preferences y otros: búsqueda semántica + filtro tipo
        results = search_memory(query, k=3)

        if len(results) == 0:
            print("\nFredo: No encontré información sobre eso.")
            print()
            continue

        # Filtrar por tipo
        filtered = [
            (mid, dist)
            for mid, dist in results
            if get_memory_type(mid) == memory_type
        ]

        if len(filtered) == 0:
            print("\nFredo: No encontré información sobre eso.")
            print()
            continue

        best_id, best_distance = filtered[0]

        if DEBUG:
            print(f"  Distancia: {best_distance:.4f}")

        if best_distance > MAX_MEMORY_DISTANCE:
            print("\nFredo: No encontré información sobre eso.")
            print()
            continue

        memory = get_memory(best_id)

        if memory is None:
            print("\nFredo: No encontré información sobre eso.")
            print()
            continue

        answer = answer_from_memory(query, memory[2])
        print(f"\nFredo: {answer}")

    # ==========================================
    # COMPLETE TASK
    # ==========================================

    elif action == "complete_task":

        query = data.get("query")

        results = search_memory(query, k=5)

        if len(results) == 0:
            print("\nFredo: No encontré una tarea pendiente relacionada.")
            print()
            continue

        # Filtrar solo tasks con umbral estricto
        task_matches = [
            (mid, dist)
            for mid, dist in results
            if get_memory_type(mid) == "task"
        ]

        if len(task_matches) == 0:
            print("\nFredo: No encontré una tarea pendiente relacionada.")
            print()
            continue

        best_id, best_distance = task_matches[0]

        if DEBUG:
            task_row = get_memory(best_id)
            print(f"  Tarea candidata: {task_row[2]}")
            print(f"  Distancia: {best_distance:.4f} (umbral: {MAX_TASK_COMPLETE_DISTANCE})")

        if best_distance > MAX_TASK_COMPLETE_DISTANCE:
            print("\nFredo: No encontré una tarea pendiente relacionada.")
            print()
            continue

        task = get_memory(best_id)
        complete_task_by_id(best_id)
        print(f"\nFredo: Tarea completada: {task[2]}")

    # ==========================================
    # REMINDER
    # ==========================================

    elif action == "reminder":

        message   = data.get("message")
        remind_at = parse_datetime(message)

        if remind_at is None:

            pending_action = {
                "action": "reminder",
                "message": message
            }

            print("\nFredo: ¿Para qué fecha y hora?")

        else:

            save_reminder(message, remind_at)
            print(f"\nFredo: Recordatorio guardado para {remind_at}")

    # ==========================================
    # LOAD PDF
    # ==========================================

    elif action == "load_pdf":

        filepath = data.get("filepath", "").strip()

        if not filepath:
            print("\nFredo: ¿Cuál es la ruta del archivo PDF?")

        else:
            print(f"\nFredo: Cargando PDF...")

            result = load_pdf(filepath)

            if result["success"]:
                print(
                    f"\nFredo: PDF cargado correctamente.\n"
                    f"  Archivo: {result['filename']}\n"
                    f"  Chunks generados: {result['chunks']}"
                )
            else:
                print(f"\nFredo: {result['error']}")

    # ==========================================
    # SEARCH PDF
    # ==========================================

    elif action == "search_pdf":

        query = data.get("query")

        if DEBUG:
            print(f"\n[PDF] Buscando: {query}")

        results = search_pdf_chunks(query, k=PDF_TOP_K)

        if len(results) == 0:
            print("\nFredo: No encontré información relacionada en los documentos.")
            print()
            continue

        # Filtrar por umbral de distancia
        valid = [
            (cid, dist)
            for cid, dist in results
            if dist <= MAX_PDF_DISTANCE
        ]

        if len(valid) == 0:
            print("\nFredo: No encontré información relacionada en los documentos.")
            print()
            continue

        if DEBUG:
            import time
            t0 = time.time()

        # Recuperar texto de los chunks
        chunks_text = []
        for chunk_id, dist in valid:
            chunk = get_chunk_by_id(chunk_id)
            if chunk is not None:
                chunks_text.append(chunk[3])  # content
                if DEBUG:
                    doc = get_document_info(chunk[1])
                    doc_name = doc[1] if doc else "?"
                    preview  = chunk[3][:80].replace("\n", " ")
                    print(f"  [Chunk {chunk[2]} | doc: {doc_name} | dist: {dist:.4f}]")
                    print(f"  {preview}...")

        if not chunks_text:
            print("\nFredo: No encontré información relacionada en los documentos.")
            print()
            continue

        answer = answer_from_chunks(query, chunks_text)

        if DEBUG:
            elapsed = time.time() - t0
            print(f"  [PDF] Tiempo total: {elapsed:.2f}s")

        print(f"\nFredo: {answer}")

    # ==========================================
    # NOTE
    # ==========================================

    elif action == "note":

        print("\nFredo: Nota detectada.")

    # ==========================================
    # CHAT
    # ==========================================

    else:

        print("\nFredo:", data.get("response"))

    print()
