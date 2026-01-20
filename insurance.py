import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
from evidence import save_evidence_context
from app_context import AppContext

CONFIG_FILE = "config.ini"

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

# Insurance Configs
B_CFG = CONFIG["INSURANCE_MAIN"]
S_CFG = CONFIG["INSURANCE_SERVICES"]
ctx = AppContext(window_title_regex=WINDOW_TITLE)

# Helpers
def connect_main_window():
    return ctx.connect()

def force_scroll_down(window):
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        # Scroll logic simplified for core
        mouse.scroll(coords=(window.rectangle().left + cfg.getint("CENTER_X_OFFSET"), window.rectangle().top + cfg.getint("CENTER_Y_OFFSET")), wheel_dist=cfg.getint("WHEEL_DIST"))
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

def insurance_navigate_main():
    """Logic เข้าเมนู N -> อ่านบัตร -> กรอกข้อมูล"""
    try:
        app, main_window = connect_main_window()
        print(f"[*] Navigating to Insurance Main ({B_CFG['BUTTON_N_TITLE']})...")
        main_window.child_window(title=B_CFG['BUTTON_N_TITLE'], control_type="Text").click_input()
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
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        return True
    except Exception as e:
        print(f"[X] Navigation Failed: {e}")
        return False

def run_service(step_name, service_title):
    """Logic ทำรายการย่อย (เรียกใช้จากไฟล์ลูก)"""
    app = None
    try:
        print(f"\n{'='*50}\n[*] Starting: {step_name} ({service_title})")
        if not insurance_navigate_main(): return

        app, main_window = connect_main_window()
        
        print(f"[*] Selecting Service: {service_title}")
        target = main_window.child_window(title=service_title, auto_id=S_CFG["TRANSACTION_CONTROL_TYPE"], control_type="Text")
        if not scroll_until_found(target, main_window): raise Exception(f"Service {service_title} not found")
        target.click_input()
        time.sleep(WAIT_TIME)

        print("[*] Clicking Next...")
        main_window.child_window(title=B_CFG["NEXT_BUTTON_TITLE"], auto_id=B_CFG["NEXT_BUTTON_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Clicking Finish...")
        main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print(f"[V] SUCCESS: {step_name}")

    except Exception as e:
        save_evidence_context(app, {"test_name": "Insurance", "step_name": step_name, "error_message": str(e)})
        print(f"[X] FAILED: {e}")