import sqlite3
import time

class User:
    def __init__(self, id, username, balance):
        self.id = id
        self.username = username
        self.balance = balance

    @staticmethod
    def get_user_by_id(user_id):
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user_data = c.fetchone()
        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def add_user(username, balance):
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (username, balance) VALUES (?, ?)', (username, balance))
            conn.commit()
            return c.lastrowid  # Return the ID of the newly created user

    @staticmethod
    def delete_user(user_id):
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return c.rowcount  # Return the number of rows affected

    def update_balance(self, amount):
        max_retries = 5  # Maximum number of retries
        retry_wait = 0.5  # Wait time between retries in seconds
        for attempt in range(max_retries):
            try:
                if self.balance + amount >= 0:
                    with sqlite3.connect('users.db', timeout=10) as conn:  # Increased timeout
                        c = conn.cursor()
                        c.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, self.id))
                        c.execute('SELECT balance FROM users WHERE id = ?', (self.id,))
                        self.balance = c.fetchone()[0]
                        conn.commit()
                    return True
                return False  # If the balance would go negative, don't retry
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_wait)  # Wait before retrying
                else:
                    raise  # Reraise the last exception if all retries fail or if it's not a locking issue

