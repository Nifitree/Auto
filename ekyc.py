import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys # เพิ่ม sys

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
    # ใช้ sys.exit(1) เพื่อให้แน่ใจว่าโปรแกรมหยุดทำงาน
    sys.exit(1) 

# ดึงค่า Global ที่ใช้ร่วมกัน
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID'] 

# ดึง Section หลัก
B_CFG = CONFIG['EKYC_MAIN']
S_CFG = CONFIG['EKYC_SERVICES']

# ==================== SCROLL HELPERS mouse ====================

def force_scroll_down(window, config):
    """เลื่อนหน้าจอลงโดยใช้ Mouse wheel"""
    try:
        center_x_offset = config.getint('MOUSE_SCROLL', 'CENTER_X_OFFSET')
        center_y_offset = config.getint('MOUSE_SCROLL', 'CENTER_Y_OFFSET')
        wheel_dist = config.getint('MOUSE_SCROLL', 'WHEEL_DIST')
        focus_delay = config.getfloat('MOUSE_SCROLL', 'FOCUS_DELAY')
        scroll_delay = config.getfloat('MOUSE_SCROLL', 'SCROLL_DELAY')
    except ValueError:
        print("[!] Scroll config invalid. Using defaults.")
        center_x_offset, center_y_offset, wheel_dist, focus_delay, scroll_delay = 300, 300, -20, 0.5, 1.0

    print(f"...กำลังเลื่อนหน้าจอลง (Mouse Wheel {wheel_dist})...")

    try:
        rect = window.rectangle()
        center_x = rect.left + center_x_offset
        center_y = rect.top + center_y_offset
        
        mouse.click(coords=(center_x, center_y))
        time.sleep(focus_delay)
        
        mouse.scroll(coords=(center_x, center_y), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)
        print("[/] Scroll สำเร็จ")
    except Exception as e:
        print(f"[!] Scroll failed: {e}, ใช้ PageDown แทน")
        window.type_keys("{PGDN}")

# ==================== MAIN LOGIC ====================

def run_ekyc_step(service_name, service_title):
    """
    Flow การทำงาน:
    1. กด 'A' (Agency)
    2. กด 'K' (BaS)
    3. เลือกรายการย่อย (Service Title)
    4. ตรวจสอบ/กรอกเลขไปรษณีย์
    5. ตรวจสอบ/กรอกเบอร์โทรศัพท์
    6. กด 'ถัดไป'
    7. กด 'ESC' เพื่อออก
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
        print("[/] เชื่อมต่อหน้าจอสำเร็จ")

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

        # 4. [การตรวจสอบ/กรอก] เลขไปรษณีย์
        print(f"[*] 4. กำลังตรวจสอบ/กรอกเลขไปรษณีย์ ID='{POSTAL_CODE_EDIT_AUTO_ID}'")
        postal_control = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        
        #  [จุดที่ 1] ตรวจสอบว่าช่องปรากฏหรือไม่ ก่อน Scroll
        if not postal_control.exists(timeout=1):
            print("[!] ช่องไปรษณีย์ไม่ปรากฏทันที, กำลังเลื่อนหน้าจอลง...")
        
        # ใช้การวนลูป Scroll & Check เพื่อความแม่นยำสูงสุด
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if postal_control.exists(timeout=1):
                print("[/] ช่องไปรษณีย์พบแล้วหลังการ Scroll")
                found = True
                break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องไปรษณีย์ '{POSTAL_CODE_EDIT_AUTO_ID}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return False # ยกเลิกการทำงานหากหาไม่พบ

        # [จุดที่ 2] ดำเนินการกรอกข้อมูล (เมื่อแน่ใจว่าพบแล้ว)
        if not postal_control.texts()[0].strip():
            # ถ้าช่องว่าง (Empty) ให้ทำการกรอก
            print(f" [-] -> ช่องว่าง, กรอก: {POSTAL_CODE}")
            postal_control.click_input() 
            main_window.type_keys(POSTAL_CODE)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {postal_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)
    
        # --- ค้นหาช่องหมายเลขโทรศัพท์และกรอกข้อมูล ---
        print(f"[*] 2.2. กำลังตรวจสอบ/กรอกเบอร์โทรศัพท์ ID='{PHONE_EDIT_AUTO_ID}'")
        phone_control = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    
        # [จุดที่ 2] ตรวจสอบ/Scroll ซ้ำเพื่อหาช่องเบอร์โทรศัพท์
        if not phone_control.exists(timeout=1):
            print("[!] ช่องเบอร์โทรศัพท์ไม่ปรากฏทันที, กำลังตรวจสอบ/เลื่อนหน้าจอซ้ำ...")
        
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if phone_control.exists(timeout=1):
                print("[/] ช่องเบอร์โทรศัพท์พบแล้วหลังการ Scroll")
                found = True
                break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องเบอร์โทรศัพท์ '{PHONE_EDIT_AUTO_ID}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return False # ยกเลิกการทำงานหากหาไม่พบ
    
        #  [จุดที่ 3] ดำเนินการกรอกข้อมูล (เมื่อแน่ใจว่าพบแล้ว)
        if not phone_control.texts()[0].strip():
            print(f" [-] -> ช่องว่าง, กรอก: {PHONE_NUMBER}")
            phone_control.click_input()
            main_window.type_keys(PHONE_NUMBER)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {phone_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)

        # 6. กด 'ถัดไป'
        print(f"[*] 6. กดปุ่ม '{NEXT_TITLE}'")
        main_window.child_window(title=NEXT_TITLE, auto_id=ID_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 7. กด ESC
        print(f"[*] 7. กดปุ่ม ESC เพื่อย้อนกลับ")
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