import sqlite3

def init_db():
    connection = sqlite3.connect("reminders.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            is_sent INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    connection.close()

reminders = []

def add_reminder(reminder):
    connection = sqlite3.connect("reminders.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO reminders (chat_id, text, date, time)
        VALUES (?, ?, ?, ?)
    """, (
        reminder["chat_id"],
        reminder["text"],
        reminder["date"],
        reminder["time"]
    ))
    connection.commit()
    connection.close()

def get_reminders(chat_id):
    connection = sqlite3.connect("reminders.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM reminders WHERE chat_id = ?", (chat_id))

    rows = cursor.fetchall()
    connection.close()

    reminders = []
    for row in rows:
        reminders.append({
            "id": row[0],
            "chat_id": row[1],
            "text": row[2],
            "date": row[3],
            "time": row[4],
            "is_sent": row[5]
        })
    return reminders

def delete_reminders(reminder_id: int):
    connection = sqlite3.connect("reminders.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?",
                   (reminder_id,))
    
    if cursor.rowcount == 0:
        print("Нічого не видалено (ID не знайдено)")
    connection.commit()
    connection.close()

def update_reminder(reminder_id: int, new_text:str):
    connection = sqlite3.connect("reminders.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE reminders
        SET text = ?
        WHERE id = ?
        """, 
    (new_text, reminder_id))

    connection.commit()
    connection.close()

def get_all_reminders():
    connection = sqlite3.connect("reminders.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM reminders")

    rows = cursor.fetchall()
    connection.close()

    reminders = []

    for row in rows:
        reminders.append({
            "id": row[0],
            "chat_id": row[1],
            "text": row[2],
            "date": row[3],
            "time": row[4],
            "is_sent": row[5]
        })
    return reminders

def mark_as_sent(reminder_id: int):
    connection = sqlite3.connect("reminders.db")
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE reminders SET is_sent = 1 WHERE id = ?",
        (reminder_id,)
    )

    connection.commit()
    connection.close()