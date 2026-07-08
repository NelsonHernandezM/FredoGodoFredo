import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH


def save_reminder(message, remind_at):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reminders(
            user_id,
            message,
            remind_at,
            executed
        )
        VALUES(1, ?, ?, 0)
        """,
        (message, str(remind_at))
    )

    conn.commit()
    conn.close()
