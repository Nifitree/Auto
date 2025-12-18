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

# ดึงค่า Global
WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
ID_CARD_BUTTON_TITLE = CONFIG["GLOBAL"]["ID_CARD_BUTTON_TITLE"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

B_CFG = CONFIG["BANK_POS_MAIN"]
S_CFG = CONFIG["BANK_POS_SUB_TRANSACTIONS"]

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

# ==================== 3. MAIN NAVIGATION ====================

def bank_pos_navigate_main():
    """ขั้นตอนการนำทางเข้าหน้า 'ผู้ฝากส่ง' และกรอกข้อมูล"""
    try:
        app, main_window = connect_main_window()

        # กดปุ่มฟังก์ชัน N
        main_window.child_window(title=B_CFG['BUTTON_N_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # กดอ่านบัตรประชาชน
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

        # ตรวจสอบและกรอกรหัสไปรษณีย์
        postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(postal, main_window):
            return False
        fill_if_empty(main_window, postal, POSTAL_CODE)

        # ตรวจสอบและกรอกเบอร์โทร
        phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(phone, main_window):
            return False
        fill_if_empty(main_window, phone, PHONE_NUMBER)

        # กดถัดไป
        main_window.child_window(
            title=B_CFG["NEXT_BUTTON_TITLE"],
            auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        print("[V] SUCCESS: เตรียมหน้าข้อมูลผู้ฝากส่งสำเร็จ")
        return True

    except Exception as e:
        print(f"[X] FAILED: bank_pos_navigate_main error: {e}")
        return False

# ==================== 4. TRANSACTION ENGINE ====================

def run_bank_transaction(main_window, title):
    """ทำรายการย่อย (คลิกรายการ -> ถัดไป -> เสร็จสิ้น)"""
    # คลิกที่รายการย่อย
    main_window.child_window(
        title=title,
        auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    # คลิกปุ่มถัดไป
    main_window.child_window(
        title=B_CFG["NEXT_BUTTON_TITLE"],
        auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    # กดปุ่มเสร็จสิ้น
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def run_service(step_name, service_title, use_main=True):
    """หุ้มการทำงานทั้งหมดพร้อมดักจับ Error เพื่อแคปภาพ"""
    app = None
    try:
        # เริ่มต้นใหม่ทุกครั้งเพื่อให้ State หน้าจอถูกต้อง
        if use_main and not bank_pos_navigate_main():
            return

        app, main_window = connect_main_window()
        
        # ตรวจสอบว่ารายการอยู่บนหน้าจอหรือไม่ (ถ้าไม่อยู่ให้ Scroll หา)
        target = main_window.child_window(title=service_title, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text")
        if not scroll_until_found(target, main_window):
            raise Exception(f"ไม่พบรายการ {service_title} หลังการ Scroll")

        run_bank_transaction(main_window, service_title)
        print(f"[V] SUCCESS: {step_name} ({service_title}) ดำเนินการสำเร็จ")

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "Bank POS Automation",
            "step_name": step_name,
            "error_message": str(e)
        })
        print(f"[X] FAILED: {step_name} error: {e}")

# ==================== 5. ENTRY POINT ====================

if __name__ == "__main__":
    # รันรายการ 1-6 โดยใช้ระบบ Engine กลาง
    # รายการ 1: เริ่มต้น (ใช้ use_main=True เพื่อความเสถียรตามที่คุณต้องการ)
    run_service("bank_pos_navigate1", S_CFG["TRANSACTION_1_TITLE"], use_main=True)
    
    run_service("bank_pos_navigate2", S_CFG["TRANSACTION_2_TITLE"])
    run_service("bank_pos_navigate3", S_CFG["TRANSACTION_3_TITLE"])
    run_service("bank_pos_navigate4", S_CFG["TRANSACTION_4_TITLE"])
    run_service("bank_pos_navigate5", S_CFG["TRANSACTION_5_TITLE"])
    run_service("bank_pos_navigate6", S_CFG["TRANSACTION_6_TITLE"])

    print(f"\n{'='*50}\n[V] จบพาร์ท Bank POS ทั้งหมด")