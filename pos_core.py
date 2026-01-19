# Save as: pos_core.py
import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse
from evidence import save_evidence_context
from app_context import AppContext
# [จุดแก้ไข 1] Import Helper เพื่อให้ไฟล์ลูก (pos_1.py) เรียกใช้ได้
from ui_helper import select_combobox_item 

CONFIG_FILE = "config.ini"

# ==================== CONFIGURATION ====================

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] Config not found: {filename}")
            return configparser.ConfigParser()
        config.read(filename, encoding="utf-8")
        return config
    except Exception as e:
        print(f"[X] Config Error: {e}")
        return configparser.ConfigParser()

CONFIG = read_config()
if not CONFIG.sections():
    print("Cannot load config.ini")
    sys.exit(1)

# Global Configs
WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
ID_CARD_BUTTON_TITLE = CONFIG["GLOBAL"]["ID_CARD_BUTTON_TITLE"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

# POS Configs
B_CFG = CONFIG["PRAISANI_POS_MAIN"]
S_CFG = CONFIG["PRAISANI_POS_SERVICES"]

# [จุดแก้ไข 2] โหลด Config ส่วน Payment
T_CFG = CONFIG["PAYMENT"]
RECEIVE_PAYMENT_TITLE = S_CFG.get('RECEIVE_PAYMENT_TITLE', 'รับเงิน')

# Initialize AppContext
ctx = AppContext(window_title_regex=WINDOW_TITLE)

# ==================== HELPERS ====================

def connect_main_window():
    return ctx.connect()

def force_scroll_down(window):
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        mouse.scroll(
            coords=(window.rectangle().left + cfg.getint("CENTER_X_OFFSET"), 
                    window.rectangle().top + cfg.getint("CENTER_Y_OFFSET")), 
            wheel_dist=cfg.getint("WHEEL_DIST")
        )
        time.sleep(1.0)
    except:
        window.type_keys("{PGDN}")

def scroll_until_found(control, window, max_scrolls=3):
    for _ in range(max_scrolls):
        if control.exists(timeout=1): return True
        force_scroll_down(window)
    return False

def fill_if_empty(window, control, value):
    if not control.texts()[0].strip():
        control.click_input()
        window.type_keys(value)

# ==================== CORE LOGIC ====================

def pos_services_main():
    """Logic เข้าเมนู A -> P -> อ่านบัตร -> กรอกข้อมูล"""
    try:
        app, main_window = connect_main_window()
        print(f"[*] Navigating to POS Main ({B_CFG['HOTKEY_AGENCY_TITLE']} -> {B_CFG['HOTKEY_BaS_TITLE']})...")
        
        main_window.child_window(title=B_CFG['HOTKEY_AGENCY_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        main_window.child_window(title=B_CFG['HOTKEY_BaS_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Reading ID Card...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

        print("[*] Checking Postal Code...")
        postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(postal, main_window): raise Exception("Postal not found")
        fill_if_empty(main_window, postal, POSTAL_CODE)

        print("[*] Checking Phone...")
        phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(phone, main_window): raise Exception("Phone not found")
        fill_if_empty(main_window, phone, PHONE_NUMBER)

        print("[*] Clicking Next...")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        return True
    except Exception as e:
        print(f"[X] Navigation Failed: {e}")
        return False

def run_pos_transaction(main_window, title):
    """ทำรายการย่อย (เลือก -> ถัดไป -> เสร็จสิ้น)"""
    print(f"[*] Selecting Item: {title}")
    main_window.child_window(title=title, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    print("[*] Clicking Next...")
    main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["ID_AUTO_ID"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    print("[*] Clicking Finish...")
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def run_service(step_name, service_title, use_main=True, use_search=False):
    """Wrapper หลักสำหรับเรียกจากไฟล์ลูก"""
    app = None
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name} ({service_title})")
        
        app, main_window = connect_main_window()

        if use_main and not pos_services_main():
            return

        if use_search:
            print(f"[*] Searching for code: {service_title}")
            search_input = main_window.child_window(auto_id=S_CFG["SEARCH_EDIT_ID"], control_type="Edit")
            search_input.click_input()
            search_input.type_keys("^a{BACKSPACE}")
            search_input.type_keys(service_title, with_spaces=True)
            search_input.type_keys("{ENTER}")
            time.sleep(1.5)

            target = main_window.child_window(title=service_title, control_type="Text")
            if not target.exists(timeout=3):
                raise Exception(f"Service {service_title} not found in search results")

        run_pos_transaction(main_window, service_title)
        print(f"[V] SUCCESS: {step_name}")

    except Exception as e:
        target_app = app if (app is not None) else ctx.app
        if target_app:
            save_evidence_context(target_app, {
                "test_name": "Praisani POS",
                "step_name": step_name,
                "error_message": str(e)
            })
            print("[/] Evidence Saved")
        print(f"[X] FAILED: {e}")