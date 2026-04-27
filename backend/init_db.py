import sqlite3
import os

# connect to the database (if file does not exist -- create it)
db_file_path = os.path.join(os.path.dirname(__file__), 'database.db')
connection = sqlite3.connect(db_file_path)

# open the schema.sql file which describes the database
with open(os.path.join(os.path.dirname(__file__), 'schema.sql')) as db_file:
    # run the commands in this file
    connection.executescript(db_file.read())

# connect to the database with a cursor
cur = connection.cursor()

# add two default entries
cur.execute(
    "INSERT INTO destinations (name, estimated_cost, notes) VALUES (?, ?, ?)",
    ('Hawaii', 3200.00, 'Beach vacation')
)
cur.execute(
    "INSERT INTO destinations (name, estimated_cost, notes) VALUES (?, ?, ?)",
    ('Bahamas', 2800.00, 'Family trip')
)

# commit changes and close the connection
connection.commit()
connection.close()