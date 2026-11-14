-- [P2-3] CSDL studentdb + bảng students (chạy tự động lần khởi tạo đầu tiên)
CREATE DATABASE IF NOT EXISTS studentdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE studentdb;

CREATE TABLE IF NOT EXISTS students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(10),
  fullname VARCHAR(100),
  dob DATE,
  major VARCHAR(50)
);

INSERT INTO students (student_id, fullname, dob, major) VALUES
  ('SV001', 'Trần Anh Hào',  '2004-03-12', 'Khoa học máy tính'),
  ('SV002', 'Trần Thị Bình',  '2004-07-25', 'Kỹ thuật phần mềm'),
  ('SV003', 'Lê Hoàng Cường', '2003-11-02', 'Mạng máy tính'),
  ('SV004', 'Phạm Minh Dũng', '2004-01-18', 'Khoa học dữ liệu'),
  ('SV005', 'Võ Thu Hà',      '2004-09-30', 'An toàn thông tin');
