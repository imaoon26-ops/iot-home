import sqlite3 # เรียกใช้งานเครื่องมือทำฐานข้อมูล SQLite (เปรียบเหมือนไปจ้างช่างทำสมุดจด)

def init_db(): # สร้างฟังก์ชันชื่อ init_db() ให้เป็นหมวดหมู่
    # บรรทัดนี้สั่งสร้างไฟล์ชื่อ 'iot_database.db' ถ้ามีอยู่แล้วมันจะแค่เปิดไฟล์นั้นขึ้นมา
    conn = sqlite3.connect('iot_database.db') 
    
    cursor = conn.cursor() # สร้าง 'ปากกา' (cursor) สำหรับเอาไว้เขียนคำสั่งลงในสมุด

    # --- ส่วนที่ 1: สร้างตารางอุณหภูมิ ---
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS room_temp ( -- สร้างหน้ากระดาษชื่อ room_temp (ถ้ายังไม่มี)
            id INTEGER PRIMARY KEY,            -- ช่องลำดับที่ (1, 2, 3...)
            temp REAL,                         -- ช่องเก็บอุณหภูมิแบบทศนิยม (REAL)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP -- ช่องประทับเวลาอัตโนมัติ
        )
    ''')

    # --- ส่วนที่ 2: สร้างตารางสถานะไฟ ---
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS light_status ( -- สร้างหน้ากระดาษชื่อ light_status
            id INTEGER PRIMARY KEY,
            status BOOLEAN,                       -- ช่องเก็บว่าไฟ เปิด(True) หรือ ปิด(False)
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- ส่วนที่ 3: สร้างตารางสถานะบอร์ด ---
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS board_status ( -- สร้างหน้ากระดาษชื่อ board_status
            id INTEGER PRIMARY KEY,
            board_name TEXT,                      -- ช่องเก็บชื่อบอร์ดเป็นข้อความ
            is_online BOOLEAN,                    -- ช่องเก็บว่า ออนไลน์อยู่ไหม
            last_time_heartbeat DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit() # เซฟสมุด! (สำคัญมาก ถ้าไม่ commit ข้อมูลที่เขียนมาจะหายหมด)
    conn.close()  # ปิดหน้าสมุด
    print("สร้าง Database สำเร็จ!") # ปริ้นท์บอกเราว่าทำงานเสร็จแล้ว

if __name__ == '__main__': # เช็คว่าเรากำลังกดรันไฟล์นี้โดยตรงใช่ไหม?
    init_db()              # ถ้าใช่ ให้เรียกใช้ฟังก์ชัน init_db() ด้านบนเลย