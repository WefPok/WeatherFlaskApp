import sqlite3
import time

class User:
    def __init__(self, id, username, balance):
        """
        Initialize a new User instance.

        :param id: The unique identifier for the user.
        :param username: The username of the user.
        :param balance: The current balance of the user's account.
        """
        self.id = id
        self.username = username
        self.balance = balance

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a user from the database by their user ID.

        :param user_id: The ID of the user to retrieve.
        :return: A User instance if found, None otherwise.
        """
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user_data = c.fetchone()
        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def add_user(username, balance):
        """
        Add a new user to the database.

        :param username: The username of the new user.
        :param balance: The starting balance of the new user.
        :return: The ID of the newly created user.
        """
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (username, balance) VALUES (?, ?)', (username, balance))
            conn.commit()
            return c.lastrowid  # Return the ID of the newly created user

    @staticmethod
    def delete_user(user_id):
        """
        Delete a user from the database by their user ID.

        :param user_id: The ID of the user to delete.
        :return: The number of rows affected (should be 1 if a user was deleted).
        """

        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return c.rowcount  # Return the number of rows affected

    def update_balance(self, amount):
        """
        Update the balance of the user. If the update fails due to a database lock, it will retry the update a
        maximum number of times before raising an exception.

        :param amount: The amount to add to the user's balance. Can be negative.
        :return: True if the update was successful, False if the update would result in a negative balance.
        :raises: sqlite3.OperationalError if all retries fail due to a database lock.
        """

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

