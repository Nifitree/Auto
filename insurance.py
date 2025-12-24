import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
from evidence import save_evidence_context

# ชื่อไฟล์ Config
CONFIG_FILE = "config.ini"

# ==================== 1. CONFIGURATION ====================

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
        config.read(filename, encoding="utf-8")
        return config
    except Exception as e:
        print(f"[X] FAILED: อ่าน config ไม่ได้: {e}")
        return configparser.ConfigParser()

# โหลด config ล่วงหน้า
CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้")
    sys.exit(1)

# --- Global Config ---
WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
ID_CARD_BUTTON_TITLE = CONFIG["GLOBAL"]["ID_CARD_BUTTON_TITLE"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

# --- Insurance Specific Config (Changed from Bank) ---
B_CFG = CONFIG["INSURANCE_MAIN"]
S_CFG = CONFIG["INSURANCE_SERVICES"]

# ==================== 2. HELPERS ====================

def connect_main_window():
    """เชื่อมต่อหน้าต่างหลักของ POS"""
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()

def force_scroll_down(window):
    """เลื่อนหน้าจอลงเมื่อหา Object ไม่เจอ"""
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

# ==================== 3. MAIN NAVIGATION ====================

def insurance_navigate_main():
    """ขั้นตอนการนำทางเข้าหน้า Insurance และกรอกข้อมูลผู้ฝากส่ง"""
    try:
        app, main_window = connect_main_window()

        # 1. กดปุ่มเมนูหลัก (เช่น ปุ่ม N)
        print(f"[*] Clicking Main Menu Button: {B_CFG['BUTTON_N_TITLE']}")
        main_window.child_window(title=B_CFG['BUTTON_N_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 2. กดอ่านบัตรประชาชน
        print("[*] Reading ID Card...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

        # 3. กรอกรหัสไปรษณีย์
        print("[*] Checking Postal Code...")
        postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(postal, main_window):
            raise Exception("Postal Code field not found")
        fill_if_empty(main_window, postal, POSTAL_CODE)

        # 4. กรอกเบอร์โทร
        print("[*] Checking Phone Number...")
        phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(phone, main_window):
            raise Exception("Phone Number field not found")
        fill_if_empty(main_window, phone, PHONE_NUMBER)

        # 5. กดถัดไป
        print("[*] Clicking Next...")
        main_window.child_window(
            title=B_CFG["NEXT_BUTTON_TITLE"],
            auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        print("[V] SUCCESS: Navigated to Insurance Service Selection")
        return True

    except Exception as e:
        print(f"[X] FAILED: insurance_navigate_main error: {e}")
        return False

# ==================== 4. TRANSACTION ENGINE ====================

def run_insurance_transaction(main_window, title):
    """ทำรายการย่อย (คลิกรายการ -> ถัดไป -> เสร็จสิ้น)"""
    print(f"[*] Selecting Service: {title}")
    
    # 1. คลิกที่รายการย่อย
    target = main_window.child_window(
        title=title,
        auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"],
        control_type="Text"
    )
    
    # Scroll หาถ้าไม่เจอ
    if not scroll_until_found(target, main_window):
        raise Exception(f"Service item '{title}' not found after scrolling")
        
    target.click_input()
    time.sleep(WAIT_TIME)

    # 2. คลิกปุ่มถัดไป
    print("[*] Clicking Next...")
    main_window.child_window(
        title=B_CFG["NEXT_BUTTON_TITLE"],
        auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    # 3. กดปุ่มเสร็จสิ้น
    print("[*] Clicking Finish...")
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def run_service(step_name, service_title, use_main=True):
    """หุ้มการทำงานทั้งหมดพร้อมดักจับ Error เพื่อแคปภาพ"""
    app = None
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name} ({service_title})")
        
        # เริ่มต้นใหม่ทุกครั้งเพื่อให้ State หน้าจอถูกต้อง
        if use_main and not insurance_navigate_main():
            return

        app, main_window = connect_main_window()
        
        run_insurance_transaction(main_window, service_title)
        
        print(f"[V] SUCCESS: {step_name} Complete.")

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "Insurance POS Automation",
            "step_name": step_name,
            "error_message": str(e)
        })
        print(f"[X] FAILED: {step_name} error: {e}")

# ==================== 5. ENTRY POINT ====================

if __name__ == "__main__":
    # รายการ 1: เริ่มต้น (ใช้ use_main=True เพื่อเข้าหน้าแรก)
    run_service("Insurance_Service_1", S_CFG["TRANSACTION_1_TITLE"], use_main=True)
    
    # รายการ 2-6: ต่อเนื่อง
    run_service("Insurance_Service_2", S_CFG["TRANSACTION_2_TITLE"])
    run_service("Insurance_Service_3", S_CFG["TRANSACTION_3_TITLE"])
    run_service("Insurance_Service_4", S_CFG["TRANSACTION_4_TITLE"])
    run_service("Insurance_Service_5", S_CFG["TRANSACTION_5_TITLE"])
    run_service("Insurance_Service_6", S_CFG["TRANSACTION_6_TITLE"])

    print(f"\n{'='*50}\n[V] Insurance Automation Finished.")