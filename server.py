from flask import Flask, render_template, request, redirect, session, flash   # Import Flask to allow us to create our app
from flask_bcrypt import Bcrypt
import re
# from mysqlconnection import connectToMySQL
from flask_mysqldb import MySQL

app = Flask(__name__)    # Create a new instance of the Flask class called "app"
app.secret_key = 'patagoniahealthcurry'
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z ]*$')
PSWD_REGEX = re.compile(r'^(?=.{6,}$)(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootR@jit697nb'
app.config['MYSQL_DB'] = 'pat_phy'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')          # The "@" decorator associates this route with the function immediately following
def landing_page():
    return render_template('index.html')  # Return the string 'Hello World!' as a response

@app.route('/patient/register', methods = ['GET', 'POST'])
def patient_process():
    msg = ""
    form = request.form
    if request.method == 'POST' and 'first_name' in form and 'last_name' in form and 'email' in form:
        first_name = form['first_name']
        last_name = form['last_name']
        email = form['email']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM patients WHERE email = %s', [email])
        account = cursor.fetchone()
        if account:
            msg = "Account already exists!"
        elif not NAME_REGEX.match(request.form['first_name']):
            msg = "Invalid first name!"
        elif not NAME_REGEX.match(request.form['last_name']):
            msg = "Invalid last name!"
        elif not EMAIL_REGEX.match(request.form['email']):
            msg = "Invalid email address!"
        else:
            cursor.execute("INSERT INTO patients(first_name, last_name, email) VALUES (%s, %s, %s)", [first_name, last_name, email])
            mysql.connection.commit()
            msg = "You have successfully registered!"

    elif request.method == 'POST':
        msg = "Please fill out the form!"
    return render_template('patient_reg.html', msg = msg)


@app.route('/physicians')
def physicians_login():
    return render_template('physician_login.html')


@app.route('/physician/register', methods = ['GET', 'POST'])
def physician_register():
    msg = ""
    form = request.form
    if request.method == 'POST' and 'first_name' in form and 'last_name' in form and 'email' in form:
        first_name = form['first_name']
        last_name = form['last_name']
        email = form['email']
        pw_hash = bcrypt.generate_password_hash(request.form['pswd'])
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM physicians WHERE email = %s', [email])
        account = cursor.fetchone()
        if account:
            msg = "Account already exists!"
        elif not NAME_REGEX.match(request.form['first_name']):
            msg = "Invalid first name!"
        elif not NAME_REGEX.match(request.form['last_name']):
            msg = "Invalid last name!"
        elif not EMAIL_REGEX.match(request.form['email']):
            msg = "Invalid email address!"
        elif not PSWD_REGEX.match(request.form['pswd']):
            msg = "Missing Password Requirement"
        else:
            cursor.execute("INSERT INTO physicians(first_name, last_name, email, pswd_hash) VALUES (%s, %s, %s, %s)", [first_name, last_name, email, pw_hash])
            mysql.connection.commit()
            msg = "You have successfully registered!"

    elif request.method == 'POST':
        msg = "Please fill out the form!"
    return render_template('physician_reg.html', msg = msg)

@app.route('/physician/login', methods = ['GET', 'POST'])
def login():
    msg = ""
    form = request.form
    if request.method == 'POST' and 'email' in form and 'pswd' in form:
        email = form['email']
        password = form['pswd']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM physicians WHERE email = %s', [email])
        account = cursor.fetchone()
        if account:
            if bcrypt.check_password_hash(account['pswd_hash'], password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['email'] = account['email']
                return redirect('/physician/profile')
        else:
            msg = "Incorrect Email/Password!"
    return render_template('physician_login.html', msg = msg)

@app.route('/physician/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM physicians WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM patients WHERE physician_id = %s', [session['id']])
        patients = cursor.fetchall()
        return render_template('profile.html', account = account, patients = patients)
    return redirect('/physician/login')

@app.route('/physician/add_patients')
def add_patients():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM physicians WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM patients WHERE is_taken = 0')
        patients = cursor.fetchall()
        return render_template('add_patients.html', account = account, patients = patients)

    return redirect('/physician/login')

@app.route('/add/<string:email>')
def add_patient(email):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE patients SET is_taken = 1, physician_id = %s WHERE email = %s', [session['id'], email])
        mysql.connection.commit()
        return redirect('/physician/add_patients')


@app.route('/physician/logout')
def logout():
    if 'loggedin' in session:
        session.pop('id')
        session.pop('email')
        session.clear()
        msg = "You have been logged out successfuly"
        return render_template('physician_login.html', msg = msg)






if __name__=="__main__":   # Ensure this file is being run directly and not from a different module
    app.run(debug=True)    # Run the app in debug mode.