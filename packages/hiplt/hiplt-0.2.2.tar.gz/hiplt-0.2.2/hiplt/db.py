# hiplt/db.py

import sqlite3
from typing import Optional, List, Any


class Database:
    """
    Обёртка над SQLite3 с базовыми методами.
    """

    def __init__(self, db_path: str = "cso.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, query: str, params: tuple = ()) -> None:
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    db = Database()

    db.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, email TEXT)"
    )
    db.execute("INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)", ("nikita", "nikita@example.com"))

    user = db.fetchone("SELECT * FROM users WHERE username=?", ("nikita",))
    print(dict(user) if user else "User not found")

    db.close()