import json

def parse_response(text):

    try:
        return json.loads(text)

    except Exception:

        return {
            "action":"chat",
            "response":"Error interpretando respuesta"
        }