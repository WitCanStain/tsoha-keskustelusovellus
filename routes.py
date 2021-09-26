from app import app
from flask import redirect, render_template, request, session


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    from users import login
    if login(username, password):
        session["username"] = username
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        from users import user_register
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        if user_register(role, username, password):
            session["username"] = username
            return redirect("/")
    elif request.method == "GET":
        return render_template("register.html")    
