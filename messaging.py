from db import db
from flask import session, flash, escape
from time import time
import traceback

def create_thread(title, message, category_id):
    print(f"Entered messaging:create_thread({title}, {message}, {category_id}).")
    try:
        if message:
            title = escape(title)
            user_id = session["user_id"]
            created = time()
            sql = "INSERT INTO threads (title, category_id, created_by) VALUES (:title, :category_id, :created_by) RETURNING id"
            result = db.session.execute(sql, {"title": title, "category_id": category_id, "created_by": user_id})
            thread_id = result.fetchone()[0]
            print(f"thread_id: {thread_id}")
            create_message(thread_id, user_id, message)
            db.session.commit()
            return thread_id
        else:
            flash("You cannot create a thread with an empty starting message.")
            return False
    except:
        flash("Thread creation failed.")
        traceback.print_exc()
        return False

def update_thread(thread_id, title):
    print(f"Entered messaging:update_thread({thread_id}, {title}).")
    try:
        if not title:
            flash("Cannot create empty thread title.")
            return False
        title = escape(title)
        sql = "UPDATE threads SET title=:title WHERE id=:thread_id"
        db.session.execute(sql, {"thread_id": thread_id, "title": title})
        db.session.commit()
        return True
            
    except:
        flash("Updating thread failed.")
        traceback.print_exc()
        return False

    
def get_thread(thread_id):
    print(f"Entered messaging:get_thread({thread_id}).")
    try:
        sql = "SELECT title FROM threads WHERE id=:thread_id AND visible=true"
        title = db.session.execute(sql, {"thread_id": thread_id}).fetchone()[0]
        sql = "SELECT user_id, content, username, messages.id FROM messages LEFT JOIN users ON user_id=users.id WHERE thread_id=:thread_id AND messages.visible=true ORDER BY messages.id ASC"
        result = db.session.execute(sql, {"thread_id": thread_id})
        messages = result.fetchall()
        
        return {"id":thread_id, "title": title, "messages": messages}
    except:
        traceback.print_exc()
        return False

def remove_thread(thread_id):
    print(f"Entered messaging:remove_thread({thread_id}).")
    try:
        sql = "UPDATE threads SET visible=false WHERE id=:thread_id RETURNING category_id"
        category_id = db.session.execute(sql, {"thread_id": thread_id}).fetchone()[0]
        sql = "UPDATE messages SET visible=false WHERE thread_id=:thread_id"
        db.session.execute(sql, {"thread_id": thread_id})
        db.session.commit()
        return category_id
    except:
        traceback.print_exc()
        return False


def get_thread_id_from_message_id(message_id):
    print(f"Entered messaging:get_thread_id_from_message_id({message_id}).")
    try:
        sql = "SELECT thread_id FROM messages WHERE id=:message_id"
        thread_id = db.session.execute(sql, {"message_id": message_id}).fetchone()[0]
        return thread_id
    except:
        traceback.print_exc()
        return False

def create_message(thread_id, user_id, content):
    print(f"Entered messaging:create_message({thread_id}, {user_id}, {content}).")
    try:
        content = escape(content) # sanitize input
        print(f"escaped message: {content}")
        sql = "INSERT INTO messages (content, thread_id, user_id) VALUES (:content, :thread_id, :user_id) RETURNING id"
        message_id = db.session.execute(sql, {"content": content, "thread_id": thread_id, "user_id": user_id}).fetchone()[0]
        db.session.commit()
        return message_id            
    except:
        traceback.print_exc()
        return False

def update_message(message_id, new_content):
    print(f"Entered messaging:update_message({message_id}, {new_content}).")
    try:
        if not new_content:
            flash("Cannot create an empty message.")
            return False
        new_content = escape(new_content)
        sql = "UPDATE messages SET content=:new_content WHERE id=:message_id AND visible=true"
        db.session.execute(sql, {"new_content": new_content, "message_id": message_id})
        db.session.commit()
        return True
    except:
        flash("Updating message failed.")
        traceback.print_exc()
        return False

def remove_message(message_id):
    print(f"Entered messaging:remove_message({message_id}).")
    try:
        sql = "UPDATE messages SET visible=false WHERE id=:message_id RETURNING thread_id"
        thread_id = db.session.execute(sql, {"message_id": message_id}).fetchone()[0]
        db.session.commit()
        return thread_id
    except:
        flash("Could not remove message.")
        traceback.print_exc()
        return False

def message_is_owned_by_user(message_id, user_id):
    print(f"Entered messaging:message_is_owned_by_user({message_id}, {user_id}).")
    try:
        sql = "SELECT id FROM messages WHERE user_id=:user_id"
        id = db.session.execute(sql, {"user_id": user_id}).fetchone()[0]
        if id:
            return True
        else:
            return False
    except:
        traceback.print_exc()
        return False

