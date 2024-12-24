import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

# Function to connect to a database container
def connect_to_db(container, db_file):
    return sqlite3.connect(f"/{container}/{db_file}")

@app.route('/all-schools', methods=['GET'])
def get_all_schools():
    conn1 = connect_to_db("demographics-container", "demographics.db")
    # Repeat for other DBs and query data...
    conn2 = connect_to_db("facilities-container", "facilities.db")
    conn3 = connect_to_db("academic-container", "academic.db")


