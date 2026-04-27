# Back End Full_Stack App
from flask import Flask, request, jsonify
import sqlite3
import os

# create the backend application, which only works with the database
backend_app = Flask(__name__)
MAX_TEXT_LENGTH = 20
MAX_COST = 100000


def db_path():
    return os.path.join(os.path.dirname(__file__), 'database.db')

# function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def validate_payload(name, estimated_cost, notes):
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > MAX_TEXT_LENGTH:
        return False, f"Name must be 1 to {MAX_TEXT_LENGTH} characters."
    if not isinstance(notes, str) or not notes.strip() or len(notes.strip()) > MAX_TEXT_LENGTH:
        return False, f"Notes must be 1 to {MAX_TEXT_LENGTH} characters."

    try:
        cost_value = float(estimated_cost)
    except (TypeError, ValueError):
        return False, "Estimated cost must be a valid number."

    if cost_value <= 0 or cost_value >= MAX_COST:
        return False, f"Estimated cost must be greater than 0 and less than {MAX_COST}."

    return True, {
        "name": name.strip(),
        "estimated_cost": cost_value,
        "notes": notes.strip()
    }

# ENDPOINTS
@backend_app.route("/api", methods=["GET"])
def get_all():
    # retrieve list from the database
    # connect to DB, run the SQL statement, close the connection
    conn = get_db_connection()
    rows = conn.execute('SELECT id, created, name, estimated_cost, notes FROM destinations ORDER BY id DESC').fetchall()
    conn.close()
    result_list = [dict(row) for row in rows]
    return jsonify(result_list), 200

# create a new destination
@backend_app.route("/api/new", methods=["POST"])
def create_dest():
    # get info from POST request
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON body."}), 400

    # Accept either the original list format or a standard JSON object
    payload = data[0] if isinstance(data, list) and data else data
    if not isinstance(payload, dict):
        return jsonify({"error": "JSON body must be an object."}), 400

    is_valid, result = validate_payload(
        payload.get("name"),
        payload.get("estimated_cost"),
        payload.get("notes")
    )
    if not is_valid:
        return jsonify({"error": result}), 400

    # Connect to DB and insert information
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO destinations (name, estimated_cost, notes) VALUES (?, ?, ?)',
        (result["name"], result["estimated_cost"], result["notes"])
    )
    conn.commit()
    conn.close()
    return jsonify({
        "id": cursor.lastrowid,
        "name": result["name"],
        "estimated_cost": result["estimated_cost"],
        "notes": result["notes"]
    }), 201