def create_category(category_name, whitelist):
    print(f"Entered messaging:create_category({category_name}).")
    try:
        if not category_name:
            flash("Category creation failed. Did you provide a name for the category?")
            return False
        if len(whitelist) == 0:
            whitelist = None
        else:
            whitelist = list(map(int, whitelist))
        sql = "INSERT INTO categories(name, whitelist) VALUES (:name, :whitelist) RETURNING id"    
        category_id = db.session.execute(sql, {"name": category_name, "whitelist": whitelist}).fetchone()[0]
        db.session.commit()
        return category_id
    except:
        flash("Category creation failed.")
        traceback.print_exc()
        return False

def get_categories():
    print("Entered messaging:get_categories().")
    try:
        user_id = session["user_id"] if "user_id" in session else None
        print(user_id)
        sql = """
        SELECT categories.id, categories.name, COUNT(DISTINCT threads.id) AS thread_count, COUNT(messages.id) AS msg_count, SUBSTR(MAX(messages.created)::TEXT, 1, 19) AS last_msg_time
        FROM categories 
        LEFT JOIN threads 
        ON categories.id=threads.category_id AND threads.visible=true
        LEFT JOIN messages 
        ON messages.thread_id=threads.id AND messages.visible=true
        WHERE categories.visible=true AND (:user_id = ANY(whitelist) OR whitelist IS NULL)
        GROUP BY categories.id
        """
        categories = db.session.execute(sql, {"user_id": user_id}).fetchall()
        print(categories)
        return categories
    except:
        traceback.print_exc()
        return False

def get_category(category_id):
    print(f"Entered messaging:get_category({category_id}).")
    try:
        user_id = session["user_id"] if "user_id" in session else None
        if not user_has_category_access(category_id, user_id):
            print("User does not have access to this category.")
            return False
        sql = "SELECT id, title FROM threads WHERE category_id=:category_id AND visible=true"
        threads = db.session.execute(sql, {"category_id": category_id}).fetchall()
        sql = "SELECT id, name FROM categories WHERE id=:category_id LIMIT 1"
        result = db.session.execute(sql, {"category_id": category_id}).fetchone()
        category_id = result[0]
        category_name = result[1]
        
        return {"name": category_name, "id": category_id, "threads": threads}
        
    except:
        traceback.print_exc()
        return False

def remove_category(category_id):
    print(f"Entered messaging:remove_category({category_id})")
    try:
        sql = "UPDATE categories SET visible=false WHERE id=:category_id"
        db.session.execute(sql, {"category_id": category_id})
        sql = "UPDATE threads SET visible=false WHERE category_id=:category_id"
        db.session.execute(sql, {"category_id": category_id})
        sql = """UPDATE messages set visible=false FROM threads 
        WHERE messages.thread_id=threads.id AND threads.category_id=:category_id"""
        db.session.execute(sql, {"category_id": category_id})
        db.session.commit()
        return True
    except:
        traceback.print_exc()
        return False

def user_has_category_access(category_id, user_id):
    print(f"Entered messaging:user_has_category_access({category_id}, {user_id}).")
    try:
        if not user_id:
            sql = "SELECT id FROM categories WHERE id=:category_id AND whitelist IS NULL LIMIT 1"
        else:
            sql = "SELECT id FROM categories WHERE id=:category_id AND (:user_id=ANY(whitelist) OR whitelist IS NULL) LIMIT 1"
        result = db.session.execute(sql, {"category_id": category_id, "user_id": user_id}).fetchone()
        print(result)
        if result[0]:
            return True
        else:
            return False

    except:
        traceback.print_exc()
        return False

def user_owns_thread(thread_id, user_id):
    print(f"Entered messaging:user_owns_thread({thread_id}, {user_id}).")
    try:
        sql = "SELECT user_id FROM messages WHERE thread_id=:thread_id ORDER BY id ASC LIMIT 1"
        result = db.session.execute(sql, {"thread_id": thread_id}).fetchone()
        if result["user_id"] == user_id:
            return True
        else:
            return False
            
    except:
        traceback.print_exc()
        return False


def search(search_query):
    print(f"Entered messaging:search({search_query}).")
    try:
        sql = """
        SELECT messages.id, messages.content, messages.thread_id, SUBSTR(messages.created::TEXT, 1, 19) AS created, users.username, threads.title 
        FROM messages LEFT JOIN users ON messages.user_id=users.id 
        LEFT JOIN threads ON messages.thread_id=threads.id 
        WHERE content LIKE :search_query"""
        results = db.session.execute(sql, {"search_query": f"%{search_query}%"}).fetchall()
        print(results)
        return results
    except:
        traceback.print_exc()
        return False