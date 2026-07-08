from datetime import datetime

from modules.memory_store import (
    save_memory,
    get_memory
)

from modules.vector_memory import (
    add_memory,
    search_memory,
    reset_memory
)

reset_memory()

memory_id = save_memory(
    "object_location",
    "Guardé el lápiz azul en el cajón del escritorio",
    str(datetime.now())
)

add_memory(
    memory_id,
    "Guardé el lápiz azul en el cajón del escritorio"
)

results = search_memory(
    "¿Dónde está mi lapicero azul?"
)

print(results)

for memory_id in results:

    print(
        get_memory(memory_id)
    )