from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session

def login(username, password):
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
        print("Username or password is incorrect.")
        return False

def user_register(role, username, password):
    
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
        return False



def check_registration_validity(role, username, password):
    
    # if role not in ['user', 'admin']:
    #     return False
    sql = "SELECT * FROM users WHERE username=:username"
    print("username:" + username)
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if username == password:
        print("Username and password cannot be the same.")
        return False
    elif user:
        print("User already exists.")
        return False
    else:
        print("Registration information is valid")
        return True
    

    
