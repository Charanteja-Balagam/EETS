import sys
from ExpenseManager import expense_manager
from eets_routes import app


if __name__ == '__main__':
    """
        Calls the 'create_tables()' function to establish a connection to the SQLite database and create
           the necessary tables if they don't already exist.
        Starts the Flask application using 'app.run(debug=True)'.
        
    """
    expense_manager.create_tables()
    app.run(debug=True)
