from flask import Flask, jsonify, request
from flask_cors import CORS  # ตัวป้องกันเบราว์เซอร์บล็อกหน้าเว็บ
import sqlite3 
import paho.mqtt.publish as publish 

# --- สร้างและตั้งค่าแอปพลิเคชัน ---
app = Flask(__name__) 
CORS(app)  # เปิดใช้งาน CORS

# --- ฟังก์ชันตัวช่วย (Helper Function) ---
def query_db(query):
    conn = sqlite3.connect('iot_database.db')
    conn.row_factory = sqlite3.Row  
    rv = conn.execute(query).fetchall() 
    conn.close()
    return rv 

# ==========================================
# ส่วนที่ 1: API สำหรับดึงข้อมูลล่าสุด
# ==========================================
@app.route('/room_temp', methods=['GET']) 
def get_temp():
    # ดึงค่าอุณหภูมิล่าสุด 1 ค่า
    row = query_db("SELECT temp FROM room_temp ORDER BY timestamp DESC LIMIT 1")
    return jsonify({"temp": row[0]['temp'] if row else 0.0})


@app.route('/door_unlock', methods=['GET', 'POST'])
def door_unlock():
    # กล้องจะยิงมาที่นี่ เพื่อสั่งเปิดไฟแดง
    publish.single("house/door/command", "ON", hostname="localhost")
    return jsonify({"status": "Door Unlocked!"})

# ==========================================
# ส่วนที่ 3: API สำหรับดึงประวัติไปทำกราฟ (Frontend)
# ==========================================
@app.route('/api/history/temp', methods=['GET'])
def get_temp_history():
    # ดึงข้อมูล 20 ค่าล่าสุดไปวาดกราฟ
    rows = query_db("SELECT timestamp, temp FROM room_temp ORDER BY timestamp DESC LIMIT 20")
    
    labels = []
    values = []
    
    # ต้องกลับด้านข้อมูล (reversed) เพื่อให้กราฟเรียงจากซ้าย (อดีต) ไปขวา (ปัจจุบัน)
    for r in reversed(rows): 
        # ตัดเอาแค่เวลา (HH:MM:SS) มาแสดง จะได้ไม่รกกราฟ
        timestamp_str = r['timestamp']
        if ' ' in timestamp_str:
            time_only = timestamp_str.split(' ')[1] 
        else:
            time_only = timestamp_str
            
        labels.append(time_only) 
        values.append(r['temp'])
        
    return jsonify({"labels": labels, "values": values})

# ==========================================
# ส่วนการรันเซิร์ฟเวอร์
# ==========================================
if __name__ == '__main__':
    # เปิดเซิร์ฟเวอร์ที่พอร์ต 5000 
    app.run(host='0.0.0.0', port=5000)