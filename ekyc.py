import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os

CONFIG_FILE = "config.ini"

# ==================== CONFIG & HELPER FUNCTIONS ====================

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
            
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED: ไม่สามารถอ่านไฟล์ {filename} ได้: {e}")
        return configparser.ConfigParser()

# โหลด Config
CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้ โปรดตรวจสอบไฟล์")
    exit()

# ดึงค่า Global ที่ใช้ร่วมกัน
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']

# ดึง Section หลัก
B_CFG = CONFIG['EKYC_MAIN']
S_CFG = CONFIG['EKYC_SERVICES']

# ==================== MAIN LOGIC ====================

def run_ekyc_step(service_name, service_title):
    """
    Flow การทำงาน:
    1. กด 'A' (Agency)
    2. กด 'K' (BaS)
    3. เลือกรายการย่อย (Service Title)
    4. กรอกเบอร์โทรศัพท์
    5. กด 'ถัดไป'
    6. กด 'ESC' เพื่อออก
    """
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {service_name} (รหัส: {service_title})")
    
    # ดึงค่า Config ที่จำเป็น
    HOTKEY_AGENCY_TITLE = B_CFG['HOTKEY_AGENCY_TITLE']
    HOTKEY_BaS_TITLE = B_CFG['HOTKEY_BaS_TITLE']
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    ID_AUTO_ID = B_CFG['ID_AUTO_ID']
    
    try:
        # เชื่อมต่อ Application
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        # print("[/] เชื่อมต่อหน้าจอสำเร็จ")

        # 1. กด A (Agency)
        print(f"[*] 1. กดปุ่ม '{HOTKEY_AGENCY_TITLE}' (Agency)")
        main_window.child_window(title=HOTKEY_AGENCY_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 2. กด K (BaS)
        print(f"[*] 2. กดปุ่ม '{HOTKEY_BaS_TITLE}' (BaS)")
        main_window.child_window(title=HOTKEY_BaS_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 3. เลือกรายการย่อย
        print(f"[*] 3. เลือกรายการ: {service_title}")
        main_window.child_window(title=service_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 4. กรอกเบอร์โทรศัพท์
        print(f"[*] 4. กรอกเบอร์โทรศัพท์: {PHONE_NUMBER}")
        main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit").click_input()
        main_window.type_keys(PHONE_NUMBER)
        
        # 5. กด 'ถัดไป'
        print(f"[*] 5. กดปุ่ม '{NEXT_TITLE}'")
        main_window.child_window(title=NEXT_TITLE, auto_id=ID_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 6. กด ESC
        print(f"[*] 6. กดปุ่ม ESC เพื่อย้อนกลับ")
        main_window.type_keys("{ESC}")
        time.sleep(WAIT_TIME)
        
        print(f"[V] รายการ {service_name} เสร็จสิ้น")
        
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดในรายการ {service_name}: {e}")

# ----------------- Main Execution -----------------

if __name__ == "__main__":
    if 'EKYC_1_TITLE' in S_CFG:
        run_ekyc_step("Service 1", S_CFG['EKYC_1_TITLE'])
        
    if 'EKYC_2_TITLE' in S_CFG:
        run_ekyc_step("Service 2", S_CFG['EKYC_2_TITLE'])
        
    print(f"\n{'='*50}\n[V] จบการทำงานทั้งหมด")