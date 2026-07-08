import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH


# ==================================================
# TIPOS DE MEMORIA VÁLIDOS
# ==================================================

VALID_MEMORY_TYPES = {
    "object_location",
    "preference",
    "task",
    "person",
    "fact",
}


# ==================================================
# EXISTENCIA DE MEMORIA (anti-duplicados)
# ==================================================

def memory_exists(memory_type, content):
    """
    Verifica si ya existe una memoria con el mismo
    memory_type y content (comparación exacta).

    Devuelve el ID existente o None si no existe.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM memories
        WHERE memory_type = ?
        AND content = ?
        LIMIT 1
        """,
        (memory_type, content)
    )

    row = cursor.fetchone()
    conn.close()

    if row is not None:
        return row[0]

    return None


# ==================================================
# GUARDAR MEMORIA
# ==================================================

def save_memory(memory_type, content, created_at):
    """
    Guarda una memoria nueva.
    Si ya existe una memoria idéntica (mismo tipo + contenido),
    devuelve el ID existente sin insertar duplicado.
    """

    # Normalizar memory_type desconocido
    if memory_type not in VALID_MEMORY_TYPES:
        memory_type = "fact"

    existing_id = memory_exists(memory_type, content)

    if existing_id is not None:
        return existing_id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO memories(
            memory_type,
            content,
            created_at,
            completed
        )
        VALUES(?, ?, ?, 0)
        """,
        (memory_type, content, created_at)
    )

    memory_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return memory_id


# ==================================================
# OBTENER MEMORIA POR ID
# ==================================================

def get_memory(memory_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, memory_type, content, created_at
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row


# ==================================================
# OBTENER MEMORIAS POR TIPO
# ==================================================

def get_memories_by_type(memory_type):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, memory_type, content, created_at
        FROM memories
        WHERE memory_type = ?
        AND completed = 0
        """,
        (memory_type,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


# ==================================================
# OBTENER TIPO DE MEMORIA
# ==================================================

def get_memory_type(memory_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT memory_type
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return row[0]


# ==================================================
# COMPLETAR TAREA
# ==================================================

def complete_task_by_id(memory_id):
    """Marca una tarea como completada (no la elimina)."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE memories
        SET completed = 1
        WHERE id = ?
        """,
        (memory_id,)
    )

    conn.commit()
    conn.close()


# ==================================================
# LISTAR TAREAS PENDIENTES
# ==================================================

def get_pending_tasks():
    """Devuelve todas las tareas pendientes (no completadas)."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, memory_type, content, created_at
        FROM memories
        WHERE memory_type = 'task'
        AND completed = 0
        ORDER BY created_at
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return rows
