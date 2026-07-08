"""
scheduler.py

Revisa recordatorios pendientes y los ejecuta cuando llega su hora.

Uso:
    python modules/scheduler.py

Ejecutar en terminal separada mientras bot.py está activo.
En el futuro enviará notificaciones por Telegram.
"""

import sqlite3
import time
import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, TIMEZONE, SCHEDULER_INTERVAL, DEBUG


def get_pending_reminders():
    """Devuelve recordatorios pendientes cuya hora ya llegó."""

    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, message, remind_at
        FROM reminders
        WHERE executed = 0
        AND remind_at <= ?
        """,
        (now,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def mark_executed(reminder_id):
    """Marca un recordatorio como ejecutado."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE reminders
        SET executed = 1
        WHERE id = ?
        """,
        (reminder_id,)
    )

    conn.commit()
    conn.close()


def run():

    print("[SCHEDULER] Iniciado.")
    print(f"[SCHEDULER] Zona horaria: {TIMEZONE}")
    print(f"[SCHEDULER] Revisando cada {SCHEDULER_INTERVAL} segundos.")
    print()

    while True:

        try:

            reminders = get_pending_reminders()

            if DEBUG and len(reminders) == 0:
                print(f"[SCHEDULER] Sin recordatorios pendientes.")

            for reminder_id, message, remind_at in reminders:

                print()
                print("=" * 40)
                print("[FREDO] ¡Recordatorio!")
                print(f"  {message}")
                if DEBUG:
                    print(f"  (Programado: {remind_at})")
                print("=" * 40)
                print()

                mark_executed(reminder_id)

        except Exception as e:

            print(f"[SCHEDULER] Error: {e}")

        time.sleep(SCHEDULER_INTERVAL)


if __name__ == "__main__":
    run()
