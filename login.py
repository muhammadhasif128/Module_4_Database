from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
hashpwd = bcrypt.generate_password_hash('password')
import re

app = Flask(__name__)
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'
# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'JALALASSS'
app.config['MYSQL_DB'] = 'pythonlogin'
# Intialize MySQL
mysql = MySQL(app)
# http://localhost:5000/MyWebApp/ - this will be the login page, we need to use both GET and POST #requests


@app.route('/', methods=['GET', 'POST'])
def login():

    # Output message if something goes wrong...
    msg = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        user_hashpwd = account['password']

        if account and bcrypt.check_password_hash(user_hashpwd, password):

            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return render_template('home.html',msg='',username=username)
        else:
            # Account doesn’t exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg='')


@app.route('/MyWebApp/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        hashpwd = bcrypt.generate_password_hash(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, hashpwd, email,))
        mysql.connection.commit()
        msg = 'You have successfully registered!'

        return render_template('home.html', msg=msg, username=username)

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/MyWebApp/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/MyWebApp/profile')
def profile():
# Check if user is loggedin
    if 'loggedin' in session:
    # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
    # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/MyWebApp/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
