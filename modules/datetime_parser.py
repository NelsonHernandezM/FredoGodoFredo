from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

TZ = ZoneInfo("America/Matamoros")

WEEKDAYS = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6
}

def extract_hour(text):

    match = re.search(
        r'(\d{1,2})\s*(am|pm)',
        text
    )

    if not match:
        return None

    hour = int(match.group(1))
    period = match.group(2)

    if period == "pm" and hour != 12:
        hour += 12

    if period == "am" and hour == 12:
        hour = 0

    return hour


def parse_datetime(text):

    now = datetime.now(TZ)

    text = text.lower().strip()

    # =====================================
    # mañana
    # =====================================

    if "mañana" in text:

        hour = extract_hour(text)

        if hour is None:
            return None

        target = now + timedelta(days=1)

        return target.replace(
            hour=hour,
            minute=0,
            second=0,
            microsecond=0
        )

    # =====================================
    # hoy
    # =====================================

    if "hoy" in text:

        hour = extract_hour(text)

        if hour is None:
            return None

        return now.replace(
            hour=hour,
            minute=0,
            second=0,
            microsecond=0
        )

    # =====================================
    # dias de la semana
    # =====================================

    for day_name in WEEKDAYS:

        if day_name in text:

            hour = extract_hour(text)

            if hour is None:
                return None

            target_day = WEEKDAYS[day_name]

            current_day = now.weekday()

            days_ahead = (
                target_day - current_day
            ) % 7

            if days_ahead == 0:
                days_ahead = 7

            target = now + timedelta(
                days=days_ahead
            )

            return target.replace(
                hour=hour,
                minute=0,
                second=0,
                microsecond=0
            )

    # =====================================
    # en X minutos
    # =====================================

    match = re.search(
        r'en\s+(\d+)\s+minutos?',
        text
    )

    if match:

        minutes = int(
            match.group(1)
        )

        return now + timedelta(
            minutes=minutes
        )

    # =====================================
    # en X horas
    # =====================================

    match = re.search(
        r'en\s+(\d+)\s+horas?',
        text
    )

    if match:

        hours = int(
            match.group(1)
        )

        return now + timedelta(
            hours=hours
        )

    return None