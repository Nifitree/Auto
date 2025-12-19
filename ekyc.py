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

# ดึง Section หลัก
B_CFG = CONFIG['EKYC_MAIN']
S_CFG = CONFIG['EKYC_SERVICES']

# ==================== 2. HELPERS ====================

def connect_main_window():
    """เชื่อมต่อหน้าต่างหลักของ POS"""
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()

def force_scroll_down(window):
    """เลื่อนหน้าจอลงเมื่อหา Object ไม่เจอ"""
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        center_x_offset = cfg.getint("CENTER_X_OFFSET")
        center_y_offset = cfg.getint("CENTER_Y_OFFSET")
        wheel_dist = cfg.getint("WHEEL_DIST")
        focus_delay = cfg.getfloat("FOCUS_DELAY")
        scroll_delay = cfg.getfloat("SCROLL_DELAY")
    except Exception:
        center_x_offset, center_y_offset, wheel_dist, focus_delay, scroll_delay = 300, 300, -20, 0.5, 1.0

    try:
        rect = window.rectangle()
        x = rect.left + center_x_offset
        y = rect.top + center_y_offset
        mouse.click(coords=(x, y))
        time.sleep(focus_delay)
        mouse.scroll(coords=(x, y), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)
    except Exception:
        window.type_keys("{PGDN}")

def scroll_until_found(control, window, max_scrolls=3):
    """วนลูป Scroll จนกว่าจะเจอ Object"""
    for _ in range(max_scrolls):
        if control.exists(timeout=1):
            return True
        force_scroll_down(window)
    return False

def fill_if_empty(window, control, value):
    """กรอกข้อมูลเฉพาะในกรณีที่ช่องว่าง"""
    if not control.texts()[0].strip():
        control.click_input()
        window.type_keys(value)

# ==================== 3. EKYC LOGIC ====================

def execute_ekyc_flow(main_window, service_title):
    """
    Flow: Agency -> BaS -> เลือกรายการ -> กรอกข้อมูล(ไปรษณีย์/เบอร์) -> ถัดไป -> ESC
    """
    # 1. เข้าเมนู Agency (A)
    print(f"[*] กดปุ่ม '{B_CFG['HOTKEY_AGENCY_TITLE']}'")
    main_window.child_window(title=B_CFG['HOTKEY_AGENCY_TITLE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    # 2. เข้าเมนู BaS (K)
    print(f"[*] กดปุ่ม '{B_CFG['HOTKEY_BaS_TITLE']}'")
    main_window.child_window(title=B_CFG['HOTKEY_BaS_TITLE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    # 3. เลือกรายการย่อย (Service)
    print(f"[*] เลือกรายการ: {service_title}")
    # ใช้ scroll_until_found เผื่อรายการอยู่ด้านล่าง
    service_btn = main_window.child_window(title=service_title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
    if not scroll_until_found(service_btn, main_window):
        raise Exception(f"ไม่พบรายการ {service_title}")
    service_btn.click_input()
    time.sleep(WAIT_TIME)

    # 4. ตรวจสอบและกรอกรหัสไปรษณีย์
    print(f"[*] ตรวจสอบรหัสไปรษณีย์")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(postal, main_window):
        raise Exception("ไม่พบช่องกรอกรหัสไปรษณีย์")
    fill_if_empty(main_window, postal, POSTAL_CODE)
    time.sleep(0.5)

    # 5. ตรวจสอบและกรอกเบอร์โทร
    print(f"[*] ตรวจสอบเบอร์โทรศัพท์")
    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(phone, main_window):
        raise Exception("ไม่พบช่องกรอกเบอร์โทรศัพท์")
    fill_if_empty(main_window, phone, PHONE_NUMBER)
    time.sleep(0.5)

    # 6. กดถัดไป
    print(f"[*] กดปุ่ม '{B_CFG['NEXT_TITLE']}'")
    main_window.child_window(
        title=B_CFG['NEXT_TITLE'], 
        auto_id=B_CFG['ID_AUTO_ID'], 
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    # 7. กด ESC เพื่อย้อนกลับ
    print(f"[*] กดปุ่ม ESC")
    main_window.type_keys("{ESC}")
    time.sleep(WAIT_TIME)

def run_service(step_name, service_title):
    """Wrapper สำหรับรัน Service พร้อมดัก Error"""
    app = None
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {step_name} (รหัส: {service_title})")
    try:
        app, main_window = connect_main_window()
        
        execute_ekyc_flow(main_window, service_title)
        
        print(f"[V] SUCCESS: {step_name} เสร็จสิ้น")

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "EKYC Automation",
            "step_name": step_name,
            "error_message": str(e)
        })
        print(f"[X] FAILED: {step_name} error: {e}")

# ==================== 4. MAIN EXECUTION ====================

if __name__ == "__main__":
    # ตรวจสอบและรัน Service ตามที่มีใน Config
    if 'EKYC_1_TITLE' in S_CFG:
        run_service("Service 1", S_CFG['EKYC_1_TITLE'])
        
    if 'EKYC_2_TITLE' in S_CFG:
        run_service("Service 2", S_CFG['EKYC_2_TITLE'])
        
    print(f"\n{'='*50}\n[V] จบการทำงานทั้งหมด")