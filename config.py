# ==================================================
# CONFIGURACIÓN GLOBAL DE FREDOGODOFREDO
# ==================================================

# Modo debug: True muestra logs internos de FAISS,
# distancias y mensajes de depuración.
# False = uso normal sin ruido en consola.
DEBUG = False

# Umbral máximo de distancia FAISS para aceptar un resultado.
# Menor = más estricto. Valor recomendado: 0.35 - 0.45
MAX_MEMORY_DISTANCE = 0.40

# Umbral más estricto para complete_task, para evitar
# completar accidentalmente la tarea equivocada.
MAX_TASK_COMPLETE_DISTANCE = 0.30

# Ruta de la base de datos SQLite
DB_PATH = "database.db"

# Modelo de lenguaje (Ollama)
LLM_MODEL = "qwen3:8b"

# Modelo de embeddings
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_DIMENSION = 384

# Zona horaria
TIMEZONE = "America/Matamoros"

# Intervalo del scheduler en segundos
SCHEDULER_INTERVAL = 60

# ==================================================
# PDF RAG
# ==================================================

# Tamaño aproximado de cada chunk en palabras
PDF_CHUNK_SIZE = 500

# Solapamiento entre chunks en palabras
PDF_CHUNK_OVERLAP = 100

# Número de chunks a recuperar en búsqueda semántica
PDF_TOP_K = 4

# Umbral de distancia FAISS para pdf_chunk
MAX_PDF_DISTANCE = 0.55
