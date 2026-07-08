# FredoGodoFredo

FredoGodoFredo es un asistente personal privado ejecutado completamente de forma local mediante Ollama.

El proyecto implementa un pipeline de Inteligencia Artificial basado en memoria semántica, recuperación de información (Retrieval-Augmented Generation, RAG) y generación mediante Large Language Models (LLM).

Todo el procesamiento se realiza localmente sin depender de servicios en la nube.

---

# Características

- Memoria persistente en SQLite.
- Memoria semántica mediante embeddings.
- Índice vectorial con FAISS.
- Recuperación de contexto antes de consultar al LLM.
- RAG sobre documentos PDF.
- Recordatorios con interpretación de fechas en lenguaje natural.
- Sistema de tareas.
- Almacenamiento de preferencias.
- Almacenamiento de ubicación de objetos.
- Ejecución completamente local utilizando Ollama.

---

# Arquitectura

```
                 Usuario
                    │
                    ▼
         Clasificación de intención
                    │
      ┌─────────────┴─────────────┐
      │                           │
      ▼                           ▼
 Memoria                    Consulta PDF
      │                           │
Embeddings                 Embeddings
      │                           │
      ▼                           ▼
    FAISS                     FAISS
      │                           │
      └─────────────┬─────────────┘
                    │
                    ▼
      Recuperación del contexto
                    │
                    ▼
        Construcción del Prompt
                    │
                    ▼
          Ollama (Qwen3 8B)
                    │
                    ▼
              Respuesta final
```

---

# Pipeline de IA

El flujo general es:

1. El usuario realiza una consulta.
2. El sistema identifica la intención.
3. Se generan embeddings utilizando:

```
intfloat/multilingual-e5-small
```

4. Se realiza búsqueda semántica mediante FAISS.
5. Se recuperan memorias relevantes.
6. Se construye el prompt enriquecido.
7. El modelo Qwen genera la respuesta final.

Este flujo constituye un pipeline de Retrieval-Augmented Generation (RAG).

---

# Tecnologías

- Python
- Ollama
- Qwen3
- SQLite
- FAISS
- Sentence Transformers
- PyMuPDF
- NumPy

---

# Modelos utilizados

## LLM

Qwen3 8B

## Embeddings

intfloat/multilingual-e5-small

---

# Funciones

## Memoria

Ejemplo:

```
Mi nombre es Nelson.
```

Después:

```
¿Cómo me llamo?
```

El sistema recupera la memoria y responde correctamente.

---

## Objetos

```
Guardé las llaves en el escritorio.
```

Posteriormente:

```
¿Dónde están mis llaves?
```

---

## Preferencias

```
No me hables de forma muy formal.
```

---

## Recordatorios

```
Recuérdame llamar a Juan mañana a las 7 pm.
```

---

## RAG sobre PDFs

Puede indexar documentos PDF y responder preguntas utilizando únicamente la información contenida en ellos.

---
 

 

# Autor

Nelson Hernández Morales

Doctorado en Ciencias de la Ingeniería

Universidad Autónoma de Tamaulipas
