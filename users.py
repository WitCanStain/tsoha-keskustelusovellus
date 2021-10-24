from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session, flash
import traceback
from string import ascii_lowercase
allowed_chars = ascii_lowercase + 'åäö0123456789'

def login(username, password):
    print(f"Entered users:login({username}, {password}).")
    try:

        hash_value = generate_password_hash(password)
        sql = "SELECT id, password FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        if user:
            db_password = user[1]
            user_id = user[0]
            if db_password and check_password_hash(hash_value, password):
                return user_id
        else:
            flash("Username or password is incorrect.")
            return False
    except:
        traceback.print_exc()
        flash("Login failed.") 

def user_register(role, username, password):
    print(f"Entered users:user_register({role}, {username}, {password}).")
    try:
        hash_value = generate_password_hash(password)
        if check_registration_validity(role, username, password):
            sql = "INSERT INTO users (role, username, password, visible) VALUES (:role, :username, :password, :visible) RETURNING id"
            result = db.session.execute(sql, {"role":role if role else "user", "username":username, "password":hash_value, "visible":True})
            user_id = result.fetchone()[0]
            print(f"user_id: {user_id}")
            db.session.commit()
            session["username"] = username
            session["user_id"] = user_id
            session["role"] = role
            return user_id
        else:
            print("User registration could not be validified.")
            flash("User registration could not be validified.")
            return False
    except:
        traceback.print_exc()
        flash("user registration failed.")
    

def check_registration_validity(role, username, password):
    print(f"Entered users:check_registration_validity({role}, {username}, {password}).")
    try:
        if role not in ['user', 'admin']:
            flash("Invalid user type.")
            return False
        elif len(password) < 3 or len(username) < 3:
            flash("Username and password must be at least 3 characters.")
            return False
        for char in username.lower() + password.lower():
            if char not in allowed_chars:
                flash("Please ensure that your username and password contain only letters A-ö and integers.")
                return False

        sql = "SELECT * FROM users WHERE username=:username"
        user = db.session.execute(sql, {"username": username}).fetchone()
        if username == password:
            print("Username and password cannot be the same.")
            flash("Username and password cannot be the same.")
            return False
        elif user:
            print("User already exists.")
            flash("User already exists.")
            return False
        else:
            print("Registration information is valid")
            return True
    except:
        traceback.print_exc()
        return False

def get_users():
    print(f"Entered used:get_users().")
    try:
        sql = "SELECT id, username FROM users WHERE visible=true"
        users = db.session.execute(sql).fetchall()
        return users
    except:
        traceback.print_exc()
        return False