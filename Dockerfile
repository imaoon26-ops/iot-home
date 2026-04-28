FROM python:3.9

# รวบคำสั่งให้อยู่บรรทัดเดียวกัน เพื่อป้องกันปัญหาช่องว่างที่มองไม่เห็น (NBSP)
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "api_server.py"]