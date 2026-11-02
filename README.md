# Real-Time Chat Application

## Project Overview

A Python-based Real-Time Chat Application that allows multiple users to communicate instantly over a network.

## Features

- User Registration and Login
- Secure Password Hashing
- Real-Time Messaging
- Multiple User Support
- Chat History
- SQLite Database Integration
- Tkinter Graphical User Interface
- Client-Server Communication using Python Sockets

## Technologies Used

- Python
- Tkinter
- Socket Programming
- SQLite3
- JSON
- Threading
- Hashlib

## Project Structure

```text
Chat_Application/
├── server.py
├── client.py
├── main.py
├── database.py
├── security.py
├── test_gui.py
├── screenshots/
│   ├── login.png
│   └── chat.png
├── README.md
└── .gitignore
```

## How to Run

### 1. Start the Server

```bash
python server.py
```

### 2. Start the Client

Open another terminal and run:

```bash
python client.py
```

### 3. Register or Login

Create a new account or log in using an existing account.

## Database

The application uses SQLite to store user information and chat messages.

## Security

Passwords are protected using PBKDF2-HMAC-SHA256 hashing.

## Screenshots

### Login Screen

![Login Screen](screenshots/login.png)

### Chat Window

![Chat Window](screenshots/chat.png)

## Project Purpose

This project demonstrates Python GUI development, socket programming, database management, and real-time client-server communication.

## Author

**Punit Patil**
