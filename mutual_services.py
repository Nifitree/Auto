import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse

# Custom Modules
from payment_flow import PaymentFlow
from app_context import AppContext
from ui_helper import select_combobox_item
from evidence import save_evidence_context

# ==================== 1. CONFIGURATION SETUP ====================

CONFIG_FILE = "config.ini"

def read_config(filename=CONFIG_FILE):
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] Config file not found: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED reading config: {e}")
        return configparser.ConfigParser()

# Load Config
CONFIG = read_config()
if not CONFIG.sections():
    print("Cannot load config.ini")
    sys.exit()

# --- Global Constants ---
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE']
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

# --- Section Constants ---
B_CFG = CONFIG['MUTUAL_MAIN']
S_CFG = CONFIG['MUTUAL_SERVICES']
I_CFG = CONFIG['INFORMATION']

# --- Information Values ---
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

# Initialize Helpers
ctx = AppContext(window_title_regex=WINDOW_TITLE)
payment = PaymentFlow(CONFIG, ctx)

# ==================== 2. HELPER FUNCTIONS ====================

def force_scroll_down(window, config):
    """เลื่อนหน้าจอลงโดยใช้ Mouse wheel"""
    try:
        scroll_cfg = config['MOUSE_SCROLL']
        center_x = scroll_cfg.getint('CENTER_X_OFFSET', fallback=300)
        center_y = scroll_cfg.getint('CENTER_Y_OFFSET', fallback=300)
        wheel_dist = scroll_cfg.getint('WHEEL_DIST', fallback=-20)
        focus_delay = scroll_cfg.getfloat('FOCUS_DELAY', fallback=0.5)
        scroll_delay = scroll_cfg.getfloat('SCROLL_DELAY', fallback=1.0)
    except:
        center_x, center_y, wheel_dist = 300, 300, -20
        focus_delay, scroll_delay = 0.5, 1.0

    print(f"...Scrolling down (Wheel {wheel_dist})...")
    try:
        rect = window.rectangle()
        cx, cy = rect.left + center_x, rect.top + center_y
        mouse.click(coords=(cx, cy))
        time.sleep(focus_delay)
        mouse.scroll(coords=(cx, cy), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)
        print("[/] Scroll Success")
    except Exception:
        print("[!] Scroll failed, using PageDown")
        window.type_keys("{PGDN}")

