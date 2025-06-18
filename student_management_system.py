# --- FULL STUDENT MANAGEMENT SYSTEM WITH ADMIN VIEW ---

import sqlite3
import datetime
import csv

# Reset DB every time
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Drop old tables
cursor.executescript('''
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS communication;
DROP TABLE IF EXISTS users;
''')

# Re-create tables
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Student', 'Teacher', 'Parent', 'Admin')),
        UNIQUE(name, role)
    )
''')

cursor.execute('''
    CREATE TABLE students (
        user_id INTEGER,
        age INTEGER,
        grade TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

cursor.execute('''
    CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT,
        FOREIGN KEY(student_id) REFERENCES students(user_id)
    )
''')

cursor.execute('''
    CREATE TABLE grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        score INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(user_id)
    )
''')

cursor.execute('''
    CREATE TABLE communication (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        date TEXT
    )
''')

conn.commit()

# --- FUNCTIONS ---

def register_user(name, role):
    cursor.execute("INSERT INTO users (name, role) VALUES (?, ?)", (name, role))
    user_id = cursor.lastrowid
    conn.commit()
    print(f"\n✅ {role} '{name}' registered successfully with ID: {user_id}")
    return user_id

def is_registered(name, role=None):
    if role:
        cursor.execute("SELECT id FROM users WHERE name=? AND role=?", (name, role))
    else:
        cursor.execute("SELECT id, role FROM users WHERE name=?", (name,))
    return cursor.fetchone()

def register_student(name, age, grade):
    user_id = register_user(name, "Student")
    cursor.execute("INSERT INTO students (user_id, age, grade) VALUES (?, ?, ?)", (user_id, age, grade))
    conn.commit()
    print(f"🧑‍🎓 Student '{name}' added to student table.")

def view_all_users(role=None):
    if role:
        cursor.execute("SELECT * FROM users WHERE role=?", (role,))
    else:
        cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    print(f"\n📋 All {role + 's' if role else 'Users'}:")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Role: {row[2]}")

def mark_attendance_for_all():
    cursor.execute("SELECT students.user_id, users.name FROM students JOIN users ON students.user_id = users.id")
    students = cursor.fetchall()
    today = datetime.date.today().isoformat()
    print("\n📅 Marking attendance for all students:")
    for sid, name in students:
        status = input(f"Is {name} (ID {sid}) present? (Present/Absent): ").strip().capitalize()
        if status not in ['Present', 'Absent']:
            status = "Absent"
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (sid, today, status))
    conn.commit()
    print("\n✅ Attendance recorded.")

def assign_grades_loop():
    cursor.execute("SELECT students.user_id, users.name FROM students JOIN users ON students.user_id = users.id")
    students = cursor.fetchall()
    num_subjects = int(input("How many subjects for all students? "))
    subjects = []
    for i in range(num_subjects):
        subjects.append(input(f"Enter name for subject {i+1}: "))
    for sid, name in students:
        print(f"\nEntering marks for {name} (ID {sid}):")
        for subject in subjects:
            score = int(input(f"Score for {subject}: "))
            cursor.execute("INSERT INTO grades (student_id, subject, score) VALUES (?, ?, ?)", (sid, subject, score))
    conn.commit()
    print("\n✅ Grades recorded.")

def send_message(sender, receiver, message):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO communication (sender, receiver, message, date) VALUES (?, ?, ?, ?)", (sender, receiver, message, date))
    conn.commit()
    print(f"\n📨 Message sent from {sender} to {receiver}.")

def view_messages(user_name):
    cursor.execute("SELECT * FROM communication WHERE receiver=?", (user_name,))
    rows = cursor.fetchall()
    if not rows:
        print(f"\n📭 No messages found for {user_name}.")
    else:
        print(f"\n📬 Messages for {user_name}:")
        for row in rows:
            print(f"From: {row[1]}, Date: {row[4]}\nMessage: {row[3]}\n{'-' * 30}")

def view_sent_messages(sender_name):
    cursor.execute("SELECT * FROM communication WHERE sender=?", (sender_name,))
    rows = cursor.fetchall()
    print(f"\n📤 Messages sent by {sender_name}:")
    for row in rows:
        print(f"To: {row[2]}, Date: {row[4]}\nMessage: {row[3]}\n{'-' * 30}")

def export_users(role):
    filename = f"{role.lower()}s_export.csv"
    cursor.execute("SELECT * FROM users WHERE role=?", (role,))
    data = cursor.fetchall()
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Role"])
        writer.writerows(data)
    print(f"\n📁 {role}s exported to: {filename}")

def view_all_messages():
    cursor.execute("SELECT * FROM communication")
    messages = cursor.fetchall()
    print("\n📨 All Messages:")
    for msg in messages:
        print(f"From: {msg[1]} To: {msg[2]} Date: {msg[4]}\nMessage: {msg[3]}\n{'-'*30}")

