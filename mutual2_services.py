import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys
from payment_flow import PaymentFlow
from app_context import AppContext
from ui_helper import select_combobox_item
from evidence import save_evidence_context

# ==================== CONFIG & SETUP ====================

def read_config(filename="config.ini"):
    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')
    return config

CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้"); exit()

# ดึงค่า Global
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

B_CFG, S_CFG, I_CFG = CONFIG['MUTUAL_MAIN'], CONFIG['MUTUAL_SERVICES'], CONFIG['INFORMATION']

# ข้อมูลสมาชิก/บัญชี
RECEIVE_PAYMENT_TITLE = I_CFG['RECEIVE_PAYMENT_TITLE']
MEMBER_ID_VALUE, MEMBER_ID_AUTO_ID = I_CFG['MEMBER_ID_VALUE'], I_CFG['MEMBER_ID_AUTO_ID'] 
ACCOUNT_NUM_VALUE, ACCOUNT_NUM_AUTO_ID = I_CFG['ACCOUNT_NUM_VALUE'], I_CFG['ACCOUNT_NUM_AUTO_ID'] 
ACCOUNT_NAME_VALUE, ACCOUNT_NAME_AUTO_ID = I_CFG['ACCOUNT_NAME_VALUE'], I_CFG['ACCOUNT_NAME_AUTO_ID']
AMOUNT_TO_PAY_VALUE, AMOUNT_TO_PAY_AUTO_ID = I_CFG['AMOUNT_TO_PAY_VALUE'], I_CFG['AMOUNT_TO_PAY_AUTO_ID']
LOAN_TYPE_COMBO_ID, LOAN_TYPE_SELECT = I_CFG['LOAN_TYPE_COMBO_ID'], I_CFG['LOAN_A_SELECT']

ctx = AppContext(window_title_regex=WINDOW_TITLE)
payment = PaymentFlow(CONFIG, ctx)

# ==================== HELPER FUNCTIONS ====================

def force_scroll_down(window, config):
    rect = window.rectangle()
    center_x = rect.left + config.getint('MOUSE_SCROLL', 'CENTER_X_OFFSET')
    center_y = rect.top + config.getint('MOUSE_SCROLL', 'CENTER_Y_OFFSET')
    mouse.click(coords=(center_x, center_y))
    time.sleep(0.5)
    mouse.scroll(coords=(center_x, center_y), wheel_dist=config.getint('MOUSE_SCROLL', 'WHEEL_DIST'))
    time.sleep(1.0)

def mutual_transaction(main_window, transaction_title, BARCODE_EDIT_AUTO_ID):
    """ฟังก์ชันแม่แบบ: ไม่ดัก Exception เอง แต่จะปล่อยให้ Error พุ่งไปหา Main"""
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_TITLE, NEXT_AUTO_ID = B_CFG['NEXT_TITLE'], B_CFG['NEXT_AUTO_ID']
    BARCODE_FLOW_TITLES = [S_CFG['MUTUAL_1_TITLE'], S_CFG['MUTUAL_4_TITLE']]

    main_window.child_window(title=transaction_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
    time.sleep(WAIT_TIME)

    if transaction_title in BARCODE_FLOW_TITLES:
        barcode_control = main_window.child_window(auto_id=BARCODE_EDIT_AUTO_ID, control_type="Edit")
        barcode_control.wait('visible', timeout=WAIT_TIME).click_input()
        main_window.type_keys(S_CFG['BARCODE_VALUE'])
        time.sleep(0.5)
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID).click_input()
        time.sleep(WAIT_TIME)

    main_window.child_window(title=S_CFG['OK_BUTTON_TITLE']).click_input()
    time.sleep(WAIT_TIME)
    main_window.child_window(title=B_CFG['FINISH_BUTTON_TITLE']).click_input()
    time.sleep(WAIT_TIME)

# ==================== NAV FLOW ====================

def mutual_main():
    print(f"\n[*] เริ่มต้นหน้าหลัก (A -> M -> อ่านบัตร)...")
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    main_window = app.top_window()
    
    main_window.child_window(title=B_CFG['BUTTON_A_TITLE']).click_input()
    time.sleep(WAIT_TIME)
    main_window.child_window(title=B_CFG['BUTTON_M_TITLE']).click_input()
    time.sleep(WAIT_TIME)
    main_window.child_window(title=ID_CARD_BUTTON_TITLE).click_input()

    postal_control = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    for _ in range(3):
        if postal_control.exists(): break
        force_scroll_down(main_window, CONFIG)

    if not postal_control.texts()[0].strip():
        postal_control.click_input(); main_window.type_keys(POSTAL_CODE)
    
    main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['NEXT_AUTO_ID']).click_input()
    time.sleep(WAIT_TIME)
    return True