def mutual_main():
    """Main Navigation: Home -> Mutual Fund -> ID Card -> Postal/Phone -> Next"""
    BUTTON_A = B_CFG['BUTTON_A_TITLE']
    BUTTON_M = B_CFG['BUTTON_M_TITLE']
    NEXT_BTN = B_CFG['NEXT_TITLE']
    NEXT_ID = B_CFG['NEXT_AUTO_ID']

    print(f"\n{'='*50}\n[*] 1. Navigating to Mutual Fund Service...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        print("[/] Connected to Window")

        # Navigation A -> M
        main_window.child_window(title=BUTTON_A, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        main_window.child_window(title=BUTTON_M, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # ID Card
        print(f"[*] 2.1. Clicking '{ID_CARD_BUTTON_TITLE}'...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

        # Postal Code
        print(f"[*] 2.2. Checking Postal Code (ID: {POSTAL_CODE_EDIT_AUTO_ID})")
        postal_ctrl = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        
        # Scroll logic
        if not postal_ctrl.exists(timeout=1):
            print("[!] Element not found, scrolling...")
            for _ in range(3):
                force_scroll_down(main_window, CONFIG)
                if postal_ctrl.exists(timeout=1):
                    break
        
        if not postal_ctrl.exists(timeout=1):
            print("[X] FAILED: Postal Code field not found.")
            return False

        if not postal_ctrl.texts()[0].strip():
            print(f" [-] Typing Postal: {POSTAL_CODE}")
            postal_ctrl.click_input()
            main_window.type_keys(POSTAL_CODE)
        time.sleep(0.5)

        # Phone Number
        print(f"[*] 2.3. Checking Phone Number (ID: {PHONE_EDIT_AUTO_ID})")
        phone_ctrl = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
        
        if not phone_ctrl.exists(timeout=1):
            for _ in range(3):
                force_scroll_down(main_window, CONFIG)
                if phone_ctrl.exists(timeout=1):
                    break

        if not phone_ctrl.exists(timeout=1):
            print("[X] FAILED: Phone field not found.")
            return False

        if not phone_ctrl.texts()[0].strip():
            print(f" [-] Typing Phone: {PHONE_NUMBER}")
            phone_ctrl.click_input()
            main_window.type_keys(PHONE_NUMBER)
        time.sleep(0.5)

        # Next
        print(f"[*] 2.4. Clicking '{NEXT_BTN}'...")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print("[V] Navigation Success!")
        return True

    except Exception as e:
        print(f"[X] Navigation Error: {e}")
        return False

def mutual_transaction(main_window, transaction_title, barcode_id_arg):
    """Shared function for Barcode transactions"""
    CTRL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_BTN = B_CFG['NEXT_TITLE']
    NEXT_ID = B_CFG['NEXT_AUTO_ID']
    FINISH_BTN = B_CFG['FINISH_BUTTON_TITLE']
    OK_BTN = S_CFG['OK_BUTTON_TITLE']
    BARCODE_VAL = S_CFG['BARCODE_VALUE']
    
    BARCODE_TITLES = [S_CFG['MUTUAL_1_TITLE'], S_CFG['MUTUAL_4_TITLE']]

    try:
        # Click Item
        print(f"[*] 2. Selecting Item: {transaction_title}")
        main_window.child_window(title=transaction_title, auto_id=CTRL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        if transaction_title in BARCODE_TITLES:
            print("--- [Special Step] Barcode Required ---")
            print(f"[*] 2.5. Typing Barcode: {BARCODE_VAL} (ID: {barcode_id_arg})")
            
            barcode_ctrl = main_window.child_window(auto_id=barcode_id_arg, control_type="Edit")
            barcode_ctrl.wait('visible', timeout=WAIT_TIME).click_input()
            main_window.type_keys(BARCODE_VAL)
            time.sleep(0.5)

            print(f"[*] 3. Clicking '{NEXT_BTN}'")
            main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
            time.sleep(WAIT_TIME)
            
        print(f"[*] Clicking '{OK_BTN}'")
        main_window.child_window(title=OK_BTN, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"[*] Clicking '{FINISH_BTN}'")
        main_window.child_window(title=FINISH_BTN, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

    except Exception as e:
        print(f"[X] Transaction Failed: {e}")
        raise e

# ==================== 3. SERVICE LOGIC FUNCTIONS ====================

def mutual_services1():
    print(f"\n{'='*50}\n[*] Running Service 1...")
    app = None
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        mutual_transaction(main_window, S_CFG['MUTUAL_1_TITLE'], S_CFG['BARCODE_EDIT_AUTO_ID'])
    except Exception as e:
        save_evidence_context(app, {"test_name": "Mutual", "step": "S1", "error": str(e)})
        print(f"[X] FAILED: {e}")

def mutual_services2():
    print(f"\n{'='*50}\n[*] Running Service 2 (4 Fields)...")
    try:
        if not mutual_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        TITLE = S_CFG['MUTUAL_2_TITLE']
        NEXT_BTN = B_CFG['NEXT_TITLE']
        NEXT_ID = B_CFG['NEXT_AUTO_ID']
        
        # Select Item
        print(f"[*] Selecting: {TITLE}")
        main_window.child_window(title=TITLE, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # Fill 4 Fields
        print("[*] Filling 4 fields...")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NUM_AUTO_ID).type_keys(ACCOUNT_NUM_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NAME_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # Flow: Next -> Next -> Receive -> Pay -> Next -> Next
        print(f"[*] Next (1)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print(f"[*] Next (2)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"[*] Receive Payment")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Payment Processing...")
        payment.pay_cash()
        
        print(f"[*] Next (3)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print(f"[*] Next (4 - Finish)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print("[V] Service 2 Success!")

    except Exception as e:
        save_evidence_context(app, {"test_name": "Mutual", "step": "S2", "error": str(e)})
        print(f"[X] FAILED: {e}")

def mutual_services3():
    print(f"\n{'='*50}\n[*] Running Service 3 (Combobox)...")
    try:
        if not mutual_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        TITLE = S_CFG['MUTUAL_3_TITLE']
        NEXT_BTN = B_CFG['NEXT_TITLE']
        NEXT_ID = B_CFG['NEXT_AUTO_ID']
        
        print(f"[*] Selecting: {TITLE}")
        main_window.child_window(title=TITLE, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print("[*] Filling Data & Combobox...")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
        time.sleep(0.5)
        
        select_combobox_item(main_window, LOAN_TYPE_COMBO_ID, LOAN_TYPE_SELECT, WAIT_TIME)
        time.sleep(WAIT_TIME)

        main_window.child_window(auto_id=ACCOUNT_NAME_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # Flow: Next -> Next -> Receive -> Pay -> Next -> Next
        print(f"[*] Next (1)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print(f"[*] Next (2)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"[*] Receive Payment")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print("[*] Payment Processing...")
        payment.pay_cash()
        
        print(f"[*] Next (3)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        print(f"[*] Next (4 - Finish)")
        main_window.child_window(title=NEXT_BTN, auto_id=NEXT_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print("[V] Service 3 Success!")

    except Exception as e:
        save_evidence_context(app, {"test_name": "Mutual", "step": "S3", "error": str(e)})
        print(f"[X] FAILED: {e}")

def mutual_services4():
    print(f"\n{'='*50}\n[*] Running Service 4...")
    try:
        if not mutual_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        TITLE = S_CFG['MUTUAL_4_TITLE']
        target = main_window.child_window(title=TITLE, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
        
        # Check & Scroll
        print(f"[*] Searching for item '{TITLE}'...")
        if not target.exists(timeout=1):
            for _ in range(3):
                force_scroll_down(main_window, CONFIG)
                if target.exists(timeout=1):
                    break
        
        if not target.exists(timeout=1):
            print("[X] Item not found.")
            return

        mutual_transaction(main_window, TITLE, S_CFG['BARCODE2_EDIT_AUTO_ID'])
        print("[V] Service 4 Success!")

    except Exception as e:
        print(f"[X] FAILED: {e}")

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    mutual_main()
    mutual_services1()
    mutual_services2()
    mutual_services3()
    mutual_services4()