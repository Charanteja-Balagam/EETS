import sqlite3
import re

class ExpenseManager:
    def __init__(self, db_file):
        """
        Initializes the ExpenseManager instance.

        """
        self.db_file = db_file

    def get_db_connection(self):
        """
        Establishes a connection to the SQLite database.

        """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """
        Creates the given tables in the SQLite database if they do not exist.
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id TEXT NOT NULL,
                    employee_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            ''')

            conn.commit()

    def read_users(self):
        """
        Retrieves users from the SQLite database.

        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
        return users

    def is_employee_id_exists(self, employee_id):
        """
                checks if the employee id exists in the database.

        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE employee_id = ?', (employee_id,))
            user = cursor.fetchone()
        return user is not None

    def write_users(self, users):
        """
        Writes a list of users to the SQLite database.

        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany('INSERT INTO users (employee_id, password) VALUES (?, ?)', users)
            conn.commit()

    def read_expenses(self):
        """
        Retrieves expenses from the SQLite database with query.

        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses')
            expenses = cursor.fetchall()
        return expenses

    def write_expense(self, expense, exist = False):
        """
        Writes an expense to the SQLite database. And also updates the expense.

        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            if exist == False:
                cursor.execute(
                    'INSERT INTO expenses (expense_id, employee_id, category, amount, date) VALUES (?, ?, ?, ?, ?)',
                    (expense['expense_id'], expense['employee_id'], expense['category'], expense['amount'], expense['date'])
                )
            else:
                cursor.execute("UPDATE expenses set category = '{3}', \
                                                amount = '{1}', \
                                                date = '{2}'  \
                                                where expense_id = '{0}' \
                                                and employee_id = '{4}';".format(expense['expense_id'],
                                                                                 expense['amount'], expense['date'],
                                                                                 expense['category'],
                                                                                 expense['employee_id']))

            conn.commit()

    def read_expense_by_id(self, expense_id):
        """
        Retrieves an expense from the database based on the provided expense_id.

        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses WHERE expense_id = ?', (expense_id,))
            expense = cursor.fetchone()
        return dict(expense) if expense else None

    def delete_expense(self, expense_id):
        """
            Deletes an expense from the expenses table in the SQLite database.
            This method allows users to delete an existing expense based on the provided 'expense_id'.


            """
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE expense_id = ?', (expense_id,))
            conn.commit()

    def is_valid_password(sef,password):
        """
           Validates the password according to the specified criteria.
           Raises:ValueError: If the password does not meet the specified criteria.

           """

        if len(password) <= 8:
            raise ValueError('Password must be atleast 8 characters long.')


        if not any(char.isalpha() for char in password):
            raise ValueError('Password must contain at least one alphabet.')


        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one numeric character.')


        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')



expense_manager = ExpenseManager('eets.db')