# --- LOGIN & MENU ---

def main():
    while True:
        print("👋 Welcome to the Student Management System")

        name = input("Enter your name: ")
        existing_user = is_registered(name)

        if existing_user:
            print(f"\n👤 User '{name}' already registered as {existing_user[1]}.")
            is_new = input("Are you a new user with the same name but different role? (yes/no): ").strip().lower()
            if is_new == 'yes':
                role = input("Enter your new role (Student / Teacher / Parent / Admin): ").capitalize()
                user_id = register_user(name, role)
            else:
                user_id = existing_user[0]
                role = existing_user[1]
        else:
            role = input("Enter your role (Student / Teacher / Parent / Admin): ").capitalize()
            if role not in ['Student', 'Teacher', 'Parent', 'Admin']:
                print("❌ Invalid role. Exiting.")
                return
            user_id = register_user(name, role)

        while True:
            print(f"\n🔸 MENU ({role}) 🔸")
            if role == "Teacher":
                print("1. Register New Student")
                print("2. View All Students")
                print("3. Mark Attendance for All")
                print("4. Assign Grades to All Students")
                print("5. Send Message")
                print("6. Export Students CSV")
                print("7. View Sent Messages")
            elif role == "Student":
                print("1. View Messages")
            elif role == "Parent":
                print("1. View Messages")
                print("2. Send Message to Teacher")
            elif role == "Admin":
                print("1. View All Messages")
                print("2. Export Students")
                print("3. Export Teachers")
                print("4. Export Parents")
            print("9. Logout")

            choice = input("Enter your choice: ")

            if role == "Teacher":
                if choice == "1":
                    sname = input("Student name: ")
                    age = int(input("Student age: "))
                    grade = input("Student grade: ")
                    register_student(sname, age, grade)
                elif choice == "2":
                    view_all_users("Student")
                elif choice == "3":
                    mark_attendance_for_all()
                elif choice == "4":
                    assign_grades_loop()
                elif choice == "5":
                    print("Send message to:")
                    print("1. Single Student")
                    print("2. Single Parent")
                    print("3. Group of Students")
                    print("4. Group of Parents")
                    opt = input("Choice: ")
                    if opt == "1":
                        receiver = input("Student name: ")
                        msg = input("Enter message: ")
                        send_message(name, receiver, msg)
                    elif opt == "2":
                        receiver = input("Parent name: ")
                        msg = input("Enter message: ")
                        send_message(name, receiver, msg)
                    elif opt == "3":
                        cursor.execute("SELECT name FROM users WHERE role='Student'")
                        msg = input("Enter group message to Students: ")
                        for (receiver,) in cursor.fetchall():
                            send_message(name, receiver, msg)
                    elif opt == "4":
                        cursor.execute("SELECT name FROM users WHERE role='Parent'")
                        msg = input("Enter group message to Parents: ")
                        for (receiver,) in cursor.fetchall():
                            send_message(name, receiver, msg)
                elif choice == "6":
                    export_users("Student")
                elif choice == "7":
                    view_sent_messages(name)
                elif choice == "9":
                    again = input("Logout from system or just current role? (system/role): ").strip().lower()
                    if again == "system":
                        print(f"🔒 Logged out permanently.\n")
                        return
                    else:
                        print(f"🔒 Logged out from {role} role.")
                        break

            elif role == "Student":
                if choice == "1":
                    view_messages(name)
                elif choice == "9":
                    again = input("Logout from system or just current role? (system/role): ").strip().lower()
                    if again == "system":
                        print(f"🔒 Logged out permanently.\n")
                        return
                    else:
                        print(f"🔒 Logged out from {role} role.")
                        break

            elif role == "Parent":
                if choice == "1":
                    view_messages(name)
                elif choice == "2":
                    receiver = input("Send message to Teacher name: ")
                    msg = input("Enter message: ")
                    send_message(name, receiver, msg)
                elif choice == "9":
                    again = input("Logout from system or just current role? (system/role): ").strip().lower()
                    if again == "system":
                        print(f"🔒 Logged out permanently.\n")
                        return
                    else:
                        print(f"🔒 Logged out from {role} role.")
                        break

            elif role == "Admin":
                if choice == "1":
                    view_all_messages()
                elif choice == "2":
                    export_users("Student")
                elif choice == "3":
                    export_users("Teacher")
                elif choice == "4":
                    export_users("Parent")
                elif choice == "9":
                    again = input("Logout from system or just current role? (system/role): ").strip().lower()
                    if again == "system":
                        print(f"🔒 Logged out permanently.\n")
                        return
                    else:
                        print(f"🔒 Logged out from {role} role.")
                        break

main()