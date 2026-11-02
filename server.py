
import socket
import threading
import json
from datetime import datetime

from database import connect_db, create_tables, get_messages
from security import hash_password, verify_password

HOST = "127.0.0.1"
PORT = 5000

clients = {}
clients_lock = threading.Lock()


def send_data(client, data):
    message = json.dumps(data) + "\n"
    client.sendall(message.encode("utf-8"))


def register_user(username, password):
    password_hash, salt = hash_password(password)

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, salt)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, salt)
        )

        connection.commit()
        return True, "Registration successful!"

    except Exception as error:
        print("REGISTRATION ERROR:", error, flush=True)
        return False, "Username already exists."

    finally:
        connection.close()


def login_user(username, password):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT password_hash, salt
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

    finally:
        connection.close()

    if user:
        stored_hash, salt = user

        if verify_password(password, stored_hash, salt):
            return True

    return False


def save_message(username, message):
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM rooms WHERE room_name = ?",
            ("General",)
        )

        room = cursor.fetchone()

        if room:
            cursor.execute(
                """
                INSERT INTO messages (room_id, username, message)
                VALUES (?, ?, ?)
                """,
                (room[0], username, message)
            )

            connection.commit()

    finally:
        connection.close()


# NEW: Send previous messages to a user
def send_chat_history(client):
    try:
        previous_messages = get_messages()

        send_data(client, {
            "type": "system",
            "text": "========== CHAT HISTORY =========="
        })

        for username, message, timestamp in previous_messages:
            send_data(client, {
                "type": "message",
                "username": username,
                "text": message,
                "timestamp": str(timestamp)
            })

        send_data(client, {
            "type": "system",
            "text": "========== END OF CHAT HISTORY =========="
        })

        print("CHAT HISTORY SENT SUCCESSFULLY", flush=True)

    except Exception as error:
        print("CHAT HISTORY ERROR:", repr(error), flush=True)


def broadcast(data, sender=None):
    with clients_lock:
        connected_clients = list(clients.keys())

    for client in connected_clients:
        if client != sender:
            try:
                send_data(client, data)
            except OSError as error:
                print("BROADCAST ERROR:", error, flush=True)
                remove_client(client)


def remove_client(client):
    with clients_lock:
        username = clients.pop(client, None)

    if username:
        print(f"{username} disconnected.", flush=True)

        broadcast({
            "type": "system",
            "text": f"{username} left the chat."
        })


def handle_client(client, address):
    username = None
    buffer = ""
    authenticated = False

    print(f"NEW CONNECTION: {address}", flush=True)

    try:
        while True:
            data = client.recv(4096)

            if not data:
                print("CLIENT CLOSED CONNECTION", flush=True)
                break

            print("DATA RECEIVED FROM CLIENT", flush=True)

            buffer += data.decode("utf-8")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if not line.strip():
                    continue

                message = json.loads(line)

                print("CLIENT REQUEST:", message, flush=True)

                if not authenticated:

                    action = message.get("type")
                    username = message.get("username", "").strip()
                    password = message.get("password", "")

                    if not username or not password:
                        send_data(client, {
                            "type": "auth_result",
                            "success": False,
                            "text": "Username and password required."
                        })
                        continue

                    if action == "register":
                        success, response_text = register_user(
                            username, password
                        )

                    elif action == "login":
                        success = login_user(username, password)

                        response_text = (
                            "Login successful!"
                            if success
                            else "Invalid username or password."
                        )

                    else:
                        success = False
                        response_text = "Please register or login first."

                    send_data(client, {
                        "type": "auth_result",
                        "success": success,
                        "text": response_text
                    })

                    print(
                        f"AUTHENTICATION RESULT: {success}",
                        flush=True
                    )

                    if success:
                        authenticated = True

                        with clients_lock:
                            clients[client] = username

                        print(
                            f"{username} LOGGED IN SUCCESSFULLY",
                            flush=True
                        )

                        # Send previous chat messages
                        send_chat_history(client)

                        broadcast({
                            "type": "system",
                            "text": f"{username} joined the chat."
                        })

                    continue

                if message.get("type") == "message":

                    text = message.get("text", "").strip()

                    if not text:
                        continue

                    timestamp = datetime.now().strftime("%H:%M")

                    save_message(username, text)

                    chat_message = {
                        "type": "message",
                        "username": username,
                        "text": text,
                        "timestamp": timestamp
                    }

                    print(
                        f"[{timestamp}] {username}: {text}",
                        flush=True
                    )

                    broadcast(chat_message, sender=client)
                    send_data(client, chat_message)

    except json.JSONDecodeError as error:
        print("JSON ERROR:", error, flush=True)

    except (ConnectionError, OSError) as error:
        print("CONNECTION ERROR:", error, flush=True)

    except Exception as error:
        print("SERVER ERROR:", repr(error), flush=True)

    finally:
        remove_client(client)

        try:
            client.close()
        except OSError:
            pass


def start_server():
    create_tables()

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen()

    print("=" * 45)
    print("       REAL-TIME CHAT SERVER")
    print("=" * 45)
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for users to connect...", flush=True)

    try:
        while True:
            client, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(client, address),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        print("\nServer is shutting down...")

    finally:
        server.close()
        print("Server stopped.")


if __name__ == "__main__":
    start_server()
