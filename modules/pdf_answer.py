"""
pdf_answer.py

Genera respuestas a preguntas sobre PDFs usando los chunks
recuperados por búsqueda semántica como contexto para Qwen.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_MODEL

from ollama import chat


def answer_from_chunks(question, chunks):
    """
    Genera una respuesta usando los chunks relevantes como contexto.

    question: pregunta del usuario (str)
    chunks:   lista de strings con los chunks recuperados
    """

    context = "\n\n---\n\n".join(chunks)

    response = chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Eres FredoGodoFredo.

Responde la pregunta del usuario usando ÚNICAMENTE el contexto proporcionado.

Si el contexto no contiene información suficiente para responder:
- Indica claramente que no encontraste esa información en el documento.

No inventes información.
No agregues datos externos al contexto.

Responde de forma directa y concisa.

No uses frases como:
- Buena pregunta
- Interesante
- Excelente observación
"""
            },
            {
                "role": "user",
                "content": f"""
Pregunta:
{question}

Contexto del documento:
{context}
"""
            }
        ]
    )

    return response.message.content
