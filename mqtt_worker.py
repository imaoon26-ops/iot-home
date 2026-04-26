import paho.mqtt.client as mqtt # เรียกใช้เครื่องมือคุยกับ MQTT
import sqlite3 # เรียกใช้เครื่องมือคุยกับฐานข้อมูล

# ฟังก์ชันสำหรับเขียนข้อมูลลง DB
def insert_db(query, data): 
    conn = sqlite3.connect('iot_database.db') # เปิดสมุดจด
    conn.execute(query, data)                 # เขียนข้อมูลตามคำสั่ง (query) ที่โยนเข้ามา
    conn.commit()                             # เซฟ
    conn.close()                              # ปิดสมุด

# ฟังก์ชันนี้จะทำงาน 'อัตโนมัติ' เวลามีข้อความส่งเข้ามาใน MQTT
def on_message(client, userdata, msg): 
    topic = msg.topic                             # ดูว่าส่งมาหัวข้อ (Topic) อะไร
    payload = msg.payload.decode('utf-8')         # แกะซองข้อความ (Payload) แปลงจากภาษาคอม(byte) เป็นตัวอักษร(utf-8)
    
    if topic == "house/room_temp": # ถ้าหัวข้อคือ อุณหภูมิ
        # บันทึกอุณหภูมิ (แปลง payload ให้เป็นเลขทศนิยม float) ลงตาราง room_temp
        insert_db("INSERT INTO room_temp (temp) VALUES (?)", (float(payload),))
        
    elif topic == "house/light/status": # ถ้าหัวข้อคือ สถานะไฟ
        status = True if payload == "ON" else False # แปลงคำว่า "ON" เป็น True, นอกนั้นเป็น False
        # บันทึกสถานะไฟลงตาราง light_status
        insert_db("INSERT INTO light_status (status) VALUES (?)", (status,))

client = mqtt.Client()          # สร้างตัวแทนเสมียนขึ้นมา 1 คน
client.on_message = on_message  # มอบหมายหน้าที่ "ถ้ามีข้อความมา ให้ไปทำฟังก์ชัน on_message นะ"

client.connect("localhost", 1883, 60) # ต่อไปที่ไปรษณีย์กลาง (localhost คือเครื่องเราเอง, พอร์ต 1883)
client.subscribe("house/#")           # สั่งเสมียนดักฟังทุกหัวข้อที่ขึ้นต้นด้วย "house/" (เครื่องหมาย # คืออะไรก็ได้ที่ตามหลัง)
client.loop_forever()                 # สั่งให้ทำงานไปเรื่อยๆ ห้ามหยุดพัก!