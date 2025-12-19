import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys
from evidence import save_evidence_context

CONFIG_FILE = "config.ini"

# ==================== 1. CONFIGURATION ====================

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED: อ่าน config ไม่ได้: {e}")
        return configparser.ConfigParser()

CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้")
    sys.exit(1)

# ดึงค่า Global
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID'] 

B_CFG = CONFIG['EKYC_MAIN']
S_CFG = CONFIG['EKYC_SERVICES']

# ==================== 2. HELPERS ====================

def connect_main_window():
    """เชื่อมต่อหน้าต่างหลัก"""
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()

def force_scroll_down(window):
    """เลื่อนหน้าจอลง"""
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        center_x = cfg.getint("CENTER_X_OFFSET", fallback=300)
        center_y = cfg.getint("CENTER_Y_OFFSET", fallback=300)
        wheel_dist = cfg.getint("WHEEL_DIST", fallback=-20)
        focus_delay = cfg.getfloat("FOCUS_DELAY", fallback=0.5)
        scroll_delay = cfg.getfloat("SCROLL_DELAY", fallback=1.0)
        
        rect = window.rectangle()
        x = rect.left + center_x
        y = rect.top + center_y
        
        mouse.click(coords=(x, y))
        time.sleep(focus_delay)
        mouse.scroll(coords=(x, y), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)
    except Exception:
        window.type_keys("{PGDN}")

def check_and_scroll_find(main_window, control, error_msg):
    """
    Logic เดิมของคุณ: ตรวจสอบก่อน 1 รอบ ถ้าไม่เจอค่อยวนลูป Scroll
    """
    # 1. เช็คก่อน Scroll
    if not control.exists(timeout=1):
        print("[!] ไม่พบ Element ทันที... เริ่มการ Scroll")
        
        # 2. วนลูป Scroll (3 รอบ)
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window)
            if control.exists(timeout=1):
                print(f"[/] พบแล้วหลัง Scroll ครั้งที่ {i+1}")
                found = True
                break
        
        # 3. ถ้ายังไม่เจออีก -> RAISE ERROR (เพื่อให้ไปเข้า except แคปรูปและหยุด)
        if not found:
            raise Exception(f"{error_msg} (หาไม่เจอหลัง Scroll {max_scrolls} ครั้ง)")

    return True

def fill_if_empty(window, control, value):
    """กรอกข้อมูลถ้าช่องว่าง"""
    if not control.texts()[0].strip():
        control.click_input()
        window.type_keys(value)

# ==================== 3. EKYC LOGIC ====================

def execute_ekyc_transaction(main_window, service_title):
    # 1. เข้าเมนู
    print(f"[*] เข้าเมนู Agency -> BaS")
    main_window.child_window(title=B_CFG['HOTKEY_AGENCY_TITLE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)
    main_window.child_window(title=B_CFG['HOTKEY_BaS_TITLE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    # 2. เลือกรายการย่อย
    print(f"[*] เลือกรายการ: {service_title}")
    service_btn = main_window.child_window(title=service_title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
    
    # ใช้ Logic เดิม: เช็ค -> ถ้าไม่มีค่อย Scroll -> ถ้าไม่มีอีก Raise Error
    check_and_scroll_find(main_window, service_btn, f"ไม่พบปุ่มรายการ {service_title}")
    
    service_btn.click_input()
    time.sleep(WAIT_TIME)

    # 3. กรอกรหัสไปรษณีย์
    print(f"[*] กรอกรหัสไปรษณีย์")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    
    check_and_scroll_find(main_window, postal, "ไม่พบช่องรหัสไปรษณีย์")
    fill_if_empty(main_window, postal, POSTAL_CODE)
    time.sleep(0.5)

    # 4. กรอกเบอร์โทร
    print(f"[*] กรอกเบอร์โทรศัพท์")
    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    
    check_and_scroll_find(main_window, phone, "ไม่พบช่องเบอร์โทรศัพท์")
    fill_if_empty(main_window, phone, PHONE_NUMBER)
    time.sleep(0.5)

    # 5. กดถัดไป
    print(f"[*] กดถัดไป")
    main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['ID_AUTO_ID'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    # 6. กด ESC
    print(f"[*] กด ESC")
    main_window.type_keys("{ESC}")
    time.sleep(WAIT_TIME)

# ==================== 4. RUNNER (STOP ON ERROR) ====================

def run_service(step_name, service_title):
    """Wrapper: รัน -> ถ้าพัง -> แคป -> หยุดทันที (raise)"""
    app = None
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {step_name} (รหัส: {service_title})")
    
    try:
        app, main_window = connect_main_window()
        execute_ekyc_transaction(main_window, service_title)
        print(f"[V] SUCCESS: {step_name} สำเร็จ")

    except Exception as e:
        print(f"\n[X] FAILED: {step_name} -> {e}")
        
        # --- แคปภาพ (ทำงานแน่นอนถ้า connect ผ่านแล้ว) ---
        if app:
            try:
                save_evidence_context(app, {
                    "test_name": "EKYC Automation",
                    "step_name": step_name,
                    "error_message": str(e)
                })
                print("[/] บันทึกภาพ Error เรียบร้อย")
            except Exception as img_err:
                print(f"[!] บันทึกภาพไม่สำเร็จ: {img_err}")
        else:
            print("[!] ไม่สามารถบันทึกภาพได้ (Application ยังไม่ถูกเชื่อมต่อ)")

        # --- หยุดการทำงานทันที (CRITICAL) ---
        print("!!! หยุดการทำงานตามคำสั่ง (Stop Execution) !!!")
        raise e  # การใช้ raise จะทำให้โปรแกรม Crash และหยุดทันที ไม่ไปต่อ

# ==================== 5. ENTRY POINT ====================

if __name__ == "__main__":
    # การใช้ raise ด้านบนจะทำให้ script หยุดทำงานทันทีที่รายการใดรายการหนึ่งพัง
    
    if 'EKYC_1_TITLE' in S_CFG:
        run_service("EKYC_Service_1", S_CFG['EKYC_1_TITLE'])
        
    if 'EKYC_2_TITLE' in S_CFG:
        run_service("EKYC_Service_2", S_CFG['EKYC_2_TITLE'])
        
    print(f"\n{'='*50}\n[V] จบการทำงานทั้งหมด")