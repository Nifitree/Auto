import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
from evidence import save_evidence_context
from app_context import AppContext

CONFIG_FILE = "config.ini"

# ==================== 1. CONFIGURATION ====================

def read_config(filename=CONFIG_FILE):
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

B_CFG = CONFIG["BANKING_MAIN"]
S_CFG = CONFIG["BANKING_SERVICES"]
ctx = AppContext(window_title_regex=WINDOW_TITLE)

# ==================== 2. HELPERS ====================

def connect_main_window():
    """เชื่อมต่อหน้าต่างหลักของ POS"""
    return ctx.connect()

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

# ==================== 3. NAVIGATION ====================

def banking_services_main():
    """ขั้นตอนการนำทางเข้าหน้าบริการธนาคารและกรอกข้อมูลผู้ฝาก"""
    try:
        app, main_window = connect_main_window()

        # กดปุ่ม A (Agency)
        main_window.child_window(title=B_CFG['HOTKEY_AGENCY_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # กดปุ่ม B (BaS)
        main_window.child_window(title=B_CFG['HOTKEY_BaS_TITLE'], control_type="Text").click_input()
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
            title=B_CFG["NEXT_TITLE"],
            auto_id=B_CFG["ID_AUTO_ID"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        print("[V] SUCCESS: เตรียมหน้าบริการธนาคารสำเร็จ")
        return True

    except Exception as e:
        print(f"[X] FAILED: banking_services_main error: {e}")
        return False

# ==================== 4. TRANSACTION ENGINE ====================

def run_banking_transaction(main_window, title, double_next=False):
    """
    ทำรายการย่อย:
    - double_next=False: คลิกรายการ -> ถัดไป -> เสร็จสิ้น (ปกติ)
    - double_next=True: คลิกรายการ -> ถัดไป -> ถัดไป -> เสร็จสิ้น (สำหรับรายการที่ 1)
    """
    # คลิกที่รายการย่อย
    main_window.child_window(
        title=title,
        auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    # คลิกปุ่มถัดไป (ครั้งที่ 1)
    main_window.child_window(
        title=B_CFG["NEXT_TITLE"],
        auto_id=B_CFG["ID_AUTO_ID"],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    # ถ้าเป็นโหมด Double Next (สำหรับรายการ 1) ให้กดถัดไปอีกครั้ง
    if double_next:
        print("[*] กดปุ่มถัดไปครั้งที่ 2 (ตาม Logic รายการที่ 1)")
        main_window.child_window(
            title=B_CFG["NEXT_TITLE"],
            auto_id=B_CFG["ID_AUTO_ID"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

    # กดปุ่มเสร็จสิ้น
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def run_service(step_name, service_title, use_main=True, use_search=False, double_next=False):
    """Wrapper หลักสำหรับรันแต่ละ Service พร้อมระบบ Search และ Error Handling"""
    app = None
    try:
        # เริ่มต้นใหม่ทุกครั้งเพื่อให้ State หน้าจอถูกต้อง
        if use_main and not banking_services_main():
            return

        app, main_window = connect_main_window()
        
        # ส่วนจัดการการค้นหา (Search) สำหรับรายการ 6-15
        if use_search:
            print(f"[*] ค้นหารหัสรายการ: {service_title}")
            search_input = main_window.child_window(auto_id=S_CFG["SEARCH_EDIT_ID"], control_type="Edit")
            search_input.click_input()
            search_input.type_keys("^a{BACKSPACE}") # ลบค่าเก่า
            search_input.type_keys(service_title, with_spaces=True)
            search_input.type_keys("{ENTER}")
            time.sleep(1.5)

            # ตรวจสอบว่ารายการขึ้นมาหรือไม่
            target = main_window.child_window(title=service_title, control_type="Text")
            if not target.exists(timeout=3):
                raise Exception(f"ไม่พบรายการ {service_title} จากการ Search")

        # เรียกใช้ Transaction Logic
        run_banking_transaction(main_window, service_title, double_next=double_next)
        print(f"[V] SUCCESS: {step_name} ({service_title}) ดำเนินการสำเร็จ")

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "Banking Services Automation",
            "step_name": step_name,
            "error_message": str(e)
        })
        print(f"[X] FAILED: {step_name} error: {e}")

# ==================== 5. ENTRY POINT ====================

if __name__ == "__main__":
    # รายการ 1: ใช้ double_next=True (กดถัดไป 2 ครั้ง) และใช้ use_main=True เพื่อเริ่มระบบ
    run_service("banking_services1", S_CFG["BANKING_1_TITLE"], use_main=True, double_next=True)
    
    # รายการ 2-5: แบบปกติ (กดถัดไป 1 ครั้ง)
    run_service("banking_services2", S_CFG["BANKING_2_TITLE"])
    run_service("banking_services3", S_CFG["BANKING_3_TITLE"])
    run_service("banking_services4", S_CFG["BANKING_4_TITLE"])
    run_service("banking_services5", S_CFG["BANKING_5_TITLE"])
    
    # รายการ 6-15: ใช้ระบบ Search
    # เราใช้ Loop รันได้เลยเพราะ Logic เหมือนกันหมด
    for i in range(6, 16):
        title_key = f"BANKING_{i}_TITLE"
        step_name = f"banking_services{i}"
        
        if title_key in S_CFG:
            run_service(step_name, S_CFG[title_key], use_search=True)

    print(f"\n{'='*50}\n[V] จบพาร์ท Banking Services ทั้งหมด")