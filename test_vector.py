from modules.vector_memory import (
    add_memory,
    search_memory,
    reset_memory
)

reset_memory()

add_memory(
    "Guardé el lápiz azul en el cajón del escritorio"
)

add_memory(
    "Las llaves del coche están en la mochila negra"
)

add_memory(
    "La garantía de la televisión está en la carpeta documentos"
)

queries = [
    "¿Dónde está mi lapicero azul?",
    "¿Dónde dejé las llaves?",
    "¿Dónde está la garantía de la tele?"
]

for q in queries:

    print("\n====================")
    print(q)
    print("====================")

    results = search_memory(q)

    for r in results:
        print(r)