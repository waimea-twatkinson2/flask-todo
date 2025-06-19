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
            SELECT id, thing_to_do, timestamp, priority, description, complete
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
@app.route("/add-thing", methods=["GET", "POST"])
def add_thing():
    if request.method == "POST":
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
    else:
        # Render the form page if accessed via GET
        return render_template("pages/add-thing.jinja")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM todo WHERE id=?"
        values = [id]
        client.execute(sql, values)

        # Go back to the home page
        flash("Deleted!")
        return redirect("/")

@app.get("/complete/<int:id>")
def complete_a_thing(id):
    with connect_db() as client:
        sql = "UPDATE todo SET complete=1 WHERE id=?"
        values = [id]
        client.execute(sql, values)
        flash("Completed!")
        return redirect("/")
    
@app.get("/uncomplete/<int:id>")
def uncomplete_a_thing(id):
    with connect_db() as client:
        sql = "UPDATE todo SET complete=0 WHERE id=?"
        values = [id]
        client.execute(sql, values)
        flash("Uncompleted!")
        return redirect("/")