-- [P2-3] Demo CRUD cho báo cáo. Chạy:
--   docker exec -i relational-database-server mariadb -uroot -proot < relational-database-server/crud_demo.sql
USE studentdb;

-- READ
SELECT * FROM students;
SELECT fullname, major FROM students WHERE major LIKE '%máy tính%';

-- CREATE
INSERT INTO students (student_id, fullname, dob, major)
VALUES ('SV006', 'Đỗ Quang Huy', '2004-05-06', 'Trí tuệ nhân tạo');

-- UPDATE
UPDATE students SET major = 'Kỹ thuật phần mềm' WHERE student_id = 'SV003';
SELECT student_id, fullname, major FROM students WHERE student_id = 'SV003';

-- DELETE
DELETE FROM students WHERE student_id = 'SV006';
SELECT COUNT(*) AS total_students FROM students;
