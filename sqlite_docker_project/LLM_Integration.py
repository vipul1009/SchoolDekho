import os
import sqlite3
import pandas as pd
import google.generativeai as genai

# Configure Gemini API with the API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Get user query as input
user_query = input("Enter your query about schools: ")

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

# Generate content using Gemini
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(content)

# Check if the response contains text
if response.text:
    sql_query = response.text.replace("```sql", "").replace("```", "").strip()
    # Correct table references in the SQL query
    sql_query = sql_query.replace("demographics.db.", "demographics.")
    sql_query = sql_query.replace("facilities.db.", "facilities.")
    sql_query = sql_query.replace("academic.db.", "academic.")
    print("Generated SQL Query:\n", sql_query)
else:
    print("No response generated.")
    exit()

# Function to execute queries using ATTACH DATABASE
def execute_query_with_attach(sql_query):
    try:
        # Connect to an in-memory database and attach others
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # Attach all databases
        cursor.execute("ATTACH DATABASE 'demographics.db' AS demographics;")
        cursor.execute("ATTACH DATABASE 'facilities.db' AS facilities;")
        cursor.execute("ATTACH DATABASE 'academic.db' AS academic;")

        # Execute the query and read the result into a DataFrame
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# Execute the query with attached databases
result_df = execute_query_with_attach(sql_query)

# Display the final result
if not result_df.empty:
    print("Query Results:")
    print(result_df)
else:
    print("No results found or an error occurred.")






# import os
# import sqlite3
# import pandas as pd
# import google.generativeai as genai
# from rapidfuzz import process, fuzz

# # Configure Gemini API with the API key
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# # Function to fetch all school names from the database for matching
# def fetch_school_names():
#     conn = sqlite3.connect("demographics.db")
#     query = "SELECT name FROM Schools;"
#     school_names = pd.read_sql_query(query, conn)['name'].tolist()
#     conn.close()
#     return school_names

# # Function to find the closest match using Jaro-Winkler similarity
# def get_closest_match(user_input, school_names):
#     # Extract the best match and its score
#     result = process.extractOne(user_input, school_names, scorer=fuzz.WRatio)
#     if result:
#         match = result[0]  # Extract the matched name
#         return match
#     return user_input  # Return the input if no match is found

# # Get user query as input
# user_query = input("Enter your query about schools: ")

# # Updated schema description with table names
# schema_description = """
# There are three databases: demographics.db, facilities.db, and academic.db.

# Schema:
# - demographics.db (Schools): school_id, name, state, board, student_population, established_year, school_type
# - facilities.db (Facilities): school_id, annual_fee, hostel_available, transport_available, sports_facilities, arts_programs, club_activities
# - academic.db (Academics): school_id, avg_exam_score, national_ranking, pass_percentage, top_student_score
# """

# # Prepare the input content for Gemini model (Query + Schema)
# content = f"""
# Based on the following schema, generate an SQL query to answer the question:

# Query: {user_query}
# Schema: {schema_description}
# """

# # Generate content using Gemini
# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content(content)

# # Check if the response contains text
# if response.text:
#     sql_query = response.text.replace("```sql", "").replace("```", "").strip()
# else:
#     print("No response generated.")
#     exit()

# # Correct table references in the SQL query
# sql_query = sql_query.replace("facilities.db", "facilities.Facilities")
# sql_query = sql_query.replace("demographics.db", "demographics.Schools")
# sql_query = sql_query.replace("academic.db", "academic.Academics")

# # Fetch school names and correct school name in query
# school_names_in_query = fetch_school_names()
# user_input_school_name = user_query.split(" of ")[-1].strip()
# corrected_school_name = get_closest_match(user_input_school_name, school_names_in_query)
# sql_query = sql_query.replace(f"'{user_input_school_name}'", f"'{corrected_school_name}'")
# print(f"Corrected School Name: {corrected_school_name}")

# # Function to execute queries using ATTACH DATABASE
# def execute_query_with_attach(sql_query):
#     try:
#         conn = sqlite3.connect(":memory:")
#         cursor = conn.cursor()

#         # Attach all databases
#         cursor.execute("ATTACH DATABASE 'demographics.db' AS demographics;")
#         cursor.execute("ATTACH DATABASE 'facilities.db' AS facilities;")
#         cursor.execute("ATTACH DATABASE 'academic.db' AS academic;")

#         # Execute the query and read the result into a DataFrame
#         df = pd.read_sql_query(sql_query, conn)
#         conn.close()
#         return df
#     except sqlite3.Error as e:
#         print(f"Error: {e}")
#         return pd.DataFrame()

# # Execute the query with attached databases
# result_df = execute_query_with_attach(sql_query)

# # Display the final result
# if not result_df.empty:
#     print("Query Results:")
#     print(result_df)
# else:
#     print("No results found or an error occurred.")