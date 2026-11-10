from flask import Flask, jsonify, request
import json, os, time, requests, pymysql
from jose import jwt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- OIDC (Keycloak) ---
# ISSUER   : giá trị claim "iss" mà token mang theo (địa chỉ Keycloak mà người dùng truy cập)
# JWKS_URL : nơi backend lấy public key, đi thẳng qua mạng nội bộ cloud-net
ISSUER   = os.getenv("OIDC_ISSUER",   "http://localhost:8081/realms/realm_sv001")
JWKS_URL = os.getenv("OIDC_JWKS_URL", "http://authentication-identity-server:8080/realms/realm_sv001/protocol/openid-connect/certs")
AUDIENCE = os.getenv("OIDC_AUDIENCE", "flask-app")

# --- Database (MariaDB) ---
DB_CFG = dict(
    host=os.getenv("DB_HOST", "relational-database-server"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "root"),
    database=os.getenv("DB_NAME", "studentdb"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    connect_timeout=5,
)

_JWKS = None
_TS = 0

def get_jwks():
    global _JWKS, _TS
    now = time.time()
    if not _JWKS or now - _TS > 600:
        _JWKS = requests.get(JWKS_URL, timeout=5).json()
        _TS = now
    return _JWKS

app = Flask(__name__)
app.json.ensure_ascii = False   # giữ nguyên tiếng Việt có dấu trong JSON
app.json.sort_keys = False      # giữ đúng thứ tự trường

@app.get("/hello")
def hello():
    return jsonify(message="Hello from App Server!")

@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, get_jwks(), algorithms=["RS256"],
                             audience=AUDIENCE, issuer=ISSUER)
        return jsonify(message="Secure resource OK",
                       preferred_username=payload.get("preferred_username"))
    except Exception as e:
        return jsonify(error=str(e)), 401

# [P2-2] API /student: đọc danh sách sinh viên từ file JSON
@app.get("/student")
def student():
    with open(os.path.join(BASE_DIR, "students.json"), encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

# [P2-3] API /students-db: đọc danh sách sinh viên từ MariaDB (studentdb.students)
@app.get("/students-db")
def students_db():
    try:
        conn = pymysql.connect(**DB_CFG)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, student_id, fullname, dob, major FROM students ORDER BY id")
                rows = cur.fetchall()
        finally:
            conn.close()
        for r in rows:
            r["dob"] = r["dob"].isoformat() if r["dob"] else None
        return jsonify(rows)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
