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

B_CFG = CONFIG["GOODSPM_MAIN"]
S_CFG = CONFIG["GOODSPM_SERVICES"]

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

# ==================== 3. NAVIGATION ====================

def goods_pm_main():
    """ขั้นตอนการนำทางเข้าหน้าบริการชำระค่าสินค้า A -> G -> กรอกข้อมูล"""
    try:
        app, main_window = connect_main_window()

        # กดปุ่ม A (Agency)
        main_window.child_window(title=B_CFG['BT_A_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # กดปุ่ม G (Goods Payment)
        main_window.child_window(title=B_CFG['BT_G_TITLE'], control_type="Text").click_input()
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
            auto_id=B_CFG["NEXT_AUTO_ID"],
            control_type="Text"
        ).click_input()
        time.sleep(WAIT_TIME)

        print("[V] SUCCESS: เตรียมหน้าบริการชำระค่าสินค้าสำเร็จ")
        return True

    except Exception as e:
        print(f"[X] FAILED: goods_pm_main error: {e}")
        return False

# ==================== 4. TRANSACTION ENGINE ====================

def run_goods_transaction(main_window, title):
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
        title=B_CFG["NEXT_TITLE"],
        auto_id=B_CFG["NEXT_AUTO_ID"],
        control_type="Text"
    ).click_input()
    time.sleep(WAIT_TIME)

    # กดปุ่มเสร็จสิ้น
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def run_service(step_name, service_title, use_main=True, use_search=False):
    """Wrapper สำหรับรันแต่ละ Service พร้อมระบบ Search และ Error Handling"""
    app = None
    try:
        # เริ่มต้นใหม่ทุกครั้งเพื่อให้ State หน้าจอถูกต้อง
        if use_main and not goods_pm_main():
            return

        app, main_window = connect_main_window()
        
        # ส่วนจัดการการค้นหา (Search) สำหรับรายการ 7-9
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
        run_goods_transaction(main_window, service_title)
        print(f"[V] SUCCESS: {step_name} ({service_title}) ดำเนินการสำเร็จ")

    except Exception as e:
        save_evidence_context(app, {
            "test_name": "Goods Payment Automation",
            "step_name": step_name,
            "error_message": str(e)
        })
        print(f"[X] FAILED: {step_name} error: {e}")

# ==================== 5. ENTRY POINT ====================

if __name__ == "__main__":
    # รายการ 1-6: แบบปกติ (ไม่ต้อง Search)
    # ใช้ use_main=True ทุกรายการเพื่อความเสถียร (Reset หน้าจอทุกรอบ)
    run_service("goods_pm_services1", S_CFG["GOODSPM_1_TITLE"], use_main=True)
    run_service("goods_pm_services2", S_CFG["GOODSPM_2_TITLE"])
    run_service("goods_pm_services3", S_CFG["GOODSPM_3_TITLE"])
    run_service("goods_pm_services4", S_CFG["GOODSPM_4_TITLE"])
    run_service("goods_pm_services5", S_CFG["GOODSPM_5_TITLE"])
    run_service("goods_pm_services6", S_CFG["GOODSPM_6_TITLE"])
    
    # รายการ 7-9: ใช้ระบบ Search
    for i in range(7, 10):
        title_key = f"GOODSPM_{i}_TITLE"
        step_name = f"goods_pm_services{i}"
        
        if title_key in S_CFG:
            run_service(step_name, S_CFG[title_key], use_search=True)

    print(f"\n{'='*50}\n[V] จบพาร์ท Goods Payment ทั้งหมด")