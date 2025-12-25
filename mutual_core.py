# Save as: mutual_core.py
import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse
from evidence import save_evidence_context
from app_context import AppContext
from ui_helper import select_combobox_item
from payment_flow import PaymentFlow

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

# Mutual Configs
B_CFG = CONFIG["MUTUAL_MAIN"]
S_CFG = CONFIG["MUTUAL_SERVICES"]
T_CFG = CONFIG["PAYMENT"]
I_CFG = CONFIG["INFORMATION"]

# Info Values
RECEIVE_PAYMENT_TITLE = I_CFG['RECEIVE_PAYMENT_TITLE']
MEMBER_ID_VALUE = I_CFG['MEMBER_ID_VALUE']
MEMBER_ID_AUTO_ID = I_CFG['MEMBER_ID_AUTO_ID'] 
ACCOUNT_NUM_VALUE = I_CFG['ACCOUNT_NUM_VALUE']
ACCOUNT_NUM_AUTO_ID = I_CFG['ACCOUNT_NUM_AUTO_ID'] 
ACCOUNT_NAME_VALUE = I_CFG['ACCOUNT_NAME_VALUE']
ACCOUNT_NAME_AUTO_ID = I_CFG['ACCOUNT_NAME_AUTO_ID']
AMOUNT_TO_PAY_VALUE = I_CFG['AMOUNT_TO_PAY_VALUE']
AMOUNT_TO_PAY_AUTO_ID = I_CFG['AMOUNT_TO_PAY_AUTO_ID']
LOAN_TYPE_COMBO_ID = I_CFG['LOAN_TYPE_COMBO_ID']
LOAN_TYPE_SELECT = I_CFG['LOAN_A_SELECT']

# Initialize AppContext & Payment
ctx = AppContext(window_title_regex=WINDOW_TITLE)
payment = PaymentFlow(CONFIG, ctx)

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

def mutual_main():
    """Logic เข้าเมนู A -> M -> อ่านบัตร -> กรอกข้อมูล"""
    try:
        app, main_window = connect_main_window()
        print(f"[*] Navigating to Mutual Main ({B_CFG['BUTTON_A_TITLE']} -> {B_CFG['BUTTON_M_TITLE']})...")
        
        main_window.child_window(title=B_CFG['BUTTON_A_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        main_window.child_window(title=B_CFG['BUTTON_M_TITLE'], control_type="Text").click_input()
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
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        return True
    except Exception as e:
        print(f"[X] Navigation Failed: {e}")
        return False

def run_mutual_transaction(main_window, title, barcode_id=None):
    """Transaction Logic"""
    print(f"[*] Selecting Item: {title}")
    target = main_window.child_window(title=title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
    
    if not scroll_until_found(target, main_window): 
        # Check if item needs scrolling
        raise Exception(f"Item {title} not found")
        
    target.click_input()
    time.sleep(WAIT_TIME)

    # Barcode Logic
    if barcode_id:
        print(f"[*] Typing Barcode: {S_CFG['BARCODE_VALUE']}")
        barcode_ctrl = main_window.child_window(auto_id=barcode_id, control_type="Edit")
        barcode_ctrl.wait('visible', timeout=WAIT_TIME).click_input()
        main_window.type_keys(S_CFG['BARCODE_VALUE'])
        time.sleep(0.5)
        
        print("[*] Clicking Next (Barcode Step)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

    print("[*] Clicking OK/Next...")
    # Logic สำหรับกด OK หรือ Next ตาม Flow ปกติ
    if barcode_id:
        main_window.child_window(title=S_CFG['OK_BUTTON_TITLE'], control_type="Text").click_input()
    else:
        # Flow ปกติ (Service 2, 3) จะมี Logic แยกในไฟล์ Runner
        pass 
    
    time.sleep(WAIT_TIME)

def finish_transaction(main_window):
    print("[*] Clicking Finish...")
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)