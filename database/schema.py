import sqlite3

conn = sqlite3.connect("../database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT UNIQUE,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    remind_at DATETIME,
    executed INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    created_at DATETIME
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT,
    completed INTEGER DEFAULT 0
)
""")

# Migración: agregar columna completed si no existe
try:
    cursor.execute("ALTER TABLE memories ADD COLUMN completed INTEGER DEFAULT 0")
    print("Columna 'completed' agregada a memories.")
except Exception:
    pass  # Ya existe

conn.commit()
conn.close()

print("Base de datos lista.")

# ==================================================
# PDF RAG — tablas nuevas (Fase 7)
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS pdf_documents(
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    filename   TEXT NOT NULL,
    filepath   TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pdf_chunks(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES pdf_documents(id)
)
""")

# Migración: columna completed en memories si no existe
try:
    cursor.execute("ALTER TABLE memories ADD COLUMN completed INTEGER DEFAULT 0")
except Exception:
    pass

conn.commit()
conn.close()

print("Base de datos lista (incluyendo tablas PDF).")
