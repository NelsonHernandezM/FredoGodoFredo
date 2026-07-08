import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_MODEL

from ollama import chat


def answer_from_memory(question, memory):

    response = chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Eres FredoGodoFredo.

Responde usando únicamente la memoria proporcionada.

Si la memoria responde la pregunta, responde de forma breve.

No inventes información.

No agregues datos nuevos.

No uses frases como:
- Buena pregunta
- Interesante
- Excelente observación

Ejemplo:

Pregunta:
¿Dónde está mi lápiz?

Memoria:
Guardé mi lápiz azul en el escritorio

Respuesta:
Tu lápiz azul está en el escritorio.
"""
            },
            {
                "role": "user",
                "content": f"""
Pregunta:
{question}

Memoria:
{memory}
"""
            }
        ]
    )

    return response.message.content
