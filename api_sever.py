from flask_cors import CORS  # เพิ่มบรรทัดนี้ด้านบน

app = Flask(__name__)
CORS(app)  # เพิ่มบรรทัดนี้ใต้บรรทัด app = Flask...
from flask import Flask, jsonify # เรียกใช้ Flask สำหรับทำ Web API
import sqlite3 
import paho.mqtt.publish as publish # เรียกเครื่องมือสำหรับ "ส่ง" ข้อความเข้า MQTT อย่างเดียว

app = Flask(__name__) # สร้างแอปพลิเคชันเว็บตั้งชื่อว่า app

# ฟังก์ชันสำหรับไปดึงข้อมูลจาก DB มาส่งให้หน้าเว็บ
def query_db(query):
    conn = sqlite3.connect('iot_database.db')
    conn.row_factory = sqlite3.Row  # ให้คืนค่ามาเป็นชื่อคอลัมน์ จะได้อ่านง่ายๆ
    rv = conn.execute(query).fetchall() # ดึงข้อมูลมาทั้งหมดที่เข้าเงื่อนไข
    conn.close()
    return rv # ส่งข้อมูลกลับไป

# สร้างช่องทาง (Endpoint) URL: http://localhost:5000/room_temp
@app.route('/room_temp', methods=['GET']) 
def get_temp():
    # ไปค้นหา temp จาก room_temp เรียงจากเวลาล่าสุด (DESC) เอามาแค่ 1 ตัว (LIMIT 1)
    row = query_db("SELECT temp FROM room_temp ORDER BY timestamp DESC LIMIT 1")
    # ส่งข้อมูลกลับไปในรูปแบบ JSON (ถ้าไม่มีข้อมูลให้ส่ง 0.0)
    return jsonify({"temp": row[0]['temp'] if row else 0.0})

# --- (ของเดิม) สำหรับไฟบ้านสีน้ำเงิน (หน้าเว็บกดเรียก) ---
@app.route('/light_on', methods=['GET'])
def light_on():
    publish.single("house/light/command", "ON", hostname="localhost")
    return jsonify({"status": "success"})

@app.route('/light_off', methods=['GET'])
def light_off():
    publish.single("house/light/command", "OFF", hostname="localhost")
    return jsonify({"status": "success"})

# --- (เพิ่มใหม่) สำหรับประตูไฟสีแดง (กล้อง ESP32-CAM เรียก) ---
@app.route('/door_unlock', methods=['GET', 'POST'])
def door_unlock():
    # ยิงข้อความไปที่หัวข้อ door/command เพื่อสั่งเปิดไฟแดง
    publish.single("house/door/command", "ON", hostname="localhost")
    return jsonify({"status": "Door Unlocked!"})

if __name__ == '__main__':
    # เปิดเซิร์ฟเวอร์ที่พอร์ต 5000 และให้ทุกคนในวง LAN เข้าถึงได้ (0.0.0.0)
    app.run(host='0.0.0.0', port=5000)