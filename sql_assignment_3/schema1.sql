create database student;

use student;

CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    subject VARCHAR(30),
    marks INT,
    city VARCHAR(30),
    admission_date DATE,
    attendance_percentage INT
);

INSERT INTO students VALUES
(1, 'Ahmed', 'Math', 78, 'Lahore', '2023-01-15', 92),
(2, 'Ayesha', 'Science', 65, 'Karachi', '2023-01-18', 88),
(3, 'Bilal', 'Math', 45, 'Lahore', '2023-02-01', 70),
(4, 'Sana', 'English', 89, 'Islamabad', '2023-01-20', 95),
(5, 'Hassan', 'Science', NULL, 'Karachi', '2023-03-05', 60),
(6, 'Mariam', 'Math', 92, 'Lahore', '2023-01-10', 98),
(7, 'Usman', 'English', 55, 'Multan', '2023-02-14', 75),
(8, 'Zara', 'Science', 70, 'Islamabad', '2023-01-25', 85),
(9, 'Ahsan', 'Math', NULL, 'Karachi', '2023-04-02', 50),
(10, 'Nida', 'English', 60, 'Lahore', '2023-02-20', 80);

-- Get everything about all students
select * from students;

-- Just names and marks for the high scorers (above 70)
select name,marks from students where marks > 70;

-- What subjects do we actually teach? No repeats please
select distinct(subject) from students;

-- Find all students whose name starts with A
SELECT * FROM students WHERE name LIKE 'A%';

-- Who joined after January 20, 2023?
select * from students where admission_date > "2023-01-20";

-- Catch anyone with missing marks
select * from students where marks is null;

-- How many students do we have in total?
select count(name) as total_student from students;

-- What's the average score looking like?
select avg(marks) as avg_marks from students;

-- Best and worst scores in one go
select max(marks) as max_marks,min(marks) as min_marks from students;

-- Rank everyone from top scorer downward
SELECT * FROM students ORDER BY marks desc;
