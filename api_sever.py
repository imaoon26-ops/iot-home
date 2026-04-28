from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import paho.mqtt.publish as publish
from datetime import datetime
import face_recognition
import cv2
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# ==========================================
# 🌟 ระบบ AI โหลดรูปเจ้าของบ้าน (เตรียมไว้เทียบหน้า)
# ==========================================
try:
    # จะไปดึงรูป owner.jpg ในโฟลเดอร์ known_faces มาเป็นต้นแบบ
    known_image = face_recognition.load_image_file("known_faces/owner.jpg")
    known_encoding = face_recognition.face_encodings(known_image)[0]
    print("✅ ระบบ AI พร้อม! โหลดใบหน้าเจ้าของบ้านสำเร็จ")
except Exception as e:
    print("⚠️ แจ้งเตือน: หาไฟล์ known_faces/owner.jpg ไม่เจอ (ระบบสแกนหน้าจะยังไม่ทำงาน)")
    known_encoding = None

# ==========================================
# ฟังก์ชันดึงข้อมูลจาก Database
# ==========================================
def query_db(query):
    try:
        conn = sqlite3.connect('iot_database.db')
        conn.row_factory = sqlite3.Row  
        rv = conn.execute(query).fetchall() 
        conn.close()
        return rv 
    except sqlite3.OperationalError as e:
        print(f"Database Error: {e}")
        return []

# ==========================================
# 1. API: ข้อมูลสมาชิกในทีม (อาจารย์ใช้ตรวจคะแนน)
# ==========================================
@app.route('/info', methods=['GET'])
def info():
    # TODO: อย่าลืมแก้ชื่อและรหัสนักศึกษาให้เป็นของทีมตัวเอง!
    return jsonify({
        "name": ["นาย A", "นาย B", "นาย C"], 
        "std_id": ["66xxxxxx", "66xxxxxx", "66xxxxxx"]
    })

# ==========================================
# 2. API: ดึงอุณหภูมิปัจจุบัน
# ==========================================
@app.route('/room_temp', methods=['GET'])
def get_temp():
    row = query_db("SELECT temp FROM room_temp ORDER BY timestamp DESC LIMIT 1")
    return jsonify({"temp": row[0]['temp'] if row else 0.0})

# ==========================================
# 3. API: ควบคุมและตรวจสอบสถานะไฟ (Output: {} ตามโจทย์)
# ==========================================
@app.route('/light_on', methods=['GET'])
def light_on():
    publish.single("house/light/command", "ON", hostname="localhost")
    return jsonify({}) 

@app.route('/light_off', methods=['GET'])
def light_off():
    publish.single("house/light/command", "OFF", hostname="localhost")
    return jsonify({}) 

@app.route('/light_status', methods=['GET'])
def light_status():
    row = query_db("SELECT status FROM light_status ORDER BY timestamp DESC LIMIT 1")
    is_on = True if (row and row[0]['status'] == 'ON') else False
    return jsonify({"light": is_on})

# ==========================================
# 4. API: ตรวจสอบสถานะบอร์ด ESP32 (Heartbeat)
# ==========================================
@app.route('/status', methods=['GET'])
def status():
    row = query_db("SELECT status, timestamp FROM board_status ORDER BY timestamp DESC LIMIT 1")
    return jsonify({
        "ESP32_House": True if (row and row[0]['status'] == 'ON') else False,
        "last_time_heartbeat": row[0]['timestamp'] if row else "N/A"
    })

# ==========================================
# 5. API: รับรูปจากกล้อง ESP32-CAM และสแกนหน้า
# ==========================================
@app.route('/scan_face', methods=['POST'])
def scan_face():
    # 5.1 เช็คว่ามีไฟล์รูปส่งมาไหม
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image found"}), 400

    # 5.2 แปลงไฟล์รูปให้ AI อ่านได้
    file = request.files['image']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 5.3 ค้นหาใบหน้าในรูปภาพ
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    # 5.4 เทียบว่าหน้าตรงกับเจ้าของบ้านไหม
    for face_encoding in face_encodings:
        if known_encoding is not None:
            matches = face_recognition.compare_faces([known_encoding], face_encoding)
            
            if True in matches:
                # 🎯 FEEDBACK LOOP: หน้าตรง! สั่งเปิดไฟทันที
                publish.single("house/light/command", "ON", hostname="localhost")
                print("🚨 สแกนหน้าผ่าน! ส่งคำสั่งเปิดไฟบ้านแล้ว")
                return jsonify({"status": "success", "message": "Face Recognized! LED ON."}), 200

    # หน้าไม่ตรง / ไม่เจอหน้า
    print("❌ สแกนหน้าไม่ผ่าน (ไม่ใช่เจ้าของบ้าน)")
    return jsonify({"status": "fail", "message": "Unknown Person"}), 401

# ==========================================
# 6. API: กราฟประวัติอุณหภูมิย้อนหลัง (สำหรับคะแนน Bonus)
# ==========================================
@app.route('/api/history/temp', methods=['GET'])
def get_temp_history():
    rows = query_db("SELECT timestamp, temp FROM room_temp ORDER BY timestamp DESC LIMIT 20")
    
    labels = []
    values = []
    
    for r in reversed(rows): 
        timestamp_str = r['timestamp']
        # ตัดเอาแค่เวลา (HH:MM:SS) มาแสดง จะได้ไม่รกกราฟ
        time_only = timestamp_str.split(' ')[1] if ' ' in timestamp_str else timestamp_str
        labels.append(time_only) 
        values.append(r['temp'])
        
    return jsonify({"labels": labels, "values": values})

if __name__ == '__main__':
    # รันเซิร์ฟเวอร์
    app.run(host='0.0.0.0', port=5000)