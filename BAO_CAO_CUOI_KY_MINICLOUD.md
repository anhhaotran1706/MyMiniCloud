# BÁO CÁO ĐỒ ÁN CUỐI KỲ: XÂY DỰNG MÔ PHỎNG HỆ THỐNG MINICLOUD CƠ BẢN (MYMINICLOUD)

- **Học phần:** Điện toán đám mây & Ứng dụng (Cloud Computing)
- **Sinh viên thực hiện:** Nguyễn Văn A
- **Mã số sinh viên (MSSV):** SV001
- **Kết quả thực hiện:** Hoàn thành **10/10 phần cơ bản** (5.0 điểm) + **10/10 phần mở rộng** (5.0 điểm) = **10.0 / 10.0 điểm tối đa**.
- **Tệp báo cáo Word:** [BAO_CAO_CUOI_KY_MINICLOUD.docx](file:///d:/cloud/MyMiniCloud/BAO_CAO_CUOI_KY_MINICLOUD.docx)

---

## MỤC LỤC
1. [Chương 1. Giới thiệu & Mục tiêu](#chương-1-giới-thiệu--mục-tiêu)
2. [Chương 2. Kiến trúc & Sơ đồ hệ thống](#chương-2-kiến-trúc--sơ-đồ-hệ-thống)
3. [Chương 3. Cấu hình & Dockerfile chi tiết](#chương-3-cấu-hình--dockerfile-chi-tiết)
4. [Chương 4. Demo & Kiểm thử thực tế](#chương-4-demo--kiểm-thử-thực-tế)
5. [Chương 5. Đánh giá & Phân tích](#chương-5-đánh-giá--phân-tích)
6. [Phụ lục](#phụ-lục)

---

## CHƯƠNG 1. GIỚI THIỆU & MỤC TIÊU

### 1.1. Mục tiêu
Hệ thống **MyMiniCloud** mô phỏng một nền tảng Cloud Platform hoàn chỉnh gồm 9 loại máy chủ cơ bản (cùng 1 Node Exporter và 2 Web Nodes phụ trợ cân bằng tải, tổng cộng 12 container). Mỗi dịch vụ chạy trong một container chuyên biệt, giao tiếp an toàn qua mạng ảo hóa nội bộ `cloud-net`, và có thể triển khai tức thì trên máy cá nhân (Localhost) lẫn đám mây công cộng (AWS EC2 Ubuntu).

### 1.2. 9 Loại máy chủ bắt buộc và ánh xạ AWS
| STT | Loại Server | Vai trò & Yêu cầu | Công nghệ / Image | Tương đương trên AWS |
|:---:|---|---|---|---|
| 1 | Web Server | Giao diện web tĩnh, blog cá nhân 3 bài | `nginx:stable` (custom) | AWS S3 Static Web / Amplify |
| 2 | Application Server | Xử lý logic API, JSON, kết nối MariaDB | `python:3.11-alpine` (Flask) | AWS Elastic Beanstalk / ECS |
| 3 | Database Server | Lưu trữ dữ liệu quan hệ, bảng notes & students | `mariadb:11` | Amazon RDS (MariaDB/MySQL) |
| 4 | Authentication Server | Quản lý người dùng, cấp phát token JWT/OIDC | `quay.io/keycloak/keycloak` | Amazon Cognito / IAM |
| 5 | Object Storage Server | Lưu trữ bucket, avatar public & tài liệu private | `minio/minio` (Silo drop-in) | Amazon S3 Object Storage |
| 6 | Internal DNS Server | Phân giải tên miền private zone `cloud.local` | `internetsystemsconsortium/bind9:9.18` | Amazon Route 53 Private Zone |
| 7 | Monitoring Server | Thu thập định kỳ metrics từ node & container | `prom/prometheus:latest` | Amazon CloudWatch / Prometheus |
| 8 | Logging/Visualization | Dashboard trực quan hóa chỉ số hạ tầng | `grafana/grafana:latest` | Amazon Managed Grafana |
| 9 | Reverse Proxy / Gateway | Điểm vào duy nhất cổng 80, cân bằng tải | `nginx:stable` | AWS ALB / API Gateway |

### 1.3. Bảng quy hoạch cổng mạng (Port Mapping)
| Container | Dịch vụ | Cổng Host | Cổng Container | Ghi chú |
|---|---|---|---|---|
| `api-gateway-proxy-server` | Gateway / Reverse Proxy | **80** | 80 | Cổng tiếp nhận chính |
| `web-frontend-server` | Web chính (Blog tĩnh) | 8080 | 80 | Kiểm thử độc lập |
| `web-frontend-server1` | Node 1 Load Balancer | 8082 | 80 | Backend LB cluster |
| `web-frontend-server2` | Node 2 Load Balancer | 8083 | 80 | Backend LB cluster |
| `application-backend-server` | Flask API | 8085 | 8081 | Microservice API |
| `relational-database-server` | MariaDB | 3306 | 3306 | Volume lưu trữ lâu dài |
| `authentication-identity-server` | Keycloak | 8081 | 8080 | Identity Provider |
| `object-storage-server` (API) | MinIO S3 API | 9000 | 9000 | S3 compatible API |
| `object-storage-server` (UI) | MinIO Console | 9001 | 9001 | Giao diện quản trị web |
| `internal-dns-server` | Bind9 DNS | 1053 | 53 (UDP/TCP) | Phân giải tên miền |
| `monitoring-node-exporter-server` | Node Exporter | 9100 | 9100 | Xuất metrics hệ điều hành |
| `monitoring-prometheus-server` | Prometheus Server | 9090 | 9090 | Quản lý scrape targets |
| `monitoring-grafana-dashboard-server` | Grafana Dashboard | 3000 | 3000 | Trực quan hóa PromQL |

---

## CHƯƠNG 2. KIẾN TRÚC & SƠ ĐỒ HỆ THỐNG

### 2.1. Sơ đồ kiến trúc tổng thể
```
                         [ CLIENT TRÌNH DUYỆT / CURL ]
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

### 2.2. Luồng giao tiếp giữa các thành phần
1. **Web Traffic:** Client gọi `GET /` -> Nginx Gateway chuyển tiếp sang `web-frontend-server` -> Trả về giao diện blog cá nhân với CSS và ảnh vector SVG.
2. **REST API Microservice:** Client gọi `GET /api/hello` -> Gateway cắt tiền tố `/api/` -> chuyển hướng `application-backend-server:8081/hello` -> Trả về JSON `{"message":"Hello from App Server!"}`.
3. **Database Integration:** Client gọi `GET /api/students-db` -> Flask kết nối MariaDB `studentdb` -> Truy vấn `SELECT * FROM students` -> chuyển đổi thành JSON UTF-8.
4. **OIDC Single Sign-On:** Client xác thực tại Keycloak để nhận Access Token JWT -> gửi token qua header `Authorization: Bearer <token>` vào `/api/secure` -> Backend tải public key từ JWKS endpoint của Keycloak qua `cloud-net`, giải mã và xác thực user `sv01`.
5. **Cân bằng tải Round Robin:** Yêu cầu đến `/lb/` được Gateway chia đều luân phiên giữa 2 web server: Node 1 (nền xanh) và Node 2 (nền cam).

---

## CHƯƠNG 3. CẤU HÌNH & DOCKERFILE CHI TIẾT

Toàn bộ mã nguồn và cấu hình hệ thống nằm trong thư mục [D:\cloud\MyMiniCloud](file:///d:/cloud/MyMiniCloud).

### 3.1. Web Frontend Server
- **Dockerfile:** [web-frontend-server/Dockerfile](file:///d:/cloud/MyMiniCloud/web-frontend-server/Dockerfile)
- **Nginx Config:** [web-frontend-server/conf.default](file:///d:/cloud/MyMiniCloud/web-frontend-server/conf.default)
- **Giao diện:** [web-frontend-server/html/index.html](file:///d:/cloud/MyMiniCloud/web-frontend-server/html/index.html) và 3 bài viết blog trong `html/blog/`. Có cấu hình `location = /metrics` để Prometheus scrape ra UP.

### 3.2. Application Backend Server
- **Dockerfile:** [application-backend-server/Dockerfile](file:///d:/cloud/MyMiniCloud/application-backend-server/Dockerfile)
- **Source Code Flask:** [application-backend-server/app.py](file:///d:/cloud/MyMiniCloud/application-backend-server/app.py)
- **Dữ liệu JSON sinh viên:** [application-backend-server/students.json](file:///d:/cloud/MyMiniCloud/application-backend-server/students.json)

### 3.3. Relational Database Server
- **Schema cơ bản:** [relational-database-server/init/001_init.sql](file:///d:/cloud/MyMiniCloud/relational-database-server/init/001_init.sql)
- **Schema mở rộng studentdb:** [relational-database-server/init/002_studentdb.sql](file:///d:/cloud/MyMiniCloud/relational-database-server/init/002_studentdb.sql)
- **Kịch bản CRUD:** [relational-database-server/crud_demo.sql](file:///d:/cloud/MyMiniCloud/relational-database-server/crud_demo.sql)

### 3.4. Authentication Identity Server
- **Realm export:** [authentication-identity-server/realm-export.json](file:///d:/cloud/MyMiniCloud/authentication-identity-server/realm-export.json) (chứa realm `realm_sv001`, client `flask-app`, user `sv01` và `sv02`).

### 3.5. Internal DNS Server
- **Named Options:** [internal-dns-server/named.conf.options](file:///d:/cloud/MyMiniCloud/internal-dns-server/named.conf.options)
- **Named Local:** [internal-dns-server/named.conf.local](file:///d:/cloud/MyMiniCloud/internal-dns-server/named.conf.local)
- **Zone File:** [internal-dns-server/db.cloud.local](file:///d:/cloud/MyMiniCloud/internal-dns-server/db.cloud.local)
- **Named Config gốc:** [internal-dns-server/named.conf](file:///d:/cloud/MyMiniCloud/internal-dns-server/named.conf)

### 3.6. Monitoring Stack
- **Prometheus Scrape Config:** [monitoring-prometheus-server/prometheus.yml](file:///d:/cloud/MyMiniCloud/monitoring-prometheus-server/prometheus.yml)
- **Grafana Provisioning:** [monitoring-grafana-dashboard-server/provisioning/](file:///d:/cloud/MyMiniCloud/monitoring-grafana-dashboard-server/provisioning/) với datasource Prometheus tự động và Dashboard `System Health of SV001` (CPU, Memory, Network).

### 3.7. API Gateway & Load Balancer
- **Nginx Config:** [api-gateway-proxy-server/nginx.conf](file:///d:/cloud/MyMiniCloud/api-gateway-proxy-server/nginx.conf)
- **Docker Compose:** [docker-compose.yml](file:///d:/cloud/MyMiniCloud/docker-compose.yml)

---

## CHƯƠNG 4. DEMO & KIỂM THỬ THỰC TẾ

### 4.1. Khởi động toàn hệ thống
```powershell
Set-Location "D:\cloud\MyMiniCloud"
docker compose build --no-cache
docker compose up -d
docker compose ps
```
**Kết quả thực tế:** Toàn bộ 12 container khởi động thành công và đều ở trạng thái `Up`.

### 4.2. Bảng kết quả kiểm thử Phần 1 (Cơ bản - 5 điểm)
| Bài Test | Lệnh kiểm thử | Kết quả thực tế | Trạng thái |
|---|---|---|:---:|
| 1. Web Frontend | `curl -I http://localhost:8080/` | HTTP/1.1 200 OK (Home) | **ĐẠT** |
| | `curl -I http://localhost:8080/blog/` | HTTP/1.1 200 OK (Blog) | **ĐẠT** |
| 2. App Backend | `curl http://localhost:8085/hello` | `{"message":"Hello from App Server!"}` | **ĐẠT** |
| 3. Database | `docker exec relational-database-server mariadb -uroot -proot -e "USE minicloud; SELECT * FROM notes;"` | 1 dòng: `Hello from MariaDB!` | **ĐẠT** |
| 4. Auth Keycloak | `curl -I http://localhost:8081/` | HTTP/1.1 200 OK / 302 Admin Console | **ĐẠT** |
| 5. MinIO Storage | `curl -I http://localhost:9001/` | HTTP/1.1 200 OK MinIO Console | **ĐẠT** |
| 6. DNS Server | `docker exec internal-dns-server dig @127.0.0.1 web-frontend-server.cloud.local +short` | `10.10.10.10` | **ĐẠT** |
| 7. Prometheus | `curl http://localhost:9090/api/v1/targets` | Target `node`: UP, Target `web`: UP | **ĐẠT** |
| 8. Grafana | `curl -I http://localhost:3000/` | HTTP/1.1 302 Found (Login page) | **ĐẠT** |
| 9. Reverse Proxy | `curl -I http://localhost/` | HTTP/1.1 200 OK | **ĐẠT** |
| | `curl http://localhost/api/hello` | `{"message":"Hello from App Server!"}` | **ĐẠT** |
| | `curl -I http://localhost/auth/` | HTTP/1.1 302 Found (chuyển hướng Keycloak) | **ĐẠT** |
| 10. Ping mạng | `docker run --rm --network cloud-net alpine ping -c 1 <container>` | Thành công 100% cả 9 container | **ĐẠT** |

### 4.3. Bảng kết quả kiểm thử Phần 2 (10 Yêu cầu mở rộng - 5 điểm)
| # | Yêu cầu mở rộng | Lệnh / Thao tác kiểm thử | Kết quả thực tế | Điểm |
|:---:|---|---|---|:---:|
| 1 | Blog cá nhân 3 bài | Mở `http://localhost/` và `/blog/blog1.html` | Đầy đủ 3 bài viết, kèm 3 hình vẽ SVG, responsive | 0.5 |
| 2 | API `/student` (JSON) | `curl http://localhost/api/student` | JSON 5 sinh viên (id, name, major, gpa) | 0.5 |
| 3 | CSDL `studentdb` & API | `curl http://localhost/api/students-db` | Đọc 5 sinh viên từ MariaDB, hỗ trợ CRUD | 0.5 |
| 4 | OIDC Token & `/secure` | `curl -X POST .../token` rồi gửi token tới `/secure` | `{"message":"Secure resource OK","preferred_username":"sv01"}` | 0.5 |
| 5 | MinIO Public/Private | `curl -I .../profile-pics/avatar.jpg` và `documents/baocao.pdf` | Avatar: HTTP 200 (public), PDF: HTTP 403 (private) | 0.5 |
| 6 | DNS mở rộng | `dig @127.0.0.1 app-backend.cloud.local` | Phân giải chính xác `10.10.10.20`, `.30`, `.40` | 0.5 |
| 7 | Prometheus Scrape Web | `curl http://localhost:9090/api/v1/targets` | Target `web` UP nhờ endpoint `/metrics` | 0.5 |
| 8 | Dashboard Grafana | Mở `http://localhost:3000` -> Dashboard *System Health of SV001* | 3 panel CPU, Memory, Network hiển thị dữ liệu thực tế | 0.5 |
| 9 | Gateway Route `/student/`| `curl http://localhost/student/` | Định tuyến chính xác đến API backend | 0.5 |
| 10 | Load Balancer Round Robin | `curl -s http://localhost/lb/` (2 lần) | Luân phiên `SERVER 1` (Node 1) và `SERVER 2` (Node 2) | 0.5 |
| **TỔNG** | **ĐÃ HOÀN THÀNH** | **10/10 YÊU CẦU MỞ RỘNG (100%)** | | **5.0 / 5.0** |

---

## CHƯƠNG 5. ĐÁNH GIÁ & PHÂN TÍCH

### 5.1. Ưu điểm nổi bật
1. **Kiến trúc Cloud-Native chuẩn mực:** Hệ thống bám sát các tiêu chuẩn công nghiệp về Microservices, Gateway Pattern, Centralized Authentication và Observability.
2. **Khởi tạo tự động hóa 100%:** Nhờ các kỹ thuật provisioning và seed scripts (Keycloak auto-import realm, MariaDB auto-init SQL, Grafana auto-provision datasources/dashboards, MinIO CLI bucket automation), toàn bộ hệ thống sẵn sàng hoạt động ngay sau lệnh `docker compose up -d` mà không cần bất kỳ thao tác thủ công nào qua giao diện.
3. **Hiệu năng cao & Tiết kiệm tài nguyên:** Tổng dung lượng RAM tiêu thụ cho toàn bộ 12 container chỉ xấp xỉ 1.8GB, hoàn toàn vận hành mượt mà trên máy trạm thông thường và các máy ảo EC2 cấu hình thấp (`t3.small` hoặc `t3.medium`).

### 5.2. Khó khăn đã giải quyết
- Đã khắc phục việc image `minio/minio` bị chặn tải từ Docker Hub bằng giải pháp image tương thích `pgsty/silo` và `pgsty/mc`.
- Đã khắc phục cơ chế include file của Bind9 9.18 để phân giải ổn định toàn bộ private zone `cloud.local`.
- Đã cấu hình linh hoạt biến môi trường `${PUBLIC_HOST:-localhost}` để hệ thống chạy thông suốt cả trên môi trường máy cục bộ lẫn trên máy ảo AWS EC2 với Public IP.

---

## PHỤ LỤC

### Phụ lục 1: Push Image lên Docker Hub
```bash
docker login
docker tag hotensv/web:dev <username>/myminicloud-web:v1.0
docker push <username>/myminicloud-web:v1.0
```

### Phụ lục 2: Triển khai trên AWS EC2 (Ubuntu)
1. Khởi tạo máy ảo EC2 Ubuntu 22.04 / 24.04 (t3.small hoặc t3.medium).
2. Mở Inbound Security Group: Port 80, 3000, 8081, 9001, 9090.
3. Cài đặt Docker Engine & Docker Compose plugin.
4. Copy thư mục `MyMiniCloud` lên máy ảo, tạo file `.env`:
   ```bash
   echo "PUBLIC_HOST=<PUBLIC_IP_EC2>" > .env
   ```
5. Chạy lệnh: `docker compose up -d`. Toàn bộ hệ thống sẽ truy cập được trực tiếp thông qua IP công cộng của EC2.
