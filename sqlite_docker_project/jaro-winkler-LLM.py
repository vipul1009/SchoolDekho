import os
import sqlite3
import pandas as pd
import google.generativeai as genai
from rapidfuzz import process, fuzz
from tabulate import tabulate  # Import tabulate for formatting results

# Configure Gemini API with the API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Function to apply Jaro-Winkler similarity for school name correction
def get_corrected_school_name(user_input, school_names):
    best_match = process.extractOne(user_input, school_names, scorer=fuzz.WRatio)
    print(f"Fuzzy matching result: {best_match}")  # Debugging output to check match
    if best_match and best_match[1] > 70:  # Lowered threshold for better matching
        return best_match[0]
    return user_input

# Get query and school name from user
user_query = input("Enter your query about schools: ")
school_name_input = input("Enter the school name (or 'nil' for general query): ")

# Connect to demographics.db to fetch the school names
def fetch_school_names():
    conn = sqlite3.connect('demographics.db')  # Connect to the demographics database
    cursor = conn.cursor()
    
    # Query to get all school names
    cursor.execute("SELECT name FROM Schools")
    school_names = [row[0] for row in cursor.fetchall()]  # Get list of school names
    conn.close()
    
    return school_names

# Correct school name if provided
if school_name_input.lower() != "nil":
    school_names_in_db = fetch_school_names()  # Fetch actual school names from the database
    corrected_school_name = get_corrected_school_name(school_name_input, school_names_in_db)
    print(f"Corrected School Name: {corrected_school_name}")
    user_query = f"{user_query} about {corrected_school_name}"  # Merge query with corrected school name

# Updated schema description with table names
schema_description = """
There are three databases: demographics.db, facilities.db, and academic.db.

Schema:
- demographics.db (Schools): school_id, name, state, board, student_population, established_year, school_type
- facilities.db (Facilities): school_id, annual_fee, hostel_available, transport_available, sports_facilities, arts_programs, club_activities
- academic.db (Academics): school_id, avg_exam_score, national_ranking, pass_percentage, top_student_score
"""

# Prepare the input content for Gemini model (Query + Schema)
content = f"""
Based on the following schema, generate an SQL query to answer the question:

Query: {user_query}
Schema: {schema_description}
"""

# Generate SQL using Gemini
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(content)

# Extract and clean the SQL query
if response.text:
    sql_query = response.text.replace("```sql", "").replace("```", "").strip()
    print("Generated SQL Query:\n", sql_query)
else:
    print("No response generated.")
    exit()

# Function to execute queries using ATTACH DATABASE
def execute_query_with_attach(sql_query):
    try:
        conn = sqlite3.connect(":memory:")  # In-memory connection
        cursor = conn.cursor()

        # Attach all databases
        cursor.execute("ATTACH DATABASE 'demographics.db' AS demographics;")
        cursor.execute("ATTACH DATABASE 'facilities.db' AS facilities;")
        cursor.execute("ATTACH DATABASE 'academic.db' AS academic;")

        # Ensure SQL references are in the correct format (using database alias)
        sql_query = sql_query.replace("demographics.db.Schools", "demographics.Schools")
        sql_query = sql_query.replace("facilities.db.Facilities", "facilities.Facilities")
        sql_query = sql_query.replace("academic.db.Academics", "academic.Academics")

        # Execute the query and read the result into a DataFrame
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# Execute the query and display results
result_df = execute_query_with_attach(sql_query)
if not result_df.empty:
    print("Query Results:")
    print(tabulate(result_df, headers='keys', tablefmt='pretty'))  # Format the result as a table
else:
    print("No results found or an error occurred.")
