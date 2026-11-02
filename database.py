
import sqlite3

DATABASE_NAME = "chat.db"


def connect_db():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    connection = connect_db()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    # Chat rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT UNIQUE NOT NULL
        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    """)

    connection.commit()
    connection.close()


def add_room(room_name):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO rooms (room_name) VALUES (?)",
            (room_name,)
        )
        connection.commit()

    except sqlite3.IntegrityError:
        pass

    finally:
        connection.close()


# NEW: Get previous chat messages
def get_messages():
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT username, message, timestamp
            FROM messages
            ORDER BY id ASC
        """)

        messages = cursor.fetchall()
        return messages

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()
    add_room("General")

    print("Database created successfully!")
    print("Users, rooms and messages tables are ready.")
