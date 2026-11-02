
import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from queue import Queue, Empty

HOST = "127.0.0.1"
PORT = 5000


class ChatClient:

    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Chat Application")
        self.root.geometry("800x600")
        self.root.minsize(650, 450)
        self.root.configure(bg="#EAF3FA")

        self.client = None
        self.username = ""
        self.connected = False
        self.authenticated = False

        self.send_lock = threading.Lock()
        self.message_queue = Queue()

        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)

        # Create chat interface first
        self.create_gui()

        # Start queue processing
        self.root.after(100, self.process_queue)

        # Start login process
        self.root.after(200, self.show_login_dialog)

    def create_gui(self):

        # Header
        header = tk.Frame(
            self.root,
            bg="#246B9E",
            height=70
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="REAL-TIME CHAT",
            font=("Arial", 20, "bold"),
            bg="#246B9E",
            fg="white"
        ).pack(side="left", padx=20)

        self.status = tk.Label(
            header,
            text="● Not Connected",
            font=("Arial", 11, "bold"),
            bg="#246B9E",
            fg="#FFB4A2"
        )
        self.status.pack(side="right", padx=20)

        # Welcome section
        welcome = tk.Frame(
            self.root,
            bg="#EAF3FA"
        )
        welcome.pack(fill="x", padx=18, pady=10)

        self.welcome_label = tk.Label(
            welcome,
            text="Welcome! Please login to start chatting.",
            font=("Arial", 14, "bold"),
            bg="#EAF3FA",
            fg="#246B9E"
        )
        self.welcome_label.pack(anchor="w")

        # Chat area
        chat_frame = tk.Frame(
            self.root,
            bg="white"
        )
        chat_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=10
        )

        self.chat_area = tk.Text(
            chat_frame,
            font=("Arial", 12),
            bg="white",
            fg="#243B53",
            wrap="word",
            state="disabled",
            padx=12,
            pady=12,
            relief="flat"
        )
        self.chat_area.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            chat_frame,
            command=self.chat_area.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.chat_area.config(
            yscrollcommand=scrollbar.set
        )

        self.chat_area.tag_config(
            "system",
            foreground="#438FCF",
            font=("Arial", 10, "italic")
        )

        self.chat_area.tag_config(
            "message",
            foreground="#243B53",
            font=("Arial", 12)
        )

        self.chat_area.tag_config(
            "own",
            foreground="#16804A",
            font=("Arial", 12, "bold")
        )

        # Message input section
        bottom = tk.Frame(
            self.root,
            bg="#EAF3FA"
        )
        bottom.pack(
            fill="x",
            padx=18,
            pady=(0, 18)
        )

        self.message_input = tk.Entry(
            bottom,
            font=("Arial", 12),
            bg="white",
            fg="#243B53",
            relief="solid",
            bd=1
        )
        self.message_input.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=12,
            padx=(0, 10)
        )

        self.message_input.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        self.send_button = tk.Button(
            bottom,
            text="SEND",
            font=("Arial", 11, "bold"),
            bg="#246B9E",
            fg="white",
            activebackground="#438FCF",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.send_message,
            state="disabled"
        )
        self.send_button.pack(side="right")

        self.display_message(
            "Please login or register to start chatting.",
            "system"
        )

        print("CHAT GUI CREATED SUCCESSFULLY")

    def show_login_dialog(self):

        if not self.root.winfo_exists():
            return

        is_new_user = messagebox.askyesno(
            "Account",
            "Are you a new user?\n\nYES = Register\nNO = Login",
            parent=self.root
        )

        self.auth_type = "register" if is_new_user else "login"

        username = simpledialog.askstring(
            "Username",
            "Enter your username:",
            parent=self.root
        )

        if not username or not username.strip():
            self.disconnect()
            return

        self.username = username.strip()

        self.welcome_label.config(
            text=f"Welcome, {self.username}!"
        )

        password = simpledialog.askstring(
            "Password",
            "Enter your password:",
            show="*",
            parent=self.root
        )

        if not password:
            self.disconnect()
            return

        self.connect_to_server(password)

    def connect_to_server(self, password):

        try:
            print("Connecting to server...")

            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect((HOST, PORT))
            self.connected = True

            print("CONNECTED TO SERVER")

            self.send_data({
                "type": self.auth_type,
                "username": self.username,
                "password": password
            })

            print("AUTH REQUEST SENT")

            threading.Thread(
                target=self.receive_messages,
                daemon=True
            ).start()

        except OSError as error:
            print("CONNECTION ERROR:", error)

            messagebox.showerror(
                "Connection Error",
                f"Cannot connect to server:\n{error}",
                parent=self.root
            )

            self.disconnect()

    def send_data(self, data):

        with self.send_lock:
            self.client.sendall(
                (json.dumps(data) + "\n").encode("utf-8")
            )

    def receive_messages(self):

        buffer = ""

        while self.connected:

            try:
                data = self.client.recv(4096)

                if not data:
                    break

                buffer += data.decode("utf-8")

                while "\n" in buffer:

                    line, buffer = buffer.split("\n", 1)

                    if line.strip():
                        message = json.loads(line)

                        print("SERVER RESPONSE:", message)

                        self.message_queue.put(message)

            except (OSError, json.JSONDecodeError) as error:
                print("RECEIVE ERROR:", error)
                break

        self.message_queue.put({
            "type": "connection_closed"
        })

    def process_queue(self):

        try:
            while True:
                message = self.message_queue.get_nowait()
                self.process_message(message)

        except Empty:
            pass

        try:
            if self.root.winfo_exists():
                self.root.after(100, self.process_queue)
        except tk.TclError:
            pass

    def process_message(self, message):

        message_type = message.get("type")

        if message_type == "auth_result":

            if message.get("success"):

                self.authenticated = True

                self.status.config(
                    text="● Connected",
                    fg="#D8F3DC"
                )

                self.send_button.config(
                    state="normal"
                )

                self.display_message(
                    message.get("text", "Login successful!"),
                    "system"
                )

                self.display_message(
                    "You are now connected to the chat.",
                    "system"
                )

                print("LOGIN SUCCESSFUL")

            else:

                messagebox.showerror(
                    "Authentication Failed",
                    message.get("text", "Login failed."),
                    parent=self.root
                )

                self.disconnect()

        elif message_type == "system":

            if self.authenticated:
                self.display_message(
                    message.get("text", ""),
                    "system"
                )

        elif message_type == "message":

            if self.authenticated:

                username = message.get("username", "Unknown")
                text = message.get("text", "")
                timestamp = message.get("timestamp", "")

                if username == self.username:
                    tag = "own"
                    display_text = f"[{timestamp}] You: {text}"
                else:
                    tag = "message"
                    display_text = f"[{timestamp}] {username}: {text}"

                self.display_message(
                    display_text,
                    tag
                )

        elif message_type == "connection_closed":

            self.connected = False
            self.send_button.config(state="disabled")

            self.status.config(
                text="● Disconnected",
                fg="#FFB4A2"
            )

            if self.authenticated:
                self.display_message(
                    "Connection to server was closed.",
                    "system"
                )

    def send_message(self):

        if not self.authenticated or not self.connected:
            return

        message = self.message_input.get().strip()

        if not message:
            return

        try:
            self.send_data({
                "type": "message",
                "text": message
            })

            self.message_input.delete(0, tk.END)

        except OSError as error:

            print("SEND ERROR:", error)

            self.connected = False

            self.display_message(
                "Connection lost.",
                "system"
            )

    def display_message(self, message, tag):

        self.chat_area.config(state="normal")

        self.chat_area.insert(
            tk.END,
            message + "\n",
            tag
        )

        self.chat_area.see(tk.END)

        self.chat_area.config(state="disabled")

    def disconnect(self):

        self.connected = False

        if self.client:

            try:
                self.client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                self.client.close()
            except OSError:
                pass

        try:
            self.root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":

    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
