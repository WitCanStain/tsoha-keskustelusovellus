from app import app
from flask import redirect, render_template, request, session, flash
from users import user_register, login
import messaging
@app.route("/")
def index():
    categories = messaging.get_categories()
    return render_template("index.html", categories=categories)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user_id = login(username, password)
    if user_id:
        session["username"] = username
        session["user_id"] = user_id
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        if  user_register(role, username, password):
            return redirect("/")
        else:
            return "Registration failed."
    elif request.method == "GET":
        return render_template("register.html")    

@app.route("/create_thread", methods=["POST", "GET"])
def create_thread():
    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        category_id = request.form["category"]
        thread_id = messaging.create_thread(title, message, category_id)
        if thread_id:
            print(f"Thread creation by {session['username']} successful.")
            return redirect(f"/thread/{thread_id}")
        else:
            return redirect("/create_thread")
    elif request.method == "GET":
        categories = messaging.get_categories()
        return render_template("create_thread.html", categories=categories)

@app.route("/create_message", methods=["POST"])
def create_message():
    message = request.form["message"]
    thread_id = request.form["thread_id"]
    user_id = session["user_id"]
    messaging.create_message(thread_id, user_id, message)
    return redirect(f"/thread/{thread_id}")


@app.route("/create_category", methods=["POST", "GET"])
def create_category():
    if request.method == "GET":
        return render_template("create_category.html")
    elif request.method == "POST":
        category_name = request.form["name"]
        category_id = messaging.create_category(category_name)
        if category_id:
            return redirect(f"/category/{category_id}")
        else:
            return redirect("/create_category")

@app.route("/update_message/<int:id>", methods=["POST", "GET"])
def update_message(id):
    if (message_is_owned_by_user(id, session["user_id"])):
        if request.method == "POST":
            new_content = request.form["new_content"]
            thread_id = request.form["thread_id"]
            messaging.update_message(id, new_content)
            return redirect(f"/thread/{thread_id}")
        elif request.method == "GET":
            thread_id = messaging.get_thread_id_from_message_id(id)
            if thread_id:
                return redirect(f"/thread/{thread_id}?edit={id}")
            else:
                return redirect("/404")

@app.route("/thread/<id>", methods=["GET"])
def thread(id):
    edit_message = int(request.args.get('edit', None)) if request.args.get('edit', None) else None
    edit_thread = int(request.args.get('editthread', None)) if request.args.get('editthread', None) else None
    thread = messaging.get_thread(id)
    if thread:
        return render_template("thread.html", thread=thread, edit_message=edit_message, edit_thread=edit_thread)
    else:
        return "Thread could not be found."

@app.route("/update_thread/<int:id>", methods=["POST", "GET"])
def update_thread(id):
    if request.method == "GET":
        return redirect(f"/thread/{id}?editthread={id}")
    elif request.method == "POST":
        new_title = request.form["new_title"]
        if messaging.update_thread(id, new_title):
            return redirect(f"/thread/{id}")
        else:
            return redirect(f"/update_thread/{id}")

@app.route("/category/<int:id>", methods=["GET"])
def category(id):
    category = messaging.get_category(id)
    if category:
        session["category_id"] = id
        session["category_name"] = category["name"]
        return render_template("category.html", category=category)
    else:
        return redirect("/404")

@app.route("/404", methods=["GET"])
def not_found():
    return "404: not found."