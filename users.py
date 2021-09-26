from db import db
from werkzeug.security import check_password_hash, generate_password_hash

def login(username, password):
    hash_value = generate_password_hash(password)
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    db_password = result.fetchone()
    print(db_password)
    if db_password and check_password_hash(hash_value, password):
        return True
    else:
        print("Username or password is incorrect.")
        return False

def user_register(role, username, password):
    
    hash_value = generate_password_hash(password)
    if check_registration_validity(role, username, password):

        sql = "INSERT INTO users (role, username, password, visible) VALUES (:role, :username, :password, :visible)"
        db.session.execute(sql, {"role":role, "username":username, "password":hash_value, "visible":True})
        db.session.commit()
        return True
    else:
        print("User registration could not be validified.")
        return False



def check_registration_validity(role, username, password):
    
    if role not in ['user', 'admin']:
        return False
    sql = "SELECT * FROM users WHERE username=:username"
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
    

    