# ==================== SERVICE FUNCTIONS (No internal Try-Except) ====================

def mutual_services1():
    print(f"[*] ดำเนินรายการ 1: {S_CFG['MUTUAL_1_TITLE']}")
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    mutual_transaction(app.top_window(), S_CFG['MUTUAL_1_TITLE'], S_CFG['BARCODE_EDIT_AUTO_ID'])

def mutual_services2():
    print(f"[*] ดำเนินรายการ 2: {S_CFG['MUTUAL_2_TITLE']}")
    if not mutual_main(): return
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    win = app.top_window()
    win.child_window(title=S_CFG['MUTUAL_2_TITLE']).click_input()
    time.sleep(WAIT_TIME)
    win.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
    win.child_window(auto_id=ACCOUNT_NUM_AUTO_ID).type_keys(ACCOUNT_NUM_VALUE)
    win.child_window(auto_id=ACCOUNT_NAME_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
    win.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
    win.child_window(title=B_CFG['NEXT_TITLE']).click_input()
    time.sleep(WAIT_TIME); win.child_window(title=B_CFG['NEXT_TITLE']).click_input()
    time.sleep(WAIT_TIME); win.child_window(title=RECEIVE_PAYMENT_TITLE).click_input()
    payment.pay_cash()
    win.child_window(title=B_CFG['FINISH_BUTTON_TITLE']).click_input()

def mutual_services3():
    print(f"[*] ดำเนินรายการ 3: {S_CFG['MUTUAL_3_TITLE']}")
    if not mutual_main(): return
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    win = app.top_window()
    win.child_window(title=S_CFG['MUTUAL_3_TITLE']).click_input()
    time.sleep(WAIT_TIME)
    win.child_window(auto_id=MEMBER_ID_AUTO_ID).type_keys(MEMBER_ID_VALUE)
    select_combobox_item(win, combo_auto_id=LOAN_TYPE_COMBO_ID, item_title=LOAN_TYPE_SELECT, sleep=WAIT_TIME)
    win.child_window(auto_id=ACCOUNT_NAME_AUTO_ID).type_keys(ACCOUNT_NAME_VALUE)
    win.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID).type_keys(AMOUNT_TO_PAY_VALUE)
    win.child_window(title=B_CFG['NEXT_TITLE']).click_input()
    time.sleep(WAIT_TIME); win.child_window(title=B_CFG['NEXT_TITLE']).click_input()
    time.sleep(WAIT_TIME); win.child_window(title=RECEIVE_PAYMENT_TITLE).click_input()
    payment.pay_cash()
    win.child_window(title=B_CFG['FINISH_BUTTON_TITLE']).click_input()

def mutual_services4():
    print(f"[*] ดำเนินรายการ 4: {S_CFG['MUTUAL_4_TITLE']}")
    if not mutual_main(): return
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    win = app.top_window()
    target = win.child_window(title=S_CFG['MUTUAL_4_TITLE'])
    for _ in range(3):
        if target.exists(): break
        force_scroll_down(win, CONFIG)
    mutual_transaction(win, S_CFG['MUTUAL_4_TITLE'], S_CFG['BARCODE2_EDIT_AUTO_ID'])

# ==================== MAIN EXECUTION (GLOBAL ERROR HANDLER) ====================

if __name__ == "__main__":
    current_app = None
    try:
        # เชื่อมต่อแอป
        current_app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        
        # ลำดับการรัน
        mutual_services1()
        mutual_services2()
        mutual_services3()
        mutual_services4()
        
        print("\n[V] SUCCESS: ทำงานครบทุกรายการ!")

    except Exception as e:
        # 📸 ดักจับทุกความผิดพลาด ณ จุดเดียว
        print(f"\n[X] GLOBAL ERROR DETECTED: {e}")
        error_context = {
            "test_name": "Mutual Services Overall Test",
            "step_name": "Global_Handler_Catch",
            "error_message": str(e)
        }
        # บันทึกรูปและ JSON
        save_evidence_context(current_app, error_context)
        print("[!] บันทึกหลักฐานเรียบร้อยในโฟลเดอร์ /evidence")