import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse
from evidence import save_evidence_context
from app_context import AppContext
# --- [RESTORED] Imports เดิม ---
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
T_CFG = dict(CONFIG["PAYMENT"]) if CONFIG.has_section("PAYMENT") else {}

# Info Values (from MUTUAL_SERVICES section)
RECEIVE_PAYMENT_TITLE = S_CFG.get('RECEIVE_PAYMENT_TITLE', 'รับเงิน')
MEMBER_ID_VALUE = S_CFG.get('MEMBER_ID_VALUE', '')
MEMBER_ID_AUTO_ID = S_CFG.get('MEMBER_ID_AUTO_ID', '')
ACCOUNT_NUM_VALUE = S_CFG.get('ACCOUNT_NUM_VALUE', '')
ACCOUNT_NUM_AUTO_ID = S_CFG.get('ACCOUNT_NUM_AUTO_ID', '')
ACCOUNT_NAME_VALUE = S_CFG.get('ACCOUNT_NAME_VALUE', '')
ACCOUNT_NAME_AUTO_ID = S_CFG.get('ACCOUNT_NAME_AUTO_ID', '')
AMOUNT_TO_PAY_VALUE = S_CFG.get('AMOUNT_TO_PAY_VALUE', '')
AMOUNT_TO_PAY_AUTO_ID = S_CFG.get('AMOUNT_TO_PAY_AUTO_ID', '')
LOAN_TYPE_COMBO_ID = S_CFG.get('LOAN_TYPE_COMBO_ID', '')
# LOAN_A_SELECT = ชำระหนี้เงินกู้สามัญ
# LOAN_B_SELECT = ชำระหนี้เงินกู้พิเศษ
# LOAN_C_SELECT = ชำระหนี้เงินกู้ฉุกเฉิน
# LOAN_D_SELECT = ชำระหนี้เงินกู้ตามใบ
LOAN_TYPE_SELECT = S_CFG.get('LOAN_A_SELECT', '')

# Initialize AppContext & Payment
ctx = AppContext(window_title_regex=WINDOW_TITLE)
payment = PaymentFlow(CONFIG, ctx)

# ==================== HELPERS ====================

def connect_main_window():
    return ctx.connect()

def force_scroll_down(window):
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        center_x = cfg.getint("CENTER_X_OFFSET", fallback=300)
        center_y = cfg.getint("CENTER_Y_OFFSET", fallback=300)
        wheel_dist = cfg.getint("WHEEL_DIST", fallback=-20)
        mouse.scroll(
            coords=(window.rectangle().left + center_x, 
                    window.rectangle().top + center_y), 
            wheel_dist=wheel_dist
        )
        time.sleep(1.0)
    except:
        window.type_keys("{PGDN}")

def scroll_until_found(control, window, max_scrolls=3):
    if control.exists(timeout=1): return True
    for _ in range(max_scrolls):
        force_scroll_down(window)
        if control.exists(timeout=1): return True
    return False

def fill_if_empty(window, control, value):
    try:
        if not control.texts()[0].strip():
            control.click_input()
            time.sleep(0.5)
            control.type_keys(value, with_spaces=True)
    except: pass

# --- [ADDED NEW Helpers] เพิ่มให้สำหรับไฟล์ลูกใหม่ (ไม่ลบของเก่า) ---
def fill_field_by_id(window, auto_id, value, description=""):
    print(f"[*] Filling {description} ({auto_id}): {value}")
    control = window.child_window(auto_id=auto_id)
    if not scroll_until_found(control, window):
        raise Exception(f"Field not found: {description} (ID: {auto_id})")
    control.click_input()
    time.sleep(0.5)
    control.type_keys("^a{BACKSPACE}")
    control.type_keys(value, with_spaces=True)

def press_next_button(window):
    print("[*] Clicking Next...")
    next_btn = window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"])
    if next_btn.exists():
        next_btn.click_input()
    else:
        # Fallback
        ok_btn = window.child_window(title=S_CFG.get('OK_BUTTON_TITLE', 'ตกลง'))
        if ok_btn.exists(): ok_btn.click_input()
        else: window.type_keys("{ENTER}")
    time.sleep(WAIT_TIME)

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

# --- [RESTORED] ฟังก์ชันดั้งเดิมของคุณ ---
def run_mutual_transaction(main_window, title, barcode_id=None):
    """Transaction Logic (Original)"""
    print(f"[*] Selecting Item: {title}")
    target = main_window.child_window(title=title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
    
    if not scroll_until_found(target, main_window): 
        raise Exception(f"Item {title} not found")
        
    target.click_input()
    time.sleep(WAIT_TIME)

    # Barcode Logic
    if barcode_id:
        print(f"[*] Typing Barcode: {S_CFG.get('BARCODE_VALUE', '')}")
        barcode_ctrl = main_window.child_window(auto_id=barcode_id, control_type="Edit")
        # ใช้ wait visible เพื่อความชัวร์
        barcode_ctrl.wait('visible', timeout=WAIT_TIME).click_input()
        main_window.type_keys(S_CFG.get('BARCODE_VALUE', ''))
        time.sleep(0.5)
        
        print("[*] Clicking Next (Barcode Step)")
        main_window.child_window(title=B_CFG["NEXT_TITLE"], auto_id=B_CFG["NEXT_AUTO_ID"], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

    print("[*] Clicking OK/Next...")
    if barcode_id:
        ok_title = S_CFG.get('OK_BUTTON_TITLE', 'ตกลง')
        main_window.child_window(title=ok_title, control_type="Text").click_input()
    else:
        pass 
    
    time.sleep(WAIT_TIME)

def finish_transaction(main_window):
    """Finish Button (Original)"""
    print("[*] Clicking Finish...")
    main_window.child_window(title=B_CFG["FINISH_BUTTON_TITLE"], control_type="Text").click_input()
    time.sleep(WAIT_TIME)