import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            context TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


class User:
    @staticmethod
    def create(email: str, name: str, occupation: str, interests: str, 
               hobbies: str, personality: str) -> bool:
        """Create a new user."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            context = json.dumps({
                'occupation': occupation,
                'interests': interests,
                'hobbies': hobbies,
                'personality': personality
            })

            cursor.execute('''
                INSERT INTO users (email, name, context, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (email, name, context, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # User already exists
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    @staticmethod
    def get(email: str) -> Optional[Dict]:
        """Get user by email."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'email': row[0],
                'name': row[1],
                'context': json.loads(row[2]),
                'timestamp': row[3]
            }
        return None

    @staticmethod
    def get_all_emails() -> List[str]:
        """Get all registered user emails."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT email FROM users')
        emails = [row[0] for row in cursor.fetchall()]
        conn.close()
        return emails

    @staticmethod
    def exists(email: str) -> bool:
        """Check if user exists."""
        return User.get(email) is not None


class Message:
    @staticmethod
    def create(user_email: str, role: str, content: str) -> bool:
        """Create a new message."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO messages (user_email, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_email, role, content, datetime.now()))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating message: {e}")
            return False

    @staticmethod
    def get_history(user_email: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a user."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT role, content, timestamp 
            FROM messages 
            WHERE user_email = ?
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (user_email, limit))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'role': row[0],
                'content': row[1],
                'timestamp': row[2]
            })

        conn.close()
        return messages

    @staticmethod
    def get_recent_for_context(user_email: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for AI context."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT role, content
            FROM messages 
            WHERE user_email = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_email, limit))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'role': 'assistant' if row[0] == 'bot' else 'user',
                'content': row[1]
            })

        conn.close()
        return list(reversed(messages))  # Return in chronological order

