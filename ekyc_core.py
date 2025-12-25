# Save as: ekyc_core.py
import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse
from evidence import save_evidence_context
from app_context import AppContext

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
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

# EKYC Configs
B_CFG = CONFIG["EKYC_MAIN"]
S_CFG = CONFIG["EKYC_SERVICES"]

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

# ==================== CORE LOGIC ====================

def run_ekyc_step(service_name, service_title):
    print(f"\n{'='*50}\n[*] Starting: {service_name} (Code: {service_title})")
    
    # Config Shortcuts
    HOTKEY_A = B_CFG['HOTKEY_AGENCY_TITLE']
    HOTKEY_B = B_CFG['HOTKEY_BaS_TITLE']
    CTRL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_BTN = B_CFG['NEXT_TITLE']
    ID_AUTO = B_CFG['ID_AUTO_ID']
    
    app = None
    try:
        app, main_window = connect_main_window()
        print("[/] Connected to Window")

        # 1. Menu Navigation
        print(f"[*] 1. Pressing '{HOTKEY_A}' (Agency)")
        main_window.child_window(title=HOTKEY_A, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print(f"[*] 2. Pressing '{HOTKEY_B}' (BaS)")
        main_window.child_window(title=HOTKEY_B, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 2. Select Service
        print(f"[*] 3. Selecting Service: {service_title}")
        main_window.child_window(title=service_title, auto_id=CTRL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 3. Fill Postal Code
        print(f"[*] 4. Checking Postal Code (ID: {POSTAL_CODE_EDIT_AUTO_ID})")
        postal_ctrl = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        
        if not scroll_until_found(postal_ctrl, main_window):
            raise Exception(f"Postal Code field not found")

        if not postal_ctrl.texts()[0].strip():
            postal_ctrl.click_input()
            main_window.type_keys(POSTAL_CODE)
        time.sleep(0.5)
    
        # 4. Fill Phone Number
        print(f"[*] 5. Checking Phone Number (ID: {PHONE_EDIT_AUTO_ID})")
        phone_ctrl = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
        
        if not scroll_until_found(phone_ctrl, main_window):
            raise Exception(f"Phone Number field not found")
    
        if not phone_ctrl.texts()[0].strip():
            phone_ctrl.click_input()
            main_window.type_keys(PHONE_NUMBER)
        time.sleep(0.5)

        # 5. Press Next
        print(f"[*] 6. Pressing '{NEXT_BTN}'")
        main_window.child_window(title=NEXT_BTN, auto_id=ID_AUTO, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 6. Validation Check
        print("[*] Checking navigation result...")
        if phone_ctrl.exists(timeout=1):
            raise Exception("Still on input screen after Next (Validation Failed?)")

        # 7. Press ESC
        print(f"[*] 7. Pressing ESC to return")
        main_window.type_keys("{ESC}")
        time.sleep(WAIT_TIME)
        
        print(f"[V] SUCCESS: {service_name}")
        
    except Exception as e:
        if app:
            save_evidence_context(app, {"test_name": "EKYC", "step_name": service_name, "error_message": str(e)})
            print("[/] Evidence Saved")
        
        print(f"[X] FAILED: {e}")
        sys.exit(1)