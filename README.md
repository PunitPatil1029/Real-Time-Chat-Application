# Real-Time Chat Application

## Project Overview
A Python-based Real-Time Chat Application that allows multiple users to communicate with each other instantly over a network.

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
│
├── server.py
├── client.py
├── database.py
├── security.py
├── README.md
├── .gitignore
└── chat.db
```

## How to Run

### 1. Install Python
Install Python 3 on your computer.

### 2. Run the Server
```bash
python server.py
```

### 3. Run the Client
Open another terminal and run:
```bash
python client.py
```

### 4. Login or Register
Create a new account or log in using an existing account.

## Database
The application uses SQLite to store user information and chat messages.

## Security
Passwords are protected using PBKDF2-HMAC-SHA256 hashing.

## Project Purpose
This project demonstrates Python GUI development, socket programming, database management, and real-time client-server communication.

## Author
Punit Patil
