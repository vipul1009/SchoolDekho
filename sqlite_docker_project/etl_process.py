import pandas as pd
import sqlite3

# Load the unordered CSV with missing values
df_raw = pd.read_csv('updated_academic_data.csv')  # Replace with your file path
df_raw.rename(columns={'s_id': 'school_id'}, inplace=True)
df_raw.rename(columns={'average_exam_score': 'avg_exam_score'}, inplace=True)
df_raw.rename(columns={'ranking': 'national_ranking'}, inplace=True)
df_raw.rename(columns={'passing_percentage': 'pass_percentage'}, inplace=True)
df_raw.rename(columns={'top_score': 'top_student_score'}, inplace=True)


# Extract: Print first few rows to verify extraction
print("Extracted Data (Raw):")
print(df_raw.head())

# Transform: Handle missing values
df_transformed = df_raw.copy()
df_transformed['avg_exam_score'].fillna(df_transformed['avg_exam_score'].mean(), inplace=True)
df_transformed['national_ranking'].fillna(df_transformed['national_ranking'].median(), inplace=True)
df_transformed['pass_percentage'].fillna(df_transformed['pass_percentage'].mean(), inplace=True)
df_transformed['top_student_score'].fillna(df_transformed['top_student_score'].median(), inplace=True)

# Ensure data is sorted by school_id
df_transformed.sort_values(by='school_id', inplace=True)

# Connect to the SQLite database
conn = sqlite3.connect('academic.db')  # Replace with your database path
cursor = conn.cursor()

# Load: Update the target database table
for _, row in df_transformed.iterrows():
    cursor.execute("""
        UPDATE Academics 
        SET avg_exam_score = ?, national_ranking = ?, pass_percentage = ?, top_student_score = ?
        WHERE school_id = ?
    """, (row['avg_exam_score'], row['national_ranking'], row['pass_percentage'], row['top_student_score'], row['school_id']))

# Commit changes and close the connection
conn.commit()
conn.close()

print("ETL process completed successfully.")

