import paho.mqtt.client as mqtt 
import sqlite3 

# --- 🌟 เพิ่มใหม่: ฟังก์ชันสำหรับสร้างตารางอัตโนมัติ (รันครั้งแรกตารางจะได้ไม่พัง) ---
def init_db():
    conn = sqlite3.connect('iot_database.db')
    # สร้างตาราง room_temp
    conn.execute('''CREATE TABLE IF NOT EXISTS room_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT (datetime('now','localtime')),
                    temp REAL)''')
    # สร้างตาราง light_status
    conn.execute('''CREATE TABLE IF NOT EXISTS light_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT (datetime('now','localtime')),
                    status BOOLEAN)''')
    # สร้างตาราง door_status
    conn.execute('''CREATE TABLE IF NOT EXISTS door_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT (datetime('now','localtime')),
                    status TEXT)''')
    conn.commit()
    conn.close()

# ฟังก์ชันสำหรับเขียนข้อมูลลง DB (ของเดิมน้อง)
def insert_db(query, data): 
    conn = sqlite3.connect('iot_database.db') 
    conn.execute(query, data)                 
    conn.commit()                             
    conn.close()                              

# ฟังก์ชันนี้จะทำงาน 'อัตโนมัติ' เวลามีข้อความส่งเข้ามาใน MQTT
def on_message(client, userdata, msg): 
    topic = msg.topic                             
    payload = msg.payload.decode('utf-8')         
    
    # --- 🌟 เพิ่มใหม่: ปริ้นท์บอกในหน้าจอ Terminal จะได้รู้ว่ามีข้อมูลเข้า ---
    print(f"📥 ได้รับข้อความ | หัวข้อ: {topic} | ข้อมูล: {payload}")
    
    if topic == "house/room_temp": 
        insert_db("INSERT INTO room_temp (temp) VALUES (?)", (float(payload),))
        
    
        
    # --- 🌟 เพิ่มใหม่: ถ้าหัวข้อคือ สถานะประตู (LOCKED / UNLOCKED) ---
    elif topic == "house/door/status":
        insert_db("INSERT INTO door_status (status) VALUES (?)", (payload,))

# =========================================
# เริ่มต้นการทำงานของโปรแกรม
# =========================================

init_db() # เรียกใช้ฟังก์ชันสร้างตาราง (ถ้ามีอยู่แล้วมันจะข้ามไปเอง)

client = mqtt.Client()          
client.on_message = on_message  

client.connect("localhost", 1883, 60) 
client.subscribe("house/#")           

print("🚀 MQTT Worker เริ่มทำงานและกำลังดักฟังข้อความ...") # แจ้งเตือนตอนเริ่มรัน
client.loop_forever()