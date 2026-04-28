# ใช้ตัวปกติ ไม่เอา slim เพื่อลดขั้นตอนลง compiler
FROM python:3.9

# ติดตั้ง lib สำหรับประมวลผลภาพ (OpenCV) นิดหน่อย
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ติดตั้ง library (ขั้นตอนนี้ dlib จะใช้เวลา build แป๊บหนึ่ง)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# รัน API
CMD ["python", "api_server.py"]
