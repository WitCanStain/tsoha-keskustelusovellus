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
    except Exception as e:
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
            
    except Exception as e:
        flash("Updating thread failed.")
        traceback.print_exc()
        return False

    
def get_thread(thread_id):
    print(f"Entered messaging:get_thread({thread_id}).")
    try:
        sql = "SELECT title FROM threads WHERE id=:thread_id"
        title = db.session.execute(sql, {"thread_id": thread_id}).fetchone()[0]
        sql = "SELECT user_id, content, username, messages.id FROM messages LEFT JOIN users ON user_id=users.id WHERE thread_id=:thread_id ORDER BY messages.id ASC"
        result = db.session.execute(sql, {"thread_id": thread_id})
        messages = result.fetchall()
        
        return {"id":thread_id, "title": title, "messages": messages}
    except Exception as e:
        traceback.print_exc()
        return False

def get_thread_id_from_message_id(message_id):
    print(f"Entered messaging:get_thread_id_from_message_id({message_id}).")
    try:
        sql = "SELECT thread_id FROM messages WHERE id=:message_id"
        thread_id = db.session.execute(sql, {"message_id": message_id}).fetchone()[0]
        return thread_id
    except Exception as e:
        traceback.print_exc()
        return False

def create_message(thread_id, user_id, content):
    print(f"Entered messaging:create_message({thread_id}, {user_id}, {content}).")
    try:
        if not content:
            flash("You cannot create an empty message.")
            return False
        content = escape(content) # sanitize input
        print(f"escaped message: {content}")
        sql = "INSERT INTO messages (content, thread_id, user_id) VALUES (:content, :thread_id, :user_id) RETURNING id"
        message_id = db.session.execute(sql, {"content": content, "thread_id": thread_id, "user_id": user_id}).fetchone()[0]
        db.session.commit()
        return message_id            
    except Exception as e:
        traceback.print_exc()
        flash("Message creation failed.")
        return False

def update_message(message_id, new_content):
    print(f"Entered messaging:update_message({message_id}, {new_content}).")
    try:
        if not new_content:
            flash("Cannot create an empty message.")
            return False
        new_content = escape(new_content)
        sql = "UPDATE messages SET content=:new_content WHERE id=:message_id"
        db.session.execute(sql, {"new_content": new_content, "message_id": message_id})
        db.session.commit()
        return True
    except Exception as e:
        flash("Updating message failed.")
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
    except Exception as e:
        traceback.print_exc()
        return False

def create_category(category_name):
    print(f"Entered messaging:create_category({category_name}).")
    try:
        if not category_name:
            flash("Category creation failed. Did you provide a name for the category?")
            return False

        sql = "INSERT INTO categories(name) VALUES (:name) RETURNING id"
        category_id = db.session.execute(sql, {"name": category_name}).fetchone()[0]
        db.session.commit()
        return category_id
    except Exception as e:
        flash("Category creation failed.")
        traceback.print_exc()
        return False

def get_categories():
    print("Entered messaging:get_categories().")
    try:
        sql = """
        SELECT categories.id, categories.name, COUNT(DISTINCT threads.id), COUNT(messages.id), MAX(messages.created)
        FROM categories 
        LEFT JOIN threads 
        ON categories.id=threads.category_id 
        LEFT JOIN messages 
        ON messages.thread_id=threads.id 
        GROUP BY categories.id ;
        """
        categories = db.session.execute(sql).fetchall()
        return categories
    except Exception as e:
        traceback.print_exc()
        return False

def get_category(category_id):
    print(f"Entered messaging:get_category({category_id}).")
    try:
        sql = "SELECT id, title FROM threads WHERE category_id=:category_id"
        threads = db.session.execute(sql, {"category_id": category_id}).fetchall()
        sql = "SELECT name FROM categories WHERE id=:category_id"
        category_name = db.session.execute(sql, {"category_id": category_id}).fetchone()[0]
        return {"name": category_name, "threads": threads}
        
    except Exception as e:
        traceback.print_exc()
        return False

def search(search_query):
    print(f"Entered messaging:search({search_query}).")
    try:
        sql = """
        SELECT messages.id, messages.content, messages.thread_id, messages.created, users.username, threads.title 
        FROM messages LEFT JOIN users ON messages.user_id=users.id 
        LEFT JOIN threads ON messages.thread_id=threads.id 
        WHERE content LIKE :search_query"""
        results = db.session.execute(sql, {"search_query": f"%{search_query}%"}).fetchall()
        print(results)
        return results
    except Exception as e:
        traceback.print_exc()
        return False