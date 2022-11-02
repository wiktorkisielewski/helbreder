import re
from datetime import datetime
import random
import flask_login
from flask import request, flash, redirect, url_for, render_template
from templates.psql import *
from hashlib import sha256

class User(flask_login.UserMixin):
    def __init__(self, name):
        self.name = name

def get_lang_sql():
    cur.execute('''SELECT name FROM LANGUAGES''')
    lang = cur.fetchall()
    languages = []
    for i in range (len(lang)):
        languages.append(''.join(lang[i]))
    return languages

def create_table(table_name, columns):
    columns = re.sub(r"'|:|{|}", "", str(columns))
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name}({columns})")
    c.commit()

def get_emails():
    cur.execute('''SELECT email FROM ACCOUNTS''')
    return cur.fetchall()

def get_name(email):
    cur.execute(f"SELECT username FROM ACCOUNTS WHERE email = '{email}'")
    name = cur.fetchall()
    return name[0][0]

def email_check(email):
    cur.execute('''SELECT email FROM ACCOUNTS''')
    emails_sql = get_emails()
    emails = []
    for i in range (len(emails_sql)):
        emails.append(''.join(emails_sql[i]))
    if email in emails:
        return True
    return False

def username_check(username):
    cur.execute('''SELECT username FROM ACCOUNTS''')
    username_sql = cur.fetchall()
    usernames = []
    for i in range (len(username_sql)):
        usernames.append(''.join(username_sql[i]))
    if username in usernames:
        return True
    return False

def hash_password(password):
    h = sha256()
    h.update(password.encode())
    return h.hexdigest()

def add_account(email, username, password):
    user_id = random.randint(0,1000000)
    time = datetime.now()
    password_hash = hash_password(password)
    cur.execute(f"INSERT INTO ACCOUNTS (user_id, username, password, email, created_on, last_login) VALUES ({user_id}, '{username}', '{password_hash}', '{email}', '{time.isoformat()}', '{time.isoformat()}');")
    c.commit()

def check_pass(email, password_hash):
    cur.execute(f"SELECT password FROM ACCOUNTS WHERE email = '{email}'")
    password = cur.fetchall()
    if password[0][0] == password_hash:
        return True
    return False

def sign_up():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    if email_check(email):
        flash('You already have an account!')
    elif username_check(username):
        flash('Username already exists!')
    else:
        try:
            add_account(email, username, password)
            flash('Succesfully created an account!')
        except:
            flash('Something went wrong!')

def log_in():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    if not email_check(email):
        flash('Please sign up first!')
        return render_template('html/login.html')
    else:
        password_hash = hash_password(password)
        if check_pass(email, password_hash):
            user = User(get_name(email))
            user.id = email
            flask_login.login_user(user, remember=remember)
            return redirect(url_for('static_main'))
        else:
            flash('Wrong password!')
            return render_template('html/login.html')