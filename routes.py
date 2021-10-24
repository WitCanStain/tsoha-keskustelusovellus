from app import app
from flask import redirect, render_template, request, session, flash, abort
import users
from users import get_users # users.get_users() bugs out, no idea why
import messaging
@app.route("/")
def index():
    categories = messaging.get_categories()
    return render_template("index.html", categories=categories)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    if not users.login(username, password):
        flash("Username or password is incorrect.")
        
    return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        if  users.user_register(role, username, password):
            users.login(username, password)
            return redirect("/")
        else:
            flash("user registration failed.")
            return redirect("/register")
    elif request.method == "GET":
        return render_template("register.html")    

@app.route("/create_thread", methods=["POST", "GET"])
def create_thread():
    if "user_id" not in session:
        flash(("Cannot create threads without logging in!"))
        return redirect("/")
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
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
        category_id = int(request.args.get('category', None)) if request.args.get('category', None) else None
        categories = None
        if not category_id:
            categories = messaging.get_categories()
            category = None
        else:
            category = messaging.get_category(category_id)
        return render_template("create_thread.html", categories=categories, category=category)

@app.route("/create_message", methods=["POST"])
def create_message():
    if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
    message = request.form["message"]
    thread_id = request.form["thread_id"]
    user_id = session["user_id"]
    if not message:
        flash("You cannot create an empty message.")
    else:
        result = messaging.create_message(thread_id, user_id, message)
        if not result:
            flash("Message creation failed.")
    return redirect(f"/thread/{thread_id}")


@app.route("/create_category", methods=["POST", "GET"])
def create_category():
    if not session["role"] == "admin":
        abort(403)
    if request.method == "GET":
        user_list = get_users()
        return render_template("create_category.html", users=user_list)
    elif request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        category_name = request.form["name"]
        users = request.form.getlist("users")
        category_id = messaging.create_category(category_name, users)
        
        if category_id:
            return redirect(f"/category/{category_id}")
        else:
            return redirect("/create_category")

@app.route("/update_message/<int:id>", methods=["POST", "GET"])
def update_message(id):
    if not (messaging.message_is_owned_by_user(id, session["user_id"])):
        flash("You cannot edit messages that are not yours")
        return redirect("/")
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        new_content = request.form["new_content"]
        thread_id = request.form["thread_id"]
        messaging.update_message(id, new_content)
        return redirect(f"/thread/{thread_id}")
    elif request.method == "GET":
        thread_id = messaging.get_thread_id_from_message_id(id)
        if thread_id:
            return redirect(f"/thread/{thread_id}?edit={id}")
        else:
            abort(404, description="Resource not found")

@app.route("/remove_message/<int:id>", methods=["POST"])
def remove_message(id):
    if not (messaging.message_is_owned_by_user(id, session["user_id"])):
        flash("You cannot delete messages that are not yours.")
        return redirect("/")
    if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
    thread_id = messaging.remove_message(id)
    if thread_id:
        return redirect(f"/thread/{thread_id}")
    else:
        return redirect("/")


@app.route("/thread/<id>", methods=["GET"])
def thread(id):
    edit_message = int(request.args.get('edit', None)) if request.args.get('edit', None) else None
    edit_thread = int(request.args.get('editthread', None)) if request.args.get('editthread', None) else None
    message_id = int(request.args.get('message', None)) if request.args.get('message', None) else None
    thread = messaging.get_thread(id)
    
    if thread:
        return render_template("thread.html", thread=thread, edit_message=edit_message, edit_thread=edit_thread, message_id=message_id)
    else:
        return "Thread could not be found."

@app.route("/update_thread/<int:id>", methods=["POST", "GET"])
def update_thread(id):
    if not messaging.user_owns_thread(id, session["user_id"]):
        flash("You are not the owner of this thread.")
        abort(403)
    if request.method == "GET":
        return redirect(f"/thread/{id}?editthread={id}")
    elif request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        new_title = request.form["new_title"]
        if messaging.update_thread(id, new_title):
            return redirect(f"/thread/{id}")
        else:
            return redirect(f"/update_thread/{id}")

@app.route("/remove_thread/<int:id>", methods=["POST"])
def remove_thread(id):
    if not messaging.user_owns_thread(id, session["user_id"]):
        flash("You are not the owner of this thread.")
        return redirect("/")
    category_id = messaging.remove_thread(id)
    if category_id:
        return redirect(f"/category/{category_id}")
    else:
        flash("Removing thread failed.")
        return redirect("/")

@app.route("/category/<int:id>", methods=["GET"])
def category(id):
    category = messaging.get_category(id)
    if category:
        return render_template("category.html", category=category)
    else:
        abort(404, description="Resource not found")
        
@app.route("/remove_category/<int:id>", methods=["POST"])
def remove_category(id):
    if session["csrf_token"] != request.form["csrf_token"] or session["role"] != "admin":
            abort(403)
    result = messaging.remove_category(id)
    if not result:
        flash("Removing category failed.")
    return redirect("/")

@app.route("/search", methods=["POST"])
def search():
    search_query = request.form["search_query"]
    search_results = messaging.search(search_query)
    return render_template("search_results.html", search_results=search_results)

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(403)
def unauthorized(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
