from modules.datetime_parser import parse_datetime

tests = [
    "mañana a las 8pm",
    "hoy a las 10pm",
    "miércoles a las 8pm",
    "viernes a las 6pm",
    "en 30 minutos",
    "en 2 horas"
]

for t in tests:

    print(t)

    print(
        parse_datetime(t)
    )

    print()