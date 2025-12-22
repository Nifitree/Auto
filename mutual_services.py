import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys

# Import Custom Modules
from payment_flow import PaymentFlow
from app_context import AppContext
from ui_helper import select_combobox_item
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

# Global Config
WINDOW_TITLE = CONFIG["GLOBAL"]["WINDOW_TITLE"]
WAIT_TIME = CONFIG.getint("GLOBAL", "WAIT_TIME_SEC")
PHONE_NUMBER = CONFIG["GLOBAL"]["PHONE_NUMBER"]
ID_CARD_BUTTON_TITLE = CONFIG["GLOBAL"]["ID_CARD_BUTTON_TITLE"]
PHONE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["PHONE_EDIT_AUTO_ID"]
POSTAL_CODE = CONFIG["GLOBAL"]["POSTAL_CODE"]
POSTAL_CODE_EDIT_AUTO_ID = CONFIG["GLOBAL"]["POSTAL_CODE_EDIT_AUTO_ID"]

# Config เฉพาะ Mutual
B_CFG = CONFIG["MUTUAL_MAIN"]
S_CFG = CONFIG["MUTUAL_SERVICES"]
I_CFG = CONFIG["INFORMATION"]

# Payment Flow Setup
ctx = AppContext(window_title_regex=WINDOW_TITLE)
payment = PaymentFlow(CONFIG, ctx)

# ==================== 2. HELPERS (STANDARD) ====================

def connect_main_window():
    """เชื่อมต่อหน้าต่างหลัก"""
    app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
    return app, app.top_window()

def force_scroll_down(window):
    """เลื่อนหน้าจอลง"""
    try:
        cfg = CONFIG["MOUSE_SCROLL"]
        center_x = cfg.getint("CENTER_X_OFFSET", fallback=300)
        center_y = cfg.getint("CENTER_Y_OFFSET", fallback=300)
        wheel_dist = cfg.getint("WHEEL_DIST", fallback=-20)
        focus_delay = cfg.getfloat("FOCUS_DELAY", fallback=0.5)
        scroll_delay = cfg.getfloat("SCROLL_DELAY", fallback=1.0)
        
        rect = window.rectangle()
        x = rect.left + center_x
        y = rect.top + center_y
        
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
    """กรอกข้อมูลถ้าช่องว่าง"""
    if not control.texts()[0].strip():
        control.click_input()
        window.type_keys(value)

# ==================== 3. DYNAMIC PAYMENT LOGIC ====================

def perform_dynamic_payment(payment_obj):
    """
    อ่านค่า METHOD จาก [PAYMENT_CONFIG] ใน config.ini
    และเลือกฟังก์ชันการจ่ายเงินที่ถูกต้อง
    """
    try:
        method = CONFIG.get('PAYMENT_CONFIG', 'METHOD', fallback='CASH').upper().strip()
    except:
        method = 'CASH'

    print(f"[*] กำลังดำเนินการชำระเงินด้วยวิธี: {method}")

    if method == 'CASH':
        payment_obj.pay_cash()
    elif method == 'QR':
        payment_obj.pay_qr()
    elif method == 'CREDIT':
        payment_obj.pay_credit()
    elif method == 'DEBIT':
        payment_obj.pay_debit()
    elif method == 'CHECK':
        payment_obj.pay_check()
    elif method == 'ALIPAY':
        payment_obj.pay_alipay()
    elif method == 'WECHAT':
        payment_obj.pay_wechat()
    elif method == 'THP':
        payment_obj.pay_thp()
    elif method == 'TRUEMONEY':
        payment_obj.pay_truemoney()
    elif method == 'QR_CREDIT':
        payment_obj.pay_qr_credit()
    else:
        print(f"[!] ไม่พบวิธีชำระเงิน '{method}' ในระบบ -> ใช้เงินสดแทน")
        payment_obj.pay_cash()

# ==================== 4. NAVIGATION ====================

