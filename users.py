from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session, flash
import traceback
import secrets
from string import ascii_lowercase
allowed_chars = ascii_lowercase + "åäö0123456789"

def login(username, password):
    print(f"Entered users:login({username}, {password}).")
    try:
        if not username or not password:
            return False
        sql = "SELECT id, password, role FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        print(user)
        if user:
            user_id = user[0]
            db_password = user[1]
            user_role = user[2]
            print(f"db_pass: {db_password}")
            
            if db_password and check_password_hash(db_password, password):
                session["csrf_token"] = secrets.token_hex(16)
                session["username"] = username
                session["user_id"] = user_id
                session["role"] = user_role
                return user_id
        
        return False
    except:
        traceback.print_exc()
        return False

def user_register(role, username, password):
    print(f"Entered users:user_register({role}, {username}, {password}).")
    try:
        hash_value = generate_password_hash(password)
        if check_registration_validity(role, username, password):
            sql = "INSERT INTO users (role, username, password) VALUES (:role, :username, :password) RETURNING id"
            result = db.session.execute(sql, {"role":role if role else "user", "username":username, "password":hash_value})
            user_id = result.fetchone()[0]
            db.session.commit()
            session["username"] = username
            session["user_id"] = user_id
            session["role"] = role
            return user_id
        else:
            print("User registration could not be validified.")
            return False
    except:
        traceback.print_exc()
        return False
    

def check_registration_validity(role, username, password):
    print(f"Entered users:check_registration_validity({role}, {username}, {password}).")
    try:
        if role not in ["user", "admin"]:
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
            flash("Username and password cannot be the same.")
            return False
        elif user:
            flash("User already exists.")
            return False
        else:
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