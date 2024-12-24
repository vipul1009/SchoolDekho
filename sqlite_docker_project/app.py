from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import sqlite3
import pandas as pd
import google.generativeai as genai
from rapidfuzz import process

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secure key for session management

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Dummy user credentials for login validation
USER_CREDENTIALS = {'admin': '123'}

# Route for login page

@app.route('/')
def login():
    return render_template('login.html')
# Handle login submission
@app.route('/login', methods=['POST'])
def handle_login():
    data = request.json
    username = data['username']
    password = data['password']

    if USER_CREDENTIALS.get(username) == password:
        session['user'] = username  # Set session
        return jsonify({'success': True})
    return jsonify({'success': False})

# Main page after login
@app.route('/main')
def main_page():
    if 'user' in session:
        return render_template('index.html')  # Serve main page after login
    return redirect(url_for('login'))

# Function to fetch school names from the database
def fetch_school_names():
    try:
        conn = sqlite3.connect('data/demographics.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Schools")
        school_names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return school_names
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return []

# Function to correct school names using Jaro-Winkler
def get_corrected_school_name(user_input, school_names):
    best_match = process.extractOne(user_input, school_names)
    return best_match[0] if best_match and best_match[1] > 70 else user_input

# Route to handle queries
@app.route('/submit-query', methods=['POST'])
def submit_query():
    data = request.json
    user_query = data['query']
    school_name_input = data['schoolName']

    # Initialize corrected school name as None
    corrected_school_name = None

    # Correct school name if provided
    if school_name_input.lower() != "nil":
        school_names_in_db = fetch_school_names()
        corrected_school_name = get_corrected_school_name(school_name_input, school_names_in_db)

        # If the name is corrected, update the user query with the corrected name
        if corrected_school_name != school_name_input:
            user_query = f"{user_query} about {corrected_school_name}"

    print("Final User Query:", user_query)  # Log user query for debugging

    # Prepare content for Gemini API
    schema_description = """
    There are three attached databases: demographics.db, facilities.db, and academic.db.

    Schema:
    - demographics.db (Schools): school_id, name, state, board, student_population, established_year, school_type
    - facilities.db (Facilities): school_id, annual_fee, hostel_available, transport_available, sports_facilities, arts_programs, club_activities
    - academic.db (Academics): school_id, avg_exam_score, national_ranking, pass_percentage, top_student_score

    Ensure the generated SQL uses these exact table and column names.
    """

    content = f"Based on the following schema, generate an SQL query to answer the question:\n\nQuery: {user_query}\nSchema: {schema_description}"
    
    # Generate SQL query using Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(content)
    sql_query = response.text.replace("```sql", "").replace("```", "").strip()
    
    print("Generated SQL Query:", sql_query)  # Log generated query

    # Execute the generated SQL query
    result_df = execute_query_with_attach(sql_query)
    
    if not result_df.empty:
        result_html = result_df.to_html(classes='table table-bordered', index=False)  # Convert DataFrame to HTML
        return jsonify({
            'success': True, 
            'data': result_html, 
            'correctedSchoolName': corrected_school_name  # Send corrected name if applicable
        })
    
    return jsonify({'success': False, 'error': 'No results found.'})

# Function to execute SQL query with attached databases
def execute_query_with_attach(sql_query):
    try:
        conn = sqlite3.connect(":memory:")  # In-memory database to run the query
        cursor = conn.cursor()

        # Attach the three SQLite databases
        cursor.execute("ATTACH DATABASE 'data/demographics.db' AS demographics;")
        cursor.execute("ATTACH DATABASE 'data/facilities.db' AS facilities;")
        cursor.execute("ATTACH DATABASE 'data/academic.db' AS academic;")

        # Adjust the SQL query for attached databases
        sql_query = sql_query.replace("demographics.db.Schools", "demographics.Schools")
        sql_query = sql_query.replace("facilities.db.Facilities", "facilities.Facilities")
        sql_query = sql_query.replace("academic.db.Academics", "academic.Academics")

        # Execute the query and return the results as a DataFrame
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"SQL Execution Error: {e}")
        return pd.DataFrame()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
