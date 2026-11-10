# HƯỚNG DẪN SỬ DỤNG CÁC ỨNG DỤNG WEB (WEB APPS) TRONG HỆ THỐNG MYMINICLOUD

Tài liệu này cung cấp hướng dẫn chi tiết từng bước để giảng viên, người đánh giá hoặc sinh viên có thể dễ dàng truy cập, tương tác và kiểm thử trực quan toàn bộ các giao diện Web Application trong hệ sinh thái **MyMiniCloud**.

---

## 1. BẢNG TRA CỨU NHANH CÁC GIAO DIỆN WEB & TÀI KHOẢN TRUY CẬP

| STT | Ứng dụng Web | Địa chỉ URL | Cổng Host | Tài khoản / Mật khẩu | Chức năng chính |
|:---:|---|---|:---:|:---:|---|
| **1** | **Cổng Web Portal & Blog** | [http://localhost/](http://localhost/) | 80 / 8080 | *Không cần đăng nhập* | Trang chủ tĩnh, blog 3 bài viết, ảnh SVG, responsive |
| **2** | **Cân bằng tải Round Robin**| [http://localhost/lb/](http://localhost/lb/) | 80 | *Không cần đăng nhập* | Trực quan hóa chia tải luân phiên giữa Server 1 và 2 |
| **3** | **Keycloak Identity Console** | [http://localhost:8081](http://localhost:8081) | 8081 | `admin` / `admin` | Quản lý Realm `realm_sv001`, Users, Clients OIDC |
| **4** | **MinIO Object Store UI** | [http://localhost:9001](http://localhost:9001) | 9001 | `minioadmin` / `minioadmin`| Quản lý Bucket, Upload file, phân quyền S3 |
| **5** | **Prometheus Metrics Web** | [http://localhost:9090](http://localhost:9090) | 9090 | *Không cần đăng nhập* | Kiểm tra sức khỏe Targets, tra cứu truy vấn PromQL |
| **6** | **Grafana Dashboard** | [http://localhost:3000](http://localhost:3000) | 3000 | `admin` / `admin` | Dashboard trực quan hóa CPU, RAM, Network Traffic |
| **7** | **API Microservice Explorer**| [http://localhost/api/hello](http://localhost/api/hello) | 80 | *Tùy theo endpoint* | Truy vấn REST API JSON, đọc MariaDB, kiểm thử OIDC |

---

## 2. KIỂM TRA HỆ THỐNG TRƯỚC KHI TRUY CẬP

Trước khi mở trình duyệt, đảm bảo cụm container đang chạy bằng lệnh sau trong Terminal / PowerShell:

```powershell
Set-Location "D:\cloud\MyMiniCloud"
docker compose ps
```

Nếu thấy 12 container đều ở trạng thái `Up`, hệ thống đã sẵn sàng 100%. Nếu container chưa chạy, hãy gõ:
```powershell
docker compose up -d
```

---

## 3. HƯỚNG DẪN CHI TIẾT TỪNG ỨNG DỤNG WEB

### 3.1. Web App 1: Cổng Web Portal & Blog cá nhân (Web Frontend)

- **Địa chỉ truy cập:** 
  - Qua API Gateway: **`http://localhost/`**
  - Trực tiếp vào container Web: **`http://localhost:8080/`**
- **Mô tả chức năng:**
  - Mô phỏng dịch vụ lưu trữ website tĩnh (tương đương AWS S3 Static Hosting hoặc AWS Amplify).
  - Được thiết kế với giao diện hiện đại, tối ưu khả năng tương thích trên cả máy tính lẫn thiết bị di động (Responsive Web Design).

#### Các bước trải nghiệm:
1. **Khám phá Trang chủ (Home):**
   - Mở trình duyệt và truy cập `http://localhost/`.
   - Xem phần giới thiệu đồ án đám mây, thông tin sinh viên và danh mục các bài viết mới nhất.
   - Thử nghiệm thanh điều hướng (Navigation Bar) trên cùng: bấm vào liên kết **Blog** hoặc nút **Xem tất cả bài viết**.
2. **Khám phá Chuyên trang Blog (`http://localhost/blog/`):**
   - Trang tập hợp danh sách các bài viết được nhóm theo thời gian thực hiện.
3. **Đọc 3 bài viết chuyên đề:**
   - **Bài viết 1 - *Docker là gì? Mình hiểu như sau* (`/blog/blog1.html`):** Giải thích sự khác biệt cốt lõi giữa Container và Máy ảo (Virtual Machine), minh họa bằng hình vẽ SVG con tàu chở container.
   - **Bài viết 2 - *Nginx và cái dấu gạch chéo* (`/blog/blog2.html`):** Phân tích sự khác nhau giữa chỉ thị `root` và `alias` trong cấu hình máy chủ Nginx, minh họa quy trình định tuyến từ Request đến thư mục web.
   - **Bài viết 3 - *Chín server trong một cái laptop* (`/blog/blog3.html`):** Bảng so sánh trực quan giữa 9 server trong hệ thống MyMiniCloud với các dịch vụ tương đương trên AWS.
4. **Kiểm tra tính năng quay lại:** Ở cuối mỗi bài viết đều có nút **Quay lại trang chính** giúp người dùng điều hướng mượt mà.

---

### 3.2. Web App 2: Cân bằng tải Web luân phiên (Load Balancer Demo App)

- **Địa chỉ truy cập:** **`http://localhost/lb/`**
- **Mô tả chức năng:**
  - Minh họa cơ chế cân bằng tải ứng dụng (Application Load Balancing) sử dụng Nginx Reverse Proxy với thuật toán **Round Robin**.
  - Phía sau Gateway là một cụm gồm 2 máy chủ Web độc lập: `web-frontend-server1` (cổng 8082) và `web-frontend-server2` (cổng 8083).

#### Các bước trải nghiệm:
1. Mở trình duyệt và gõ địa chỉ: `http://localhost/lb/`
2. **Lần truy cập 1:** Bạn sẽ nhìn thấy màn hình hiển thị dòng chữ lớn:
   - **`SERVER 1`** trên nền màu **Xanh ngọc (Teal - `#0F766E`)**.
3. **Lần truy cập 2:** Nhấn phím **F5** (hoặc nút **Reload / Tải lại** trên trình duyệt):
   - Màn hình đổi ngay sang **`SERVER 2`** trên nền màu **Cam hổ phách (Amber - `#B45309`)**.
4. **Lần truy cập 3 & tiếp theo:** Tiếp tục nhấn F5, trang web sẽ luân phiên đổi màu xanh - cam - xanh - cam theo đúng tỉ lệ 50/50.
5. **Kiểm tra kỹ thuật:** Bạn có thể bấm chuột phải chọn **Inspect (Kiểm tra)** -> chuyển sang tab **Network** -> xem Header phản hồi: sẽ thấy trường `X-Upstream: 172.xx.xx.xx:80` thay đổi IP tương ứng của từng container.

---

### 3.3. Web App 3: Quản lý định danh Keycloak (Identity & Access Management Console)

- **Địa chỉ truy cập:** **`http://localhost:8081`** (hoặc qua Gateway: `http://localhost/auth/`)
- **Tài khoản đăng trị mặc định:**
  - **Username:** `admin`
  - **Password:** `admin`

#### Các bước trải nghiệm:
1. **Đăng nhập:** Mở `http://localhost:8081`, điền thông tin `admin` / `admin` và bấm **Sign In**.
2. **Xem Realm đã nạp:**
   - Ở góc trên bên trái (dưới logo Keycloak), bấm vào menu chọn Realm (đang là `master`).
   - Bạn sẽ thấy realm **`realm_sv001`** đã được hệ thống tự động import sẵn. Chọn `realm_sv001`.
3. **Quản lý Người dùng (Users):**
   - Bấm vào mục **Users** ở thanh menu bên trái.
   - Bạn sẽ thấy 2 tài khoản sinh viên đã được tạo sẵn: **`sv01`** (Sinh Vien Mot) và **`sv02`** (Sinh Vien Hai).
   - Mật khẩu mặc định của 2 tài khoản này là: **`123456`**.
4. **Quản lý Client (OIDC Clients):**
   - Bấm vào mục **Clients** ở menu bên trái.
   - Nhấp vào client **`flask-app`**.
   - Kiểm tra thấy: `Client authentication` tắt (Public Client), `Direct access grants` bật, và có cấu hình Audience Mapper gắn token vào `flask-app`.

---

### 3.4. Web App 4: Lưu trữ đối tượng MinIO (Object Storage Console)

- **Địa chỉ truy cập:** **`http://localhost:9001`**
- **Tài khoản đăng nhập:**
  - **Username:** `minioadmin`
  - **Password:** `minioadmin`

#### Các bước trải nghiệm:
1. **Đăng nhập giao diện S3 Console:**
   - Mở `http://localhost:9001`, nhập `minioadmin` / `minioadmin` và nhấn **Login**.
2. **Xem danh sách Bucket trong `Object Browser`:**
   - Nhấp vào **Object Browser** ở thanh bên trái.
   - Hệ thống hiển thị 2 bucket đã được tạo tự động:
     - **`profile-pics` (Public):** Bấm vào bucket, bạn sẽ thấy tệp `avatar.jpg`. Thử mở đường dẫn trực tiếp trên trình duyệt: [http://localhost:9000/profile-pics/avatar.jpg](http://localhost:9000/profile-pics/avatar.jpg) -> Ảnh đại diện hiển thị ngay lập tức (HTTP 200).
     - **`documents` (Private):** Chứa tệp `baocao.pdf`. Khi thử mở trực tiếp [http://localhost:9000/documents/baocao.pdf](http://localhost:9000/documents/baocao.pdf) trên trình duyệt -> Hệ thống trả về `AccessDenied` (HTTP 403) chứng minh chính sách bảo mật Private hoạt động chuẩn xác.
3. **Thao tác tải lên file mới:** Bạn có thể bấm nút **Upload** -> **Upload File** để tải bất kỳ file nào từ máy tính lên bucket.

---

### 3.5. Web App 5: Giám sát chỉ số Prometheus (Metrics & Target Health)

- **Địa chỉ truy cập:** **`http://localhost:9090`**
- **Mô tả chức năng:**
  - Công cụ thu thập chuỗi thời gian (Time-series Database) hàng đầu cho hệ thống đám mây.

#### Các bước trải nghiệm:
1. **Kiểm tra trạng thái các Target (Status -> Targets):**
   - Trên thanh menu trên cùng, bấm vào **Status** -> chọn **Targets**.
   - Quan sát mục **node** (`monitoring-node-exporter-server:9100`): Hiển thị nhãn xanh lá cây **UP**.
   - Quan sát mục **web** (`web-frontend-server:80`): Hiển thị nhãn xanh lá cây **UP** (nhờ endpoint `/metrics` đã được tích hợp).
2. **Thực thi truy vấn PromQL trên giao diện Graph:**
   - Bấm vào menu **Query** (hoặc biểu tượng Prometheus ở góc trái).
   - Trong ô tìm kiếm `Expression`, nhập các câu lệnh sau và bấm nút **Execute**, sau đó chuyển sang tab **Graph**:
     - `node_cpu_seconds_total`: Xem biểu đồ xung nhịp CPU theo từng chế độ (idle, system, user).
     - `node_memory_MemAvailable_bytes`: Xem dung lượng RAM khả dụng của máy chủ.
     - `web_up`: Trả về giá trị `1` xác nhận máy chủ web đang hoạt động bình thường.

---

### 3.6. Web App 6: Trực quan hóa hạ tầng Grafana Dashboard

- **Địa chỉ truy cập:** **`http://localhost:3000`**
- **Tài khoản đăng nhập:**
  - **Username:** `admin`
  - **Password:** `admin`

#### Các bước trải nghiệm:
1. **Đăng nhập Grafana:** Mở `http://localhost:3000`, nhập `admin` / `admin` và chọn **Log in** (Nếu hỏi đổi mật khẩu mới, có thể bấm **Skip**).
2. **Mở Dashboard giám sát:**
   - Bấm vào biểu tượng menu góc trên bên trái -> chọn **Dashboards**.
   - Nhấp vào dashboard có tên: **`System Health of SV001`**.
3. **Quan sát 3 biểu đồ giám sát trực quan:**
   - **Panel 1 - CPU Usage (%):** Biểu diễn tỷ lệ phần trăm CPU tiêu thụ theo thời gian thực (tính từ metric `node_cpu_seconds_total`).
   - **Panel 2 - Memory Usage (%):** Biểu diễn tỷ lệ RAM đang được sử dụng của hệ thống (tính từ `MemAvailable` và `MemTotal`).
   - **Panel 3 - Network Traffic (Bps):** Biểu đồ đo lưu lượng mạng nhận vào (Receive - đường màu xanh) và truyền đi (Transmit - đường màu vàng) của container.
4. **Tùy chỉnh thời gian hiển thị:**
   - Ở góc trên bên phải, bấm vào khung thời gian (mặc định: `Last 30 minutes`), bạn có thể chọn `Last 5 minutes` để theo dõi sát hơn.
   - Bấm vào biểu tượng mũi tên cạnh nút Refresh để chọn chế độ tự động làm mới: `Auto refresh: 5s` hoặc `10s`.

---

### 3.7. Web App 7: Kiểm thử RESTful Microservice API qua Trình duyệt

Bạn có thể nhập trực tiếp các URL sau vào thanh địa chỉ của trình duyệt Chrome/Edge/Firefox để kiểm tra các API trả về định dạng JSON:

1. **API Chào mừng:**
   - URL: [http://localhost/api/hello](http://localhost/api/hello)
   - Kết quả hiển thị: `{"message": "Hello from App Server!"}`
2. **API Sinh viên (Đọc file JSON):**
   - URL: [http://localhost/api/student](http://localhost/api/student)
   - Kết quả: Danh sách 5 sinh viên với đầy đủ thông tin: ID, Họ tên, Chuyên ngành và GPA.
3. **API Sinh viên (Đọc trực tiếp từ CSDL MariaDB):**
   - URL: [http://localhost/api/students-db](http://localhost/api/students-db)
   - Kết quả: Dữ liệu thời gian thực được truy vấn từ bảng `students` trong cơ sở dữ liệu `studentdb`.
4. **Kiểm tra định tuyến Gateway:**
   - URL: [http://localhost/student/](http://localhost/student/)
   - Kết quả: Nginx Gateway tự động điều phối yêu cầu tới API `/student` của Backend.

---

## 4. TỔNG KẾT & GỢI Ý KHI THỰC HIỆN BÁO CÁO / DEMO

Khi thuyết trình hoặc chụp ảnh minh chứng cho báo cáo cuối kỳ, sinh viên nên mở lần lượt các tab trình duyệt theo thứ tự:
1. **Tab 1:** `http://localhost/` (Giao diện Blog chính)
2. **Tab 2:** `http://localhost/lb/` (Demo F5 luân phiên màu xanh - cam)
3. **Tab 3:** `http://localhost/api/students-db` (Dữ liệu sinh viên từ MariaDB)
4. **Tab 4:** `http://localhost:8081` (Keycloak Users: `sv01`, `sv02`)
5. **Tab 5:** `http://localhost:9001` (MinIO Object Browser: 2 bucket)
6. **Tab 6:** `http://localhost:9090/targets` (Prometheus 2 target UP)
7. **Tab 7:** `http://localhost:3000` (Grafana Dashboard 3 biểu đồ CPU/RAM/Net)

Trình tự này giúp người xem thấy rõ được toàn cảnh một hệ thống đám mây thu nhỏ hoàn thiện từ Frontend, API, Database, Security đến Monitoring!
