FROM python:3.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir flask requests python-jose pymysql
COPY app.py students.json ./
EXPOSE 8081
CMD ["python","app.py"]
