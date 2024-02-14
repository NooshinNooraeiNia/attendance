-- schema.sql

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_no TEXT UNIQUE,
    student_name TEXT,
    image_path TEXT,
    present TEXT
);
