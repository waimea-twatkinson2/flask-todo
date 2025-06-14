#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db import connect_db
from app.helpers.errors import register_error_handlers, not_found_error


# Create the app
app = Flask(__name__)

# Setup a session for messages, etc.
init_session(app)

# Handle 404 and 500 errors
register_error_handlers(app)


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        # Get all the things from the DB
        sql = """
            SELECT id, thing_to_do, timestamp, priority, description
            FROM todo
            ORDER BY priority DESC
        """
        result = client.execute(sql)
        todo = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", todo=todo)
    
    
#-----------------------------------------------------------    
# Item page
#-----------------------------------------------------------
@app.get("/item/<int:id>")
def item(id):
    with connect_db() as client:
        # Get the item from the DB
        sql = "SELECT id, thing_to_do, timestamp, priority, description FROM todo WHERE id=?"
        values = [id]
        result = client.execute(sql, values)
        todo = result.rows

        # And show it on the page
        return render_template("pages/item.jinja", todo=todo)


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Route for adding a task, using data posted from a form
#-----------------------------------------------------------
@app.post("/add-thing")
def add_thing():
    # Get the data from the form
    thing_to_do  = request.form.get("item")
    priority = request.form.get("priority")
    description = request.form.get("description")

    with connect_db() as client:
        # Add the task to the DB
        sql = "INSERT INTO todo (thing_to_do, priority, description) VALUES (?, ?, ?)"
        values = [thing_to_do, priority, description]
        client.execute(sql, values)

        # Go back to the home page
        flash(f"Task '{thing_to_do}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM things WHERE id=?"
        values = [id]
        client.execute(sql, values)

        # Go back to the home page
        flash("Thing deleted", "warning")
        return redirect("/")

