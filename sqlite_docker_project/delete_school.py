import sqlite3

def delete_school_data():
    # Get school ID from user
    school_id = int(input("Enter the School ID to delete: "))

    # Connect to all three databases
    conn_demographics = sqlite3.connect('demographics.db')
    conn_facilities = sqlite3.connect('facilities.db')
    conn_academic = sqlite3.connect('academic.db')

    try:
        # Start transactions
        conn_demographics.execute('BEGIN')
        conn_facilities.execute('BEGIN')
        conn_academic.execute('BEGIN')

        # Delete from demographics
        demographics_cursor = conn_demographics.execute('''
            DELETE FROM Schools
            WHERE school_id = ?''', (school_id,))
        
        # Delete from facilities
        facilities_cursor = conn_facilities.execute('''
            DELETE FROM facilities
            WHERE school_id = ?''', (school_id,))
        
        # Delete from academics
        academics_cursor = conn_academic.execute('''
            DELETE FROM Academics
            WHERE school_id = ?''', (school_id,))
        
        # Check if the school_id exists
        if any(cursor.rowcount == 0 for cursor in (demographics_cursor, facilities_cursor, academics_cursor)):
            raise ValueError(f"School ID {school_id} does not exist in one or more tables.")

        # Commit transactions
        conn_demographics.commit()
        conn_facilities.commit()
        conn_academic.commit()
        print("\nSchool data deleted successfully!")

    except Exception as e:
        # Rollback in case of error
        conn_demographics.rollback()
        conn_facilities.rollback()
        conn_academic.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close connections
        conn_demographics.close()
        conn_facilities.close()
        conn_academic.close()

if __name__ == "__main__":
    delete_school_data()
