#!/usr/bin/env sh
# [P2-5] Tạo bucket profile-pics (public) + documents (private) rồi upload file mẫu.
# Chạy ở thư mục gốc dự án (bash / Git Bash / PowerShell đều dùng được lệnh docker bên dưới):
docker run --rm --network cloud-net -v "${PWD}/object-storage-server/seed:/seed" --entrypoint sh minio/mc -c "
  mc alias set local http://object-storage-server:9000 minioadmin minioadmin &&
  mc mb --ignore-existing local/profile-pics &&
  mc mb --ignore-existing local/documents &&
  mc anonymous set download local/profile-pics &&
  mc cp /seed/avatar.jpg local/profile-pics/avatar.jpg &&
  mc cp /seed/baocao.pdf local/documents/baocao.pdf &&
  mc ls local
"
