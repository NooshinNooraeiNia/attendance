from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import os
import cv2
from face_recognition_module import FaceRecognitionThread


app = Flask(__name__)

DATABASE_FILE = 'info.db'
SCHEMA_FILE = 'schema.sql'

def init_db():
    with app.app_context():
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Read and execute the schema.sql script
        with open(SCHEMA_FILE, 'r') as schema_file:
            cursor.executescript(schema_file.read())

        conn.commit()
        conn.close()
        print("Database initialized.")

# Initialize the database (call this only once)
init_db()

def insert_student(student_no, name, image_path):
    print(image_path)
    name = name.upper()
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO students (student_no, student_name, image_path)
            VALUES (?, ?, ?)
        ''', (student_no, name, image_path))

        student_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return student_id
    except Exception as e:
        print(f"Error inserting student: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/attendance')
def attendance():
    init_db()
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return render_template('attendance.html', students=students)

@app.route('/start_recognition')
def start_recognition():
    FaceRecognitionThread()
    return 'Face recognition started!'

@app.route('/add_show_student')
def add_show_student():
    init_db()
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return render_template('/add_show_student.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    init_db()
    student_no = request.form.get('student_no')
    name = request.form.get('name')

    if not student_no or not name:
        return redirect(url_for('add_show_student'))

    image_folder = os.path.join(os.getcwd(), "static/student_images")
    os.makedirs(image_folder, exist_ok=True)

    image_filename = f"{student_no}_{name.upper()}.jpg"
    destination_path = os.path.join(image_folder, image_filename)

    if 'image' in request.files:
        image_file = request.files['image']
        image_file.save(destination_path)

    inserted_id = insert_student(student_no, name, destination_path)

    if inserted_id is not None:
        return redirect(url_for('add_show_student'))
    else:
        return redirect(url_for('add_show_student'))
    

@app.route('/drop_students_table')
def drop_students_table():
    with app.app_context():
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS students')
        conn.commit()
        conn.close()
    return "Students table dropped successfully!"

if __name__ == '__main__':
    app.run(debug=True)
