# Front End Full-Stack App
from flask import Flask, render_template, request
import requests
# Note the two libraries:
#
# flask.request processes incoming requests to the frontend server
# (in other words, form submissions)
#
# the python requests library (plural!) sends requests to
# a different server:  the backend server
# need to execute in Terminal:    pip install requests

# create the frontend app, which talks to the user, receives
# user requests, and then approves them to be sent to the backend
frontend_app = Flask(__name__)
backend_url = "http://127.0.0.1:5001"
MAX_TEXT_LENGTH = 20
MAX_COST = 100000


def validate_form(name, estimated_cost, notes):
    if not name or len(name.strip()) == 0 or len(name.strip()) > MAX_TEXT_LENGTH:
        return False, f"Destination name must be 1 to {MAX_TEXT_LENGTH} characters."
    if not notes or len(notes.strip()) == 0 or len(notes.strip()) > MAX_TEXT_LENGTH:
        return False, f"Notes must be 1 to {MAX_TEXT_LENGTH} characters."

    try:
        cost_value = float(estimated_cost)
    except (TypeError, ValueError):
        return False, "Estimated cost must be a number."

    if cost_value <= 0 or cost_value >= MAX_COST:
        return False, f"Estimated cost must be greater than 0 and less than {MAX_COST}."

    return True, {
        "name": name.strip(),
        "estimated_cost": cost_value,
        "notes": notes.strip()
    }

# ROUTES

# view all destinations on homepage
@frontend_app.route("/")
@frontend_app.route("/home")
def home():
    # send a request to the backend for all the destinations
    # NOTE: the response variable includes the entire HTTP response
    # NOTE: can use print(dest_list.json()) # can use for debugging
    places = []
    error_message = None
    try:
        response = requests.get(backend_url + "/api", timeout=5)
        response.raise_for_status()
        places = response.json()
    except requests.RequestException:
        error_message = "Could not load destinations from backend. Make sure backend is running."

    # now, pass the data returned from the backend to the template and
    # render it (send it to the client computer as an HTML file)
    return render_template('bucketlist.html', places=places, error_message=error_message)

# add a new destination
@frontend_app.route("/new_destination", methods=["GET", "POST"])
def new_destination():
    # if GET request, display the form
    if request.method == "GET":
        return render_template('new_destination.html')
    # process the submitted form on a POST request
    if request.method == "POST":
        # Retrieve data from the form using the 'name' attribute
        dest_name = request.form.get('dest_name', '')
        estimated_cost = request.form.get('estimated_cost', '')
        notes = request.form.get('notes', '')

        # Frontend validation happens before sending data to backend.
        is_valid, result = validate_form(dest_name, estimated_cost, notes)
        if not is_valid:
            return render_template(
                'new_destination.html',
                error_message=result,
                old_values={
                    "dest_name": dest_name,
                    "estimated_cost": estimated_cost,
                    "notes": notes
                }
            )

        # build json with requested data
        new_dest = {
            "name": result["name"],
            "estimated_cost": result["estimated_cost"],
            "notes": result["notes"]
        }
        # send a POST request to the backend to create a new entry
        try:
            response = requests.post(backend_url + "/api/new", json=new_dest, timeout=5)
            if response.status_code != 201:
                backend_error = response.json().get("error", "Failed to add destination.")
                return render_template(
                    'new_destination.html',
                    error_message=backend_error,
                    old_values={
                        "dest_name": dest_name,
                        "estimated_cost": estimated_cost,
                        "notes": notes
                    }
                )
        except (requests.RequestException, ValueError):
            return render_template(
                'new_destination.html',
                error_message="Could not reach backend. Make sure backend is running.",
                old_values={
                    "dest_name": dest_name,
                    "estimated_cost": estimated_cost,
                    "notes": notes
                }
            )

        # Give the user a message
        return f'<h1>Your form was submitted to add {result["name"]}. <a href="/home">Continue</a></h1>'