def mutual_main():
    """นำทาง: A -> M -> อ่านบัตร -> กรอกไปรษณีย์/เบอร์"""
    try:
        app, main_window = connect_main_window()

        # กด A
        main_window.child_window(title=B_CFG['BUTTON_A_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # กด M
        main_window.child_window(title=B_CFG['BUTTON_M_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # อ่านบัตร
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

        # กรอกไปรษณีย์
        postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(postal, main_window):
            return False
        fill_if_empty(main_window, postal, POSTAL_CODE)

        # กรอกเบอร์โทร
        phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
        if not scroll_until_found(phone, main_window):
            return False
        fill_if_empty(main_window, phone, PHONE_NUMBER)

        # กดถัดไป
        main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['NEXT_AUTO_ID'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print("[V] Navigation: เข้าสู่หน้าบริการกองทุนสำเร็จ")
        return True

    except Exception as e:
        print(f"[X] Navigation Error: {e}")
        return False

# ==================== 5. SPECIFIC LOGIC FUNCTIONS ====================

def execute_barcode_transaction(main_window, title, barcode_id):
    """Logic สำหรับ Service 1 และ 4 (มี Barcode)"""
    # 1. คลิกรายการ
    print(f"[*] เลือกรายการ: {title}")
    btn = main_window.child_window(title=title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
    if not scroll_until_found(btn, main_window):
        raise Exception(f"ไม่พบรายการ {title}")
    btn.click_input()
    time.sleep(WAIT_TIME)

    # 2. กรอก Barcode
    print(f"[*] กรอก Barcode: {S_CFG['BARCODE_VALUE']}")
    barcode_input = main_window.child_window(auto_id=barcode_id, control_type="Edit")
    barcode_input.wait('visible', timeout=WAIT_TIME).click_input()
    main_window.type_keys(S_CFG['BARCODE_VALUE'])
    time.sleep(0.5)

    # 3. ถัดไป -> ตกลง -> เสร็จสิ้น
    main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['NEXT_AUTO_ID'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)
    
    main_window.child_window(title=S_CFG['OK_BUTTON_TITLE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)
    
    main_window.child_window(title=B_CFG['FINISH_BUTTON_TITLE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def execute_service_2(main_window, title):
    """Logic สำหรับ Service 2 (กรอก 4 ช่อง + Payment)"""
    # 1. คลิกรายการ
    print(f"[*] เลือกรายการ: {title}")
    btn = main_window.child_window(title=title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
    if not scroll_until_found(btn, main_window):
        raise Exception(f"ไม่พบรายการ {title}")
    btn.click_input()
    time.sleep(WAIT_TIME)

    # 2. กรอกข้อมูล 4 ช่อง
    print("[*] กรอกข้อมูลสมาชิกและบัญชี...")
    main_window.child_window(auto_id=I_CFG['MEMBER_ID_AUTO_ID']).type_keys(I_CFG['MEMBER_ID_VALUE'])
    main_window.child_window(auto_id=I_CFG['ACCOUNT_NUM_AUTO_ID']).type_keys(I_CFG['ACCOUNT_NUM_VALUE'])
    main_window.child_window(auto_id=I_CFG['ACCOUNT_NAME_AUTO_ID']).type_keys(I_CFG['ACCOUNT_NAME_VALUE'])
    main_window.child_window(auto_id=I_CFG['AMOUNT_TO_PAY_AUTO_ID']).type_keys(I_CFG['AMOUNT_TO_PAY_VALUE'])
    time.sleep(WAIT_TIME)

    # 3. ถัดไป (เหลือแค่ 1 ครั้ง)
    print(f"[*] กดปุ่ม '{B_CFG['NEXT_TITLE']}'")
    next_btn = main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['NEXT_AUTO_ID'], control_type="Text")
    next_btn.click_input()
    time.sleep(WAIT_TIME)

    # 4. รับเงิน -> จ่ายเงิน (Dynamic)
    print(f"[*] รอและกดปุ่ม '{I_CFG['RECEIVE_PAYMENT_TITLE']}'")
    receive_btn = main_window.child_window(title=I_CFG['RECEIVE_PAYMENT_TITLE'], control_type="Text")
    
    if not scroll_until_found(receive_btn, main_window):
        raise Exception(f"ไม่พบปุ่ม '{I_CFG['RECEIVE_PAYMENT_TITLE']}'")
        
    receive_btn.click_input()
    time.sleep(WAIT_TIME)
    
    # จ่ายเงิน
    perform_dynamic_payment(payment)
    
    # 5. เสร็จสิ้น
    print(f"[*] รอและกดปุ่ม '{B_CFG['FINISH_BUTTON_TITLE']}'")
    finish_btn = main_window.child_window(title=B_CFG['FINISH_BUTTON_TITLE'], control_type="Text")
    
    if not scroll_until_found(finish_btn, main_window):
        raise Exception(f"จ่ายเงินเสร็จแล้ว แต่หาปุ่ม '{B_CFG['FINISH_BUTTON_TITLE']}' ไม่เจอ")
        
    finish_btn.click_input()
    time.sleep(WAIT_TIME)

def execute_service_3(main_window, title):
    """Logic สำหรับ Service 3 (Combobox + Payment)"""
    # 1. คลิกรายการ
    print(f"[*] เลือกรายการ: {title}")
    btn = main_window.child_window(title=title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text")
    if not scroll_until_found(btn, main_window):
        raise Exception(f"ไม่พบรายการ {title}")
    btn.click_input()
    time.sleep(WAIT_TIME)

    # 2. กรอกข้อมูล + เลือก Dropdown
    print("[*] กรอกข้อมูลและเลือกประเภทเงินกู้...")
    main_window.child_window(auto_id=I_CFG['MEMBER_ID_AUTO_ID']).type_keys(I_CFG['MEMBER_ID_VALUE'])
    
    # เลือก Combobox
    select_combobox_item(
        main_window, 
        combo_auto_id=I_CFG['LOAN_TYPE_COMBO_ID'], 
        item_title=I_CFG['LOAN_A_SELECT'], 
        sleep=WAIT_TIME
    )
    
    main_window.child_window(auto_id=I_CFG['ACCOUNT_NAME_AUTO_ID']).type_keys(I_CFG['ACCOUNT_NAME_VALUE'])
    main_window.child_window(auto_id=I_CFG['AMOUNT_TO_PAY_AUTO_ID']).type_keys(I_CFG['AMOUNT_TO_PAY_VALUE'])
    time.sleep(WAIT_TIME)

    # 3. ถัดไป (เหลือแค่ 1 ครั้ง)
    print(f"[*] กดปุ่ม '{B_CFG['NEXT_TITLE']}'")
    next_btn = main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['NEXT_AUTO_ID'], control_type="Text")
    next_btn.click_input()
    time.sleep(WAIT_TIME)

    # 4. รับเงิน -> จ่ายเงิน (Dynamic)
    print(f"[*] รอและกดปุ่ม '{I_CFG['RECEIVE_PAYMENT_TITLE']}'")
    receive_btn = main_window.child_window(title=I_CFG['RECEIVE_PAYMENT_TITLE'], control_type="Text")
    
    if not scroll_until_found(receive_btn, main_window):
        raise Exception(f"ไม่พบปุ่ม '{I_CFG['RECEIVE_PAYMENT_TITLE']}'")
        
    receive_btn.click_input()
    time.sleep(WAIT_TIME)
    
    # จ่ายเงิน
    perform_dynamic_payment(payment)
    
    # 5. เสร็จสิ้น
    print(f"[*] รอและกดปุ่ม '{B_CFG['FINISH_BUTTON_TITLE']}'")
    finish_btn = main_window.child_window(title=B_CFG['FINISH_BUTTON_TITLE'], control_type="Text")
    
    if not scroll_until_found(finish_btn, main_window):
        raise Exception(f"จ่ายเงินเสร็จแล้ว แต่หาปุ่ม '{B_CFG['FINISH_BUTTON_TITLE']}' ไม่เจอ")
        
    finish_btn.click_input()
    time.sleep(WAIT_TIME)

# ==================== 6. ENGINE (STOP ON ERROR) ====================

def run_service(step_name, logic_function, *args):
    """Engine กลาง: รัน Logic -> แคปภาพ Error -> หยุดทันที"""
    app = None
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {step_name}")
    
    try:
        # 1. นำทางเข้าหน้าหลัก
        if not mutual_main():
            raise Exception("Navigation Failed: ไม่สามารถเข้าหน้า Mutual Fund ได้")

        app, main_window = connect_main_window()
        
        # 2. รัน Logic
        logic_function(main_window, *args)
        
        print(f"[V] SUCCESS: {step_name} สำเร็จ")

    except Exception as e:
        print(f"\n[X] FAILED: {step_name} -> {e}")
        
        if app:
            try:
                save_evidence_context(app, {
                    "test_name": "Mutual Services Automation",
                    "step_name": step_name,
                    "error_message": str(e)
                })
                print("[/] บันทึกภาพ Error เรียบร้อย")
            except: pass
            
        print("!!! หยุดการทำงาน (Stop Execution) !!!")
        sys.exit(1)

# ==================== 7. ENTRY POINT ====================

if __name__ == "__main__":
    # Service 1: Barcode
    run_service("Service 1", execute_barcode_transaction, S_CFG['MUTUAL_1_TITLE'], S_CFG['BARCODE_EDIT_AUTO_ID'])
    
    # Service 2: 4 Fields + Dynamic Payment
    run_service("Service 2", execute_service_2, S_CFG['MUTUAL_2_TITLE'])
    
    # Service 3: Combobox + Dynamic Payment
    run_service("Service 3", execute_service_3, S_CFG['MUTUAL_3_TITLE'])
    
    # Service 4: Barcode (Logic เดียวกับ 1)
    run_service("Service 4", execute_barcode_transaction, S_CFG['MUTUAL_4_TITLE'], S_CFG['BARCODE2_EDIT_AUTO_ID'])

    print(f"\n{'='*50}\n[V] จบการทำงานทั้งหมด")