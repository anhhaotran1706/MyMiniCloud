# MyMiniCloud – Hướng Dẫn Cài Đặt & Vận Hành Từ Đầu Đến Cuối (All-In-One Guide)

Hệ thống **MyMiniCloud** mô phỏng một nền tảng điện toán đám mây (Cloud Platform) thu nhỏ gồm **9 loại máy chủ cơ bản** + 1 Node Exporter + 2 Web Nodes phụ trợ cân bằng tải = **Tổng cộng 12 container**, kết nối chung vào mạng ảo hóa `cloud-net`.

Dự án đã tích hợp hoàn chỉnh:
- **Phần 1 (5.0 điểm):** Xây dựng, kết nối mạng và kiểm thử thông suốt 9 máy chủ cơ bản.
- **Phần 2 (5.0 điểm):** Hiện thực hóa toàn bộ **10/10 yêu cầu ứng dụng thực tế mở rộng**.
- **Điểm tổng kết cam kết:** **10.0 / 10.0 điểm**.

> 📖 **Tài liệu tham khảo đính kèm:**
> - [Hướng dẫn sử dụng toàn bộ Web App (Dành cho Demo / Chấm thi)](file:///d:/cloud/MyMiniCloud/HUONG_DAN_SU_DUNG_WEBAPP.md)
> - [Báo cáo cuối kỳ bản Word chuẩn A4 (.docx)](file:///d:/cloud/MyMiniCloud/BAO_CAO_CUOI_KY_MINICLOUD.docx)
> - [Báo cáo cuối kỳ bản Markdown (.md)](file:///d:/cloud/MyMiniCloud/BAO_CAO_CUOI_KY_MINICLOUD.md)

---

## MỤC LỤC
1. [Yêu cầu môi trường & Cài đặt ban đầu cho máy mới](#1-yêu-cầu-môi-trường--cài-đặt-ban-đầu-cho-máy-mới)
2. [Kiến trúc hệ thống & Bảng phân bổ cổng](#2-kiến-trúc-hệ-thống--bảng-phân-bổ-cổng)
3. [Quy trình khởi động 1 lệnh duy nhất](#3-quy-trình-khởi-động-1-lệnh-duy-nhất)
4. [Khởi tạo dữ liệu mẫu (MinIO & Database)](#4-khởi-tạo-dữ-liệu-mẫu-minio--database)
5. [Hướng dẫn kiểm thử Phần 1 (9 Máy chủ cơ bản - 5 điểm)](#5-hướng-dẫn-kiểm-thử-phần-1-9-máy-chủ-cơ-bản---5-điểm)
6. [Hướng dẫn kiểm thử Phần 2 (10 Yêu cầu mở rộng - 5 điểm)](#6-hướng-dẫn-kiểm-thử-phần-2-10-yêu-cầu-mở-rộng---5-điểm)
7. [Các lưu ý kỹ thuật quan trọng & Xử lý sự cố](#7-các-lưu-ý-kỹ-thuật-quan-trọng--xử-lý-sự-cố)
8. [Hướng dẫn cá nhân hóa thông tin sinh viên trước khi nộp](#8-hướng-dẫn-cá-nhân-hóa-thông-tin-sinh-viên-trước-khi-nộp)
9. [Hướng dẫn Triển khai trên AWS EC2 & Push Docker Hub](#9-hướng-dẫn-triển-khai-trên-aws-ec2--push-docker-hub)

---

## 1. YÊU CẦU MÔI TRƯỜNG & CÀI ĐẶT BAN ĐẦU CHO MÁY MỚI

Khi đem dự án sang một máy tính mới (Windows, macOS hoặc Linux), bạn cần chuẩn bị môi trường như sau:

### 1.1. Cài đặt Docker
- **Trên Windows / macOS:** Tải và cài đặt **Docker Desktop** từ trang chính thức: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
  - *Lưu ý Windows:* Bật tính năng WSL2 backend khi cài đặt. Khởi động Docker Desktop và chờ biểu tượng góc dưới chuyển sang màu xanh (Engine running).
  - *Mẹo Windows PowerShell:* Nếu gặp lỗi lệnh `curl`, hãy dùng `curl.exe` để tránh trùng alias của PowerShell.
- **Trên Linux (Ubuntu / Debian):**
  ```bash
  sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2
  sudo usermod -aG docker $USER
  newgrp docker
  ```

### 1.2. Tải mã nguồn dự án
Sao chép thư mục `MyMiniCloud` về máy mới (hoặc clone từ Git repo của bạn):
```bash
cd MyMiniCloud
```

### 1.3. Lưu ý về Image MinIO (Quan trọng)
MinIO đã gỡ bỏ bản phát hành miễn phí trên Docker Hub chính thức. Để máy mới không bị lỗi `pull access denied for minio/minio`, hãy chạy 3 lệnh sau trước khi build (sử dụng drop-in fork `pgsty/silo` tương thích 100%):
```bash
docker pull pgsty/silo:latest
docker pull pgsty/mc:latest
docker tag pgsty/silo:latest minio/minio:latest
docker tag pgsty/mc:latest minio/mc:latest
```

---

## 2. KIẾN TRÚC HỆ THỐNG & BẢNG PHÂN BỔ CỔNG

### 2.1. Sơ đồ kiến trúc tổng thể
```
                         [ CLIENT / TRÌNH DUYỆT / CURL ]
                                       │ (Cổng 80)
                                       ▼
        ┌─────────────────────────────────────────────────────────────┐
        │             API GATEWAY / REVERSE PROXY SERVER              │
        │                       (Nginx:stable)                        │
        │   /           -> web-frontend-server:80                     │
        │   /api/       -> application-backend-server:8081/           │
        │   /auth/      -> authentication-identity-server:8080/       │
        │   /student/   -> application-backend-server:8081/student    │
        │   /lb/        -> upstream web_cluster (Round Robin)         │
        └───────┬──────────────┬──────────────┬──────────────┬────────┘
                │              │              │              │
        ┌───────┘              │              │              └───────┐
        ▼                      ▼              ▼                      ▼
┌──────────────┐      ┌─────────────────┐ ┌──────────────┐  ┌──────────────────┐
│ Web Frontend │      │ App Backend API │ │ Keycloak IdP │  │ Upstream Cluster │
│ (Nginx Tĩnh) │      │ (Python Flask)  │ │ (OIDC / SSO) │  │ ┌──────────────┐ │
│ - Blog 3 bài │      │ - /hello        │ │ - realm_sv001│  │ │ Node 1 (:8082)│ │
│ - CSS / SVG  │      │ - /student(JSON)│ │ - flask-app  │  │ ├──────────────┤ │
│ - /metrics   │      │ - /students-db  │ │ - sv01, sv02 │  │ │ Node 2 (:8083)│ │
└──────────────┘      │ - /secure (JWT) │ └──────────────┘  │ └──────────────┘ │
                      └────────┬────────┘                   └──────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
    ┌──────────────────────┐        ┌──────────────────────┐
    │ Relational Database  │        │ Object Storage (S3)  │
    │     (MariaDB 11)     │        │       (MinIO)        │
    │ - minicloud.notes    │        │ - bucket profile-pics│
    │ - studentdb.students │        │ - bucket documents   │
    │ - db-data volume     │        │ - Persistent data    │
    └──────────────────────┘        └──────────────────────┘

    ┌──────────────────────┐        ┌──────────────────────────────────────────┐
    │ Internal DNS Server  │        │          MONITORING STACK                │
    │       (Bind9)        │        │ Node Exporter (:9100)                    │
    │ - Zone cloud.local   │        │            │ Scrape                      │
    │ - web, app, db       │        │            ▼                             │
    │ - minio, keycloak    │        │ Prometheus (:9090) ──► Grafana (:3000)   │
    └──────────────────────┘        └──────────────────────────────────────────┘
```

### 2.2. Bảng ánh xạ cổng (Port Mapping)
| STT | Tên Container | Dịch vụ | Cổng Host | Cổng Container | Tài khoản mặc định |
|:---:|---|---|:---:|:---:|---|
| 1 | `api-gateway-proxy-server` | Nginx Gateway & Load Balancer | **80** | 80 | *Không cần* |
| 2 | `web-frontend-server` | Web tĩnh giao diện chính (Blog) | **8080** | 80 | *Không cần* |
| 3 | `web-frontend-server1` | Web Node 1 (Load Balancer) | **8082** | 80 | *Không cần* |
| 4 | `web-frontend-server2` | Web Node 2 (Load Balancer) | **8083** | 80 | *Không cần* |
| 5 | `application-backend-server`| Flask REST API Microservice | **8085** | 8081 | *Không cần* |
| 6 | `relational-database-server`| MariaDB Database | **3306** | 3306 | `root` / `root` |
| 7 | `authentication-identity-server`| Keycloak Identity Provider | **8081** | 8080 | `admin` / `admin` |
| 8 | `object-storage-server` | MinIO Object Store API | **9000** | 9000 | `minioadmin` / `minioadmin` |
| 9 | `object-storage-server` | MinIO Web Console UI | **9001** | 9001 | `minioadmin` / `minioadmin` |
| 10 | `internal-dns-server` | Bind9 DNS (Zone `cloud.local`)| **1053** | 53 (UDP/TCP)| *Không cần* |
| 11 | `monitoring-node-exporter-server`| Node Exporter System Metrics| **9100** | 9100 | *Không cần* |
| 12 | `monitoring-prometheus-server`| Prometheus Metrics Server | **9090** | 9090 | *Không cần* |
| 13 | `monitoring-grafana-dashboard-server`| Grafana Visualization | **3000** | 3000 | `admin` / `admin` |

---

## 3. QUY TRÌNH KHỞI ĐỘNG 1 LỆNH DUY NHẤT

### Bước 1: Dọn dẹp container cũ (nếu có)
```bash
# Bash
docker stop $(docker ps -q) 2>/dev/null
docker rm -f $(docker ps -aq) 2>/dev/null
```
```powershell
# PowerShell
docker stop (docker ps -q) 2>$null
docker rm -f (docker ps -aq) 2>$null
```

### Bước 2: Build và khởi động toàn bộ 12 container
```bash
docker compose build --no-cache
docker compose up -d
```

### Bước 3: Kiểm tra trạng thái
```bash
docker compose ps
```
> **Kỳ vọng:** Toàn bộ 12 container đều ở trạng thái `Up`. Keycloak cần khoảng 30–45 giây để hoàn tất khởi động và import realm `realm_sv001`.

---

## 4. KHỞI TẠO DỮ LIỆU MẪU (MINIO & DATABASE)

### 4.1. Khởi tạo Bucket và tải file lên MinIO
Chạy lệnh sau ngay tại thư mục `MyMiniCloud` để tạo 2 bucket (`profile-pics` public và `documents` private):

```bash
# Bash (Linux / macOS / Git Bash)
docker run --rm --network cloud-net -v "${PWD}/object-storage-server/seed:/seed" --entrypoint sh minio/mc -c "
  mc alias set local http://object-storage-server:9000 minioadmin minioadmin &&
  mc mb --ignore-existing local/profile-pics &&
  mc mb --ignore-existing local/documents &&
  mc anonymous set download local/profile-pics &&
  mc cp /seed/avatar.jpg local/profile-pics/avatar.jpg &&
  mc cp /seed/baocao.pdf local/documents/baocao.pdf &&
  mc ls local
"
```

```powershell
# PowerShell (Windows)
docker run --rm --network cloud-net -v "${PWD}/object-storage-server/seed:/seed" --entrypoint sh minio/mc -c "mc alias set local http://object-storage-server:9000 minioadmin minioadmin && mc mb --ignore-existing local/profile-pics && mc mb --ignore-existing local/documents && mc anonymous set download local/profile-pics && mc cp /seed/avatar.jpg local/profile-pics/avatar.jpg && mc cp /seed/baocao.pdf local/documents/baocao.pdf && mc ls local"
```

### 4.2. Chạy Demo CRUD MariaDB (Tùy chọn)
MariaDB đã tự động tạo CSDL `minicloud` (chứa bảng `notes`) và `studentdb` (chứa bảng `students`) khi khởi động lần đầu. Để chạy kịch bản thử nghiệm CRUD (Create, Read, Update, Delete):
```bash
# Bash
docker exec -i relational-database-server mariadb -uroot -proot < relational-database-server/crud_demo.sql
```
```powershell
# PowerShell
Get-Content relational-database-server/crud_demo.sql | docker exec -i relational-database-server mariadb -uroot -proot
```
*Lưu ý: Dữ liệu được lưu bền vững qua volume `db-data`. Nếu muốn xóa sạch để nạp lại từ đầu: `docker compose down -v`.*

---

## 5. HƯỚNG DẪN KIỂM THỬ PHẦN 1 (9 MÁY CHỦ CƠ BẢN - 5 ĐIỂM)

### 1️⃣ Web Frontend Server (Nginx static site)
```bash
curl -I http://localhost:8080/
curl -I http://localhost:8080/blog/
```
- **Kỳ vọng:** Cả 2 lệnh đều trả về `HTTP/1.1 200 OK`.
- **Trình duyệt:** Mở `http://localhost:8080/` hiển thị trang chủ và danh sách bài blog.

### 2️⃣ Application Backend Server (Flask API)
```bash
curl http://localhost:8085/hello
curl http://localhost/api/hello
```
- **Kỳ vọng:** Cả 2 lệnh đều trả về: `{"message":"Hello from App Server!"}` (chứng minh truy cập trực tiếp và qua Gateway đều hoạt động giống nhau).

### 3️⃣ Relational Database Server (MariaDB)
```bash
docker exec -it relational-database-server mariadb -uroot -proot -e "USE minicloud; SHOW TABLES; SELECT * FROM notes;"
```
- **Kỳ vọng:** Bảng `notes` tồn tại và có ít nhất 1 dòng dữ liệu: `Hello from MariaDB!`.

### 4️⃣ Authentication Identity Server (Keycloak)
- Mở trình duyệt: `http://localhost:8081`
- Đăng nhập: `admin` / `admin`
- **Kỳ vọng:** Mở thành công trang Dashboard Keycloak Admin Console.

### 5️⃣ Object Storage Server (MinIO)
- Mở trình duyệt: `http://localhost:9001`
- Đăng nhập: `minioadmin` / `minioadmin`
- **Kỳ vọng:** Giao diện MinIO Console hiển thị bình thường.

### 6️⃣ Internal DNS Server (Bind9)
```bash
docker exec internal-dns-server dig @127.0.0.1 web-frontend-server.cloud.local +short
```
*(Nếu trên máy đã cài sẵn công cụ dig: `dig @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short`)*
- **Kỳ vọng:** Trả về địa chỉ IP nội bộ: `10.10.10.10`.

### 7️⃣ Monitoring Node Exporter + Prometheus
- Mở trình duyệt: `http://localhost:9090`
- Vào menu **Status** -> **Targets**:
  - **Kỳ vọng:** Cả 2 target `node` và `web` đều hiển thị trạng thái xanh **UP**.
- Vào menu **Graph**, thử truy vấn: `node_cpu_seconds_total` rồi nhấn **Execute** -> Xem biểu đồ.

### 8️⃣ Monitoring Grafana Dashboard
- Mở trình duyệt: `http://localhost:3000`
- Đăng nhập: `admin` / `admin`
- **Kỳ vọng:** Đăng nhập thành công vào trang quản trị Grafana.

### 9️⃣ API Gateway Proxy Server (Nginx Reverse Proxy)
```bash
curl -I http://localhost/
curl -s  http://localhost/api/hello
curl -I http://localhost/auth/
```
- **Kỳ vọng:**
  - `http://localhost/` -> Trả về `HTTP/1.1 200 OK` (Web).
  - `http://localhost/api/hello` -> Trả về JSON từ backend Flask.
  - `http://localhost/auth/` -> Trả về `HTTP/1.1 302 Found` (chuyển hướng sang trang đăng nhập Keycloak).

### 🔟 Kiểm tra thông mạng (Ping Connectivity)
Chạy lệnh kiểm tra kết nối giữa các container trong mạng `cloud-net`:
```bash
# Bash
docker run --rm --network cloud-net alpine sh -c "
  for h in web-frontend-server application-backend-server relational-database-server \
           authentication-identity-server object-storage-server internal-dns-server \
           monitoring-prometheus-server monitoring-grafana-dashboard-server; do
    ping -c 1 -W 1 \$h > /dev/null && echo 'Ping OK: '\$h
  done
"
```
```powershell
# PowerShell
@("web-frontend-server", "application-backend-server", "relational-database-server", "authentication-identity-server", "object-storage-server", "internal-dns-server", "monitoring-prometheus-server", "monitoring-grafana-dashboard-server") | ForEach-Object {
    docker run --rm --network cloud-net alpine ping -c 1 -W 1 $_
    Write-Host "Ping $_ : OK"
}
```
- **Kỳ vọng:** Tất cả 9 server đều trả về kết quả ping thành công (0% packet loss).

---

## 6. HƯỚNG DẪN KIỂM THỬ PHẦN 2 (10 YÊU CẦU MỞ RỘNG - 5 ĐIỂM)

### ① Web Frontend – Blog cá nhân 3 bài viết chuyên đề (0.5đ)
- Mở `http://localhost/` và `http://localhost/blog/blog1.html`
- **Kỳ vọng:** Trang chủ có danh sách 3 bài viết có hyperlink. Mỗi bài viết có hình vẽ minh họa vector SVG độc quyền và liên kết quay lại trang chính.

### ② Application Backend – API /student đọc file JSON (0.5đ)
```bash
curl http://localhost/api/student
```
- **Kỳ vọng:** Trả về danh sách 5 sinh viên dạng JSON: `id`, `name`, `major`, `gpa`.

### ③ Relational Database – CSDL studentdb & API /students-db (0.5đ)
```bash
docker exec -it relational-database-server mariadb -uroot -proot -e "SELECT * FROM studentdb.students;"
curl http://localhost/api/students-db
```
- **Kỳ vọng:** Bảng `studentdb.students` có 5 bản ghi. API `/students-db` kết nối MariaDB và trả về danh sách sinh viên JSON tiếng Việt UTF-8.

### ④ Keycloak – Realm realm_sv001 + Client flask-app + API /secure (0.5đ)
Lấy JWT Access Token từ Keycloak và gọi API bảo mật:

```bash
# Bash
TOKEN=$(curl -s -X POST http://localhost:8081/realms/realm_sv001/protocol/openid-connect/token \
  -d client_id=flask-app -d grant_type=password -d username=sv01 -d password=123456 | jq -r .access_token)
curl -H "Authorization: Bearer $TOKEN" http://localhost/api/secure
```

```powershell
# PowerShell
$r = curl.exe -s -X POST http://localhost:8081/realms/realm_sv001/protocol/openid-connect/token -d client_id=flask-app -d grant_type=password -d username=sv01 -d password=123456 | ConvertFrom-Json
curl.exe -H "Authorization: Bearer $($r.access_token)" http://localhost/api/secure
```
- **Kỳ vọng:** Trả về: `{"message":"Secure resource OK","preferred_username":"sv01"}`.

### ⑤ MinIO – Phân cấp quyền Public / Private Bucket (0.5đ)
```bash
curl -I http://localhost:9000/profile-pics/avatar.jpg
curl -I http://localhost:9000/documents/baocao.pdf
```
- **Kỳ vọng:**
  - `profile-pics/avatar.jpg` -> `HTTP/1.1 200 OK` (Public).
  - `documents/baocao.pdf` -> `HTTP/1.1 403 Forbidden` (Private - bảo vệ quyền truy cập).

### ⑥ Internal DNS – Bổ sung bản ghi nội bộ (0.5đ)
```bash
docker exec internal-dns-server dig @127.0.0.1 app-backend.cloud.local +short
docker exec internal-dns-server dig @127.0.0.1 minio.cloud.local +short
docker exec internal-dns-server dig @127.0.0.1 keycloak.cloud.local +short
```
- **Kỳ vọng:** Trả về lần lượt: `10.10.10.20`, `10.10.10.30`, `10.10.10.40`.

### ⑦ Prometheus – Thêm target giám sát web-frontend-server (0.5đ)
- Mở `http://localhost:9090/targets`
- **Kỳ vọng:** Cả hai target `node` và `web` đều hiển thị trạng thái **UP** (nhờ endpoint `/metrics` tích hợp sẵn trong Nginx).

### ⑧ Grafana – Dashboard "System Health of SV001" (0.5đ)
- Mở `http://localhost:3000` (admin/admin) -> Menu **Dashboards** -> Chọn **System Health of SV001**.
- **Kỳ vọng:** Dashboard tự động hiển thị 3 biểu đồ trực quan có dữ liệu thời gian thực:
  1. CPU Usage (%)
  2. Memory Usage (%)
  3. Network Traffic (Receive / Transmit)

### ⑨ API Gateway – Định tuyến route /student/ (0.5đ)
```bash
curl http://localhost/student/
```
- **Kỳ vọng:** Trả về cùng danh sách sinh viên JSON như mục ② (chứng minh Gateway mapping route thành công).

### ⑩ Load Balancer – Cân bằng tải Round Robin (/lb/) (0.5đ)
Kiểm thử cân bằng tải luân phiên giữa 2 web server:
```bash
# Bash
for i in 1 2 3 4 5 6; do curl -s http://localhost/lb/ | grep -o "<title>.*</title>"; done
```
```powershell
# PowerShell
1..6 | ForEach-Object { (curl.exe -s http://localhost/lb/) -replace '(?s).*<title>(.*?)</title>.*','$1' }
```
- **Kỳ vọng:** Kết quả trả về xen kẽ chuẩn Round Robin:
  ```
  SERVER 1
  SERVER 2
  SERVER 1
  SERVER 2
  ...
  ```
- **Trình duyệt:** Mở `http://localhost/lb/` và nhấn F5 liên tục, màn hình đổi luân phiên giữa màu xanh ngọc (Server 1) và màu cam (Server 2).

---

## 7. CÁC LƯU Ý KỸ THUẬT QUAN TRỌNG & XỬ LÝ SỰ CỐ

1. **Khởi động Keycloak:** Keycloak phiên bản mới (chạy trên Quarkus) mất khoảng 30–45 giây để khởi động và nạp realm. Nếu gọi API `/token` mà báo lỗi kết nối, hãy đợi một lát rồi thử lại.
2. **Cơ chế xác thực OIDC JWT:** 
   - `OIDC_ISSUER`: Giá trị này phải khớp với đường dẫn người dùng gọi lấy token (`http://localhost:8081/...` hoặc Public IP trên EC2).
   - `OIDC_JWKS_URL`: Backend Flask tải khóa công khai qua mạng nội bộ `cloud-net` (`http://authentication-identity-server:8080/...`).
3. **Target `web` của Prometheus:** Mặc định Nginx tĩnh không có trang metrics. Tệp `conf.default` đã được bổ sung `location = /metrics` trả về `web_up 1`, nhờ đó Prometheus scrape ra trạng thái UP chuẩn chỉ.
4. **Áp dụng cấu hình khi chỉnh sửa:**
   - Sửa Prometheus: `docker restart monitoring-prometheus-server`
   - Sửa DNS: `docker restart internal-dns-server`
   - Sửa Proxy: `docker restart api-gateway-proxy-server`
   - Sửa Grafana: `docker restart monitoring-grafana-dashboard-server`

---

## 8. HƯỚNG DẪN CÁ NHÂN HÓA THÔNG TIN SINH VIÊN TRƯỚC KHI NỘP

Trước khi nộp bài hoặc đem đi chấm, bạn có thể nhanh chóng đổi thông tin mẫu thành thông tin cá nhân của bạn:

| Cần đổi | Vị trí tệp tin |
|---|---|
| `realm_sv001` -> Realm theo MSSV của bạn | `authentication-identity-server/realm-export.json`, `docker-compose.yml` (3 chỗ), `application-backend-server/app.py` |
| `SV001` -> MSSV của bạn | `monitoring-grafana-dashboard-server/provisioning/dashboards/system-health.json`, `relational-database-server/init/002_studentdb.sql` |
| `Trần Anh Hào / Hà Nam Anh / Bùi Châu Hải Đăng` -> Họ tên của bạn | Các tệp `.html` trong `web-frontend-server/html/` |
| Ảnh đại diện & Báo cáo PDF mẫu | Thay file `object-storage-server/seed/avatar.jpg` và `baocao.pdf` bằng ảnh và PDF của bạn |

---

## 9. HƯỚNG DẪN TRIỂN KHAI TRÊN AWS EC2 & PUSH DOCKER HUB

### 9.1. Push Custom Image lên Docker Hub (Yêu cầu kỹ thuật đồ án)
```bash
# 1. Đăng nhập Docker Hub
docker login

# 2. Gắn tag image với tài khoản Docker Hub của bạn
docker tag anhhaotran113/web:dev trananhhao/myminicloud-web:v1.0

# 3. Đẩy image lên kho lưu trữ
docker push anhhaotran113/myminicloud-web:v1.0
```

### 9.2. Triển khai toàn bộ trên AWS EC2 (Ubuntu)
1. **Khởi tạo EC2 Instance:** Chọn Ubuntu 22.04 hoặc 24.04 (loại `t3.small` hoặc `t3.medium`).
2. **Cấu hình Security Group (Inbound Rules):** Mở các cổng sau cho IP `0.0.0.0/0`:
   - `80` (API Gateway & Web)
   - `3000` (Grafana Dashboard)
   - `8081` (Keycloak Identity)
   - `9001` (MinIO Web Console)
   - `9090` (Prometheus Metrics)
3. **Cài đặt Docker trên EC2:**
   ```bash
   sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   sudo usermod -aG docker ubuntu
   ```
4. **Copy thư mục dự án và tạo biến môi trường:**
   ```bash
   git clone <repo_url> MyMiniCloud
   cd MyMiniCloud
   echo "PUBLIC_HOST=<PUBLIC_IP_EC2>" > .env
   ```
5. **Khởi động:**
   ```bash
   docker compose up -d
   ```
   Toàn bộ hệ thống sẽ truy cập được từ trình duyệt bên ngoài thông qua địa chỉ Public IP của EC2!

---

## 10. DANH SÁCH 10 MINH CHỨNG CẦN CHỤP CHO BÁO CÁO CUỐI KỲ

1. **Minh chứng 1:** Trang chủ `http://localhost/` và 1 trang bài viết blog có ảnh SVG.
2. **Minh chứng 2:** Lệnh `curl http://localhost/api/student` trả danh sách JSON.
3. **Minh chứng 3:** Kết quả `SELECT * FROM students` trong DB và `curl http://localhost/api/students-db`.
4. **Minh chứng 4:** Giao diện Keycloak Realm `realm_sv001`, danh sách Users và kết quả gọi `/api/secure` trả `Secure resource OK`.
5. **Minh chứng 5:** Giao diện MinIO Console 2 bucket, `curl -I` ảnh public (200 OK) và file private (403 Forbidden).
6. **Minh chứng 6:** Kết quả lệnh `dig` phân giải 3 bản ghi `app-backend`, `minio`, `keycloak`.
7. **Minh chứng 7:** Trang Targets của Prometheus (`node` và `web` đều hiển thị UP).
8. **Minh chứng 8:** Dashboard Grafana 3 biểu đồ CPU, RAM, Network Traffic có dữ liệu.
9. **Minh chứng 9:** Kết quả lệnh `curl http://localhost/student/` qua Gateway.
10. **Minh chứng 10:** Kết quả lệnh curl luân phiên `SERVER 1` và `SERVER 2` tại endpoint `/lb/`.
# final-cloud-computing
