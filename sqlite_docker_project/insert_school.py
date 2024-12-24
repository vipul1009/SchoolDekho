import sqlite3

def get_school_data():
    print("Enter School Details:")
    school_id = int(input("School ID: "))
    name = input("Name: ")
    state = input("State: ")
    board = input("Board: ")
    student_population = int(input("Student Population: "))
    established_year = int(input("Established Year: "))
    school_type = input("School Type: ")
    
    print("\nEnter Facilities Details:")
    annual_fee = float(input("Annual Fee: "))
    hostel_available = input("Hostel Available (yes/no): ").strip().lower() == 'yes'
    transport_available = input("Transport Available (yes/no): ").strip().lower() == 'yes'
    sports_facilities = input("Sports Facilities (comma-separated): ")
    arts_programs = input("Arts Programs (comma-separated): ")
    club_activities = input("Club Activities (comma-separated): ")

    print("\nEnter Academic Details:")
    avg_exam_score = float(input("Average Exam Score: "))
    national_ranking = int(input("National Ranking: "))
    pass_percentage = float(input("Pass Percentage: "))
    top_student_score = float(input("Top Student Score: "))

    return (school_id, name, state, board, student_population, established_year, school_type,
            annual_fee, hostel_available, transport_available, sports_facilities, arts_programs, club_activities,
            avg_exam_score, national_ranking, pass_percentage, top_student_score)

def insert_school_data():
    data = get_school_data()
    
    # Connect to all three databases
    conn_demographics = sqlite3.connect('demographics.db')
    conn_facilities = sqlite3.connect('facilities.db')
    conn_academic = sqlite3.connect('academic.db')

    try:
        # Start transactions
        conn_demographics.execute('BEGIN')
        conn_facilities.execute('BEGIN')
        conn_academic.execute('BEGIN')

        # Insert into demographics
        conn_demographics.execute('''
            INSERT INTO Schools (school_id, name, state, board, student_population, established_year, school_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            data[:7])

        # Insert into facilities
        conn_facilities.execute('''
            INSERT INTO facilities (school_id, annual_fee, hostel_available, transport_available, sports_facilities, arts_programs, club_activities)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (data[0], data[7], data[8], data[9], data[10], data[11], data[12]))

        # Insert into academics
        conn_academic.execute('''
            INSERT INTO Academics (school_id, avg_exam_score, national_ranking, pass_percentage, top_student_score)
            VALUES (?, ?, ?, ?, ?)''',
            (data[0], data[13], data[14], data[15], data[16]))

        # Commit transactions
        conn_demographics.commit()
        conn_facilities.commit()
        conn_academic.commit()
        print("\nSchool data inserted successfully!")

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
    insert_school_data()
