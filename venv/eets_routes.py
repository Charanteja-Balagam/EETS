from flask import Flask, render_template, request, redirect, url_for, session
from ExpenseManager import expense_manager
from datetime import datetime
import uuid
import io
import base64
import matplotlib
matplotlib.use('agg')

app = Flask(__name__)
app.secret_key = 'EETS_secret_key'

# Route for the login page
@app.route('/', methods=['GET', 'POST'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Route for the login page.If the request method is POST, attempts to authenticate the user based on the provided
        employee ID and password. If the credentials are valid, the user is redirected to the dashboard page.
        If the credentials are invalid, an error message is shown on the login page.If the request method is GET, the login page is rendered.

    """
    if request.method == 'POST':
        try:
            employee_id = request.form['employee_id']
            password = request.form['password']

            # Retrieve users from SQLite database
            users = expense_manager.read_users()

            # Check if login credentials are valid
            for user in users:
                if user['employee_id'] == employee_id and user['password'] == password:
                    # Set session data for logged in user
                    session['employee_id'] = employee_id

                    # Successful login, redirect to dashboard
                    return redirect(url_for('dashboard'))

            # Invalid login
            raise ValueError('Invalid employee ID or password')

        except ValueError as ve:
            # Handle the exception gracefully with a user-friendly error message
            return render_template('login.html', error='Invalid employee ID or password. Please try again.')

        except Exception as e:
            # Handle any other unexpected exceptions with a generic error message
            return render_template('login.html', error='An unexpected error occurred. Please try again later.')

    else:
        return render_template('login.html')



# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for the registration page.If the request method is POST, attempts to register a new user based on the provided
    employee ID and password. Checks if the employee ID is numeric, and if it is, adds the new user
    to the users database and redirects to the login page. If the employee ID already exists, an error
    message is shown on the registration page.If the request method is GET, the registration page is rendered.

    """

    if request.method == 'POST':
        try:
            employee_id = request.form['employee_id']
            password = request.form['password']

            # Checks if employee_id is 5 digit numeric
            if not employee_id.isdigit() or len(employee_id) != 5:
                raise ValueError('Employee ID must be a 5-digit numeric value')
            #checks if password is valid
            # Check if password is a valid one
            expense_manager.is_valid_password(password)
            # Check if employee_id already exists
            if expense_manager.is_employee_id_exists(employee_id):
                return render_template('register.html', error='Employee ID already exists')
            else:
                # Add new user to users and write to SQLite database
                expense_manager.write_users([(employee_id, password)])

                # Redirect to login page
                return redirect(url_for('login'))

        except ValueError as ve:
            # Catch ValueError if employee_id is not numeric
            return render_template('register.html', error=str(ve))

        except Exception as e:
            # Catch any other unexpected exceptions
            print(e)
            return render_template('error.html', error='An unexpected error occurred. Please try again later.')

    else:
        return render_template('register.html')



# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    """
        Route for the dashboard page.Checks if the user is logged in by verifying the presence of 'employee_id' in the session data.
        If the user is logged in, retrieves the employee_id from the session data and the current hour of the day.
        Based on the current hour, generates a personalized greeting (Good Morning, Good Afternoon, or Good Evening).
        Renders the dashboard template with the employee_id and greeting. If the user is not logged in, redirects to the login page.


        """
    try:
        # Check if user is logged in
        if 'employee_id' in session:
            employee_id = session['employee_id']
            # Get the current hour of the day
            current_hour = datetime.now().hour

            # Check the current hour and generate personalized greeting
            if 5 <= current_hour < 12:
                greeting = "Good Morning"
            elif 12 <= current_hour < 18:
                greeting = "Good Afternoon"
            else:
                greeting = "Good Evening"

            return render_template('dashboard.html', employee_id=employee_id, greeting=greeting)
        else:
            # User is not logged in, redirect to login page
            return redirect(url_for('login'))

    except Exception as e:
        # Catch any other unexpected exceptions
        return render_template('error.html', error='An unexpected error occurred. Please try again later.')



# Route for the logout action
@app.route('/logout')
def logout():
    """
       Route for the logout action.Clears the session data to log the user out and redirects them to the login page.
       """
    try:
        # Clear the session data
        session.clear()
        return redirect(url_for('login'))
    except Exception as e:
        # Catch any unexpected exceptions
        return render_template('error.html', error='An unexpected error occurred. Please try again later.')



@app.route('/add_expenses', methods=['GET', 'POST'])
def add_expenses():
    """
       Route for adding new expenses.This route allows users to add new expenses by submitting a form with category, amount, and date fields.
       The function checks if the user is logged in and redirects them to the login page if not.
       If the request method is POST, it processes the submitted form data, validates the input,
       and adds the new expense to the SQLite database.it displays an error message to the user and renders the 'add_expenses.html' template.
       If the expense is successfully added, the user is redirected to the 'view_expenses' page.

       """
    try:
        # Check if user is logged in
        if 'employee_id' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            category = request.form['category']
            amount = request.form['amount']
            date = request.form['date']



            if not category or not all(word.isalpha() for word in category.split()):
                return render_template('add_expenses.html', error='Invalid category. Category must contain only text.')

            # Retrieve expenses from SQLite database
            expenses = expense_manager.read_expenses()

            # Generate a UUID for each expense
            expense_id = str(uuid.uuid4())

            # Add new expense for the current user
            employee_id = session['employee_id']
            new_expense = {'expense_id': expense_id, 'employee_id': employee_id, 'category': category, 'amount': amount, 'date': date}

            # Ensure 'amount' is not empty
            if not amount:
                return render_template('add_expenses.html', error='Invalid amount')

            # Convert 'amount' to a numerical data type, e.g., float
            new_expense['amount'] = float(amount)

            # Write expense to SQLite database
            expense_manager.write_expense(new_expense)

            # Redirect to view expenses page
            return redirect(url_for('view_expenses'))
        else:
            return render_template('add_expenses.html')
    except Exception as e:
        # Catch any unexpected exceptions
        return render_template('error.html', error='An unexpected error occurred. Please try again later.')



# Route for viewing expenses
@app.route('/view_expenses')
def view_expenses():
    """
       Route for viewing expenses.This route allows logged-in users to view their expenses. It retrieves the user's ID from the session data.
       Then, it retrieves all expenses from the SQLite database and filters them to get the expenses for the current user.
       The expenses are passed to the 'view_expenses.html' template to be displayed to the user.
       If the user is not logged in, it redirects them to the login page.

       """
    try:
        # Check if user is logged in
        if 'employee_id' in session:
            employee_id = session['employee_id']

            # Retrieve expenses from SQLite database
            expenses = expense_manager.read_expenses()

            # Filter expenses for the current user
            user_expenses = [expense for expense in expenses if expense['employee_id'] == employee_id]

            return render_template('view_expenses.html', expenses=user_expenses)
        else:
            # User is not logged in, redirect to login page
            return redirect(url_for('login'))
    except Exception as e:
        # Catch any unexpected exceptions
        return render_template('error.html', error='An unexpected error occurred while loading expenses. Please try again later.')



@app.route('/edit_expense/<expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    """
    Route for editing an expense.This route allows users to edit an existing expense. If the request method is POST,
    it retrieves the updated expense details from the form data and updates the expense in the SQLite database.
    If the expense is successfully updated, it redirects to the 'view_expenses' page to view all expenses.
    If the expense does not exist, it also redirects to the 'view_expenses' page.
    If the request method is GET, it retrieves the expense details from the SQLite database and renders
    the 'edit_expense.html' template to allow the user to edit the expense details.
    If the expense does not exist, it redirects to the 'view_expenses' page.
    If an unexpected exception occurs while editing or retrieving the expense,
    it displays an error message and renders the 'error.html' template.


    """
    try:
        if request.method == 'POST':
            category = request.form['category']
            amount = request.form['amount']
            date = request.form['date']

            # Retrieve the expense from the database
            expense = expense_manager.read_expense_by_id(expense_id)

            if expense:
                expense_dict = dict(expense)  # Convert sqlite3.Row to a dictionary
                expense_dict['category'] = category
                expense_dict['amount'] = float(amount)
                expense_dict['date'] = date
                is_expense_exist = True

                # Write the updated expense back to the database
                expense_manager.write_expense(expense_dict, is_expense_exist)

                # Redirect to view expenses page
                return redirect(url_for('view_expenses'))
            else:
                return redirect(url_for('view_expenses'))

        else:
            # Retrieve the expense to be edited
            expense = expense_manager.read_expense_by_id(expense_id)

            if expense:
                return render_template('edit_expense.html', expense=expense)
            else:
                return redirect(url_for('view_expenses'))

    except Exception as e:
        print(e)
        # Catch any unexpected exceptions
        return render_template('error.html', error='An unexpected error occurred. Please try again later.')



@app.route('/delete_expense/<expense_id>')
def delete_expense(expense_id):
    """
    Route for deleting an expense.This route allows users to delete an existing expense. It retrieves the expense from the SQLite database
    based on the provided 'expense_id'. If the expense exists, it deletes the expense entry from the database.
    If the deletion is successful, it redirects to the 'view_expenses' page to view the updated list of expenses.
    If the expense does not exist, it also redirects to the 'view_expenses' page.
    If an unexpected exception occurs while deleting the expense,
    it displays an error message and renders the 'error.html' template.


    """
    try:
        # Retrieve the expense from the database
        expense = expense_manager.read_expense_by_id(expense_id)

        if expense:
            # Delete the expense from the database
            expense_manager.delete_expense(expense_id)

        # Redirect to view expenses page
        return redirect(url_for('view_expenses'))

    except Exception as e:
        # Catch any unexpected exceptions
        return render_template('error.html', error='An unexpected error occurred. Please try again later.')

import matplotlib.pyplot as plt
# Route for visualizing expenses
@app.route('/visualization')
def visualize_expenses():
    """
       Route for visualizing expenses.This route allows users to visualize their expenses in two different charts: expenses by category and expenses by date.
       It first checks if the user is logged in by verifying the presence of 'employee_id' in the session.
       If the user is not logged in, it redirects to the 'login' page.
       Otherwise, it retrieves the user's expenses from the SQLite database and calculates the total amount for each category and date.
       It then creates two bar charts using matplotlib to visualize the expenses by category and date.
       If there are no expenses for the user, it renders the 'visualization.html' template with None values for the plots.
       After generating the plots, it saves them to a buffer, converts them to base64-encoded strings,
       and passes them to the 'visualization.html' template for rendering.
       If an unexpected exception occurs during the process, it displays an error message
       and renders the 'error.html' template.


       """
    try:
        # Check if user is logged in
        if 'employee_id' in session:
            employee_id = session['employee_id']
        else:
            return redirect(url_for('login'))
        expenses = expense_manager.read_expenses()

        # Check if expenses data is empty
        if not expenses:
            return render_template('visualization.html', plot_category=None, plot_date=None)

        # Create a dictionary to hold the total amount for each category and date
        category_totals = {}
        date_totals = {}

        # Filter expenses for the current user
        user_expenses = [expense for expense in expenses if expense['employee_id'] == employee_id]
        # Calculate the total amount for each category and date
        for expense in user_expenses:
            category = expense['category']
            date = expense['date']
            amount = float(expense['amount'])  # Convert amount to float for aggregation

            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

            if date in date_totals:
                date_totals[date] += amount
            else:
                date_totals[date] = amount

        # Convert the category_totals and date_totals dictionaries to lists for plotting
        categories = list(category_totals.keys())
        total_amounts_category = list(category_totals.values())

        dates = list(date_totals.keys())
        total_amounts_date = list(date_totals.values())

        # Create the desired visualizations using matplotlib
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Visualization 1: Expenses by Category
        ax1.bar(categories, total_amounts_category)
        ax1.set_xlabel('Category')
        ax1.set_ylabel('Total Amount')
        ax1.set_title('Expense Visualization by Category')

        # Visualization 2: Expenses by Date
        ax2.bar(dates, total_amounts_date)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Total Amount')
        ax2.set_title('Expense Visualization by Date')

        # Save the plots to a buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()

        # Convert the plots to base64-encoded strings
        buffer.seek(0)
        plot_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        # Render the visualization template and pass the plots as variables
        return render_template('visualization.html', plot=plot_base64)

    except Exception as e:
        # Catch any unexpected exceptions
        return render_template('error.html', error='An unexpected error occurred. Please try again later.')
