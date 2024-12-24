
import sqlite3
import pandas as pd
import re

def connect_to_db(db_name):
    """Connect to the specified SQLite database."""
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to {db_name}: {str(e)}")
        return None

def natural_query_to_sql(user_query):
    """Convert natural language queries to SQL queries."""
    if "list all schools" in user_query.lower():
        return "SELECT * FROM Schools;", 'Schools'
    elif "schools in" in user_query.lower():
        region = re.search(r"schools in (.+)", user_query, re.I)
        if region:
            state = region.group(1).title().strip()
            return f"SELECT school_id, name, state FROM Schools WHERE state = '{state}';", 'Schools'
    elif "top ranked schools" in user_query.lower():
        return "SELECT school_id, national_ranking, avg_exam_score FROM Academics ORDER BY national_ranking LIMIT 10;", 'Academics'
    elif "compare schools" in user_query.lower():
        return "compare_schools", 'Custom'
    else:
        return None, None

def execute_sql_query(db_connection, query):
    """Execute the given SQL query and return a DataFrame."""
    try:
        df = pd.read_sql_query(query, db_connection)
        return df
    except Exception as e:
        return f"Error: {str(e)}"
def integrate_school_names(dataframe, conn_demographics):
    """Add school names to a DataFrame using the demographics database."""
    try:
        # Fetch school names from demographics
        df_schools = pd.read_sql_query("SELECT school_id, name FROM Schools", conn_demographics)
        
        # Merge the input dataframe with the school names
        merged_df = pd.merge(dataframe, df_schools, on="school_id", how="left")
        return merged_df
    except Exception as e:
        return f"Error: {str(e)}"

def compare_schools():
    """Custom function to compare schools across databases."""
    conn_demographics = connect_to_db('demographics.db')
    conn_facilities = connect_to_db('facilities.db')
    
    if not conn_demographics or not conn_facilities:
        return "Error: Unable to connect to one or more databases."
    
    try:
        # Fetch data from both databases
        df_schools = pd.read_sql_query("SELECT school_id, name, state FROM Schools", conn_demographics)
        df_facilities = pd.read_sql_query("SELECT school_id, annual_fee FROM Facilities", conn_facilities)
        
        # Merge the data
        df_combined = pd.merge(df_schools, df_facilities, on="school_id", how="inner")
        return df_combined
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn_demographics.close()
        conn_facilities.close()

def main():
    conn_demographics = connect_to_db('demographics.db')
    conn_academic = connect_to_db('academic.db')
    conn_facilities = connect_to_db('facilities.db')

    print("\nWelcome to School Dekho.com!")
    print("Example queries you can try:")
    print("- List all schools")
    print("- Schools in state")
    print("- Top ranked schools")
    print("- Compare schools")

    while True:
        user_query = input("\nEnter your query (or type 'exit' to quit): ").strip()
        if user_query.lower() == 'exit':
            print("\nThank you for using School Dekho.com. Goodbye!")
            break

        sql_query, db_type = natural_query_to_sql(user_query)
        if sql_query == 'compare_schools':
            result_df = compare_schools()
        elif sql_query and db_type == 'Schools':
            result_df = execute_sql_query(conn_demographics, sql_query)
        elif sql_query and db_type == 'Academics':
            result_df = execute_sql_query(conn_academic, sql_query)
            if isinstance(result_df, pd.DataFrame):
                # Add school names to the academic query result
                result_df = integrate_school_names(result_df, conn_demographics)
        elif sql_query and db_type == 'Facilities':
            result_df = execute_sql_query(conn_facilities, sql_query)
            if isinstance(result_df, pd.DataFrame):
                # Add school names to the facilities query result
                result_df = integrate_school_names(result_df, conn_demographics)
        else:
            print("\nSorry, I couldn't understand the query. Please try again.")
            continue

        if isinstance(result_df, pd.DataFrame) and not result_df.empty:
            print("\nResults:\n", result_df.to_string(index=False))
        elif isinstance(result_df, pd.DataFrame) and result_df.empty:
            print("\nNo results found for your query.")
        else:
            print("\n", result_df)

    conn_demographics.close()
    conn_academic.close()
    conn_facilities.close()

if __name__ == "__main__":
    main()
