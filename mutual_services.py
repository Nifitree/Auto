import configparser
import time
import os
import sys
from pywinauto.application import Application
from pywinauto import mouse

# Custom Modules
from payment_flow import PaymentFlow
from app_context import AppContext  # <--- [เพิ่ม]
from ui_helper import select_combobox_item
from evidence import save_evidence_context

# ==================== CONFIGURATION ====================

CONFIG_FILE = "config.ini"

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return configparser.ConfigParser()
            
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED: ไม่สามารถอ่านไฟล์ {filename} ได้: {e}")
        return configparser.ConfigParser()

# โหลด Config
CONFIG = read_config()
if not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้ โปรดตรวจสอบไฟล์")
    sys.exit()

# --- Global Config ---
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

# --- Section Configs ---
B_CFG = CONFIG['MUTUAL_MAIN']
S_CFG = CONFIG['MUTUAL_SERVICES']
T_CFG = CONFIG['PAYMENT']
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

# ==================== HELPERS & CONTEXT ====================

# <--- [แก้ไข] สร้าง ctx และส่งให้ PaymentFlow
ctx = AppContext(window_title_regex=WINDOW_TITLE)
payment = PaymentFlow(CONFIG, ctx)

def connect_main_window():
    """เชื่อมต่อหน้าต่างหลัก (ใช้ ctx)"""
    # <--- [แก้ไข] เรียกใช้จาก AppContext
    return ctx.connect()

def force_scroll_down(window, config):
    """เลื่อนหน้าจอลงโดยใช้ Mouse wheel"""
    try:
        center_x_offset = config.getint('MOUSE_SCROLL', 'CENTER_X_OFFSET')
        center_y_offset = config.getint('MOUSE_SCROLL', 'CENTER_Y_OFFSET')
        wheel_dist = config.getint('MOUSE_SCROLL', 'WHEEL_DIST')
        focus_delay = config.getfloat('MOUSE_SCROLL', 'FOCUS_DELAY')
        scroll_delay = config.getfloat('MOUSE_SCROLL', 'SCROLL_DELAY')
    except ValueError:
        print("[!] Scroll config invalid. Using defaults.")
        center_x_offset, center_y_offset, wheel_dist, focus_delay, scroll_delay = 300, 300, -20, 0.5, 1.0

    print(f"...กำลังเลื่อนหน้าจอลง (Mouse Wheel {wheel_dist})...")

    try:
        rect = window.rectangle()
        center_x = rect.left + center_x_offset
        center_y = rect.top + center_y_offset
        
        mouse.click(coords=(center_x, center_y))
        time.sleep(focus_delay)
        
        mouse.scroll(coords=(center_x, center_y), wheel_dist=wheel_dist)
        time.sleep(scroll_delay)
        print("[/] Scroll สำเร็จ")
    except Exception as e:
        print(f"[!] Scroll failed: {e}, ใช้ PageDown แทน")
        window.type_keys("{PGDN}")

# ==================== MAIN NAVIGATION ====================

def mutual_main():
    BUTTON_A_TITLE = B_CFG['BUTTON_A_TITLE']
    BUTTON_M_TITLE = B_CFG['BUTTON_M_TITLE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']

    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการกองทุนรวม' โดยการกดปุ่ม '{BUTTON_A_TITLE}'...")
    try:
        # <--- [อัปเดต] ใช้ connect_main_window ที่ผ่าน ctx แล้ว
        app, main_window = connect_main_window()
        print("[/] เชื่อมต่อหน้าจอสำเร็จ ")

        # 1. กด A
        main_window.child_window(title=BUTTON_A_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] เข้าสู่หน้า 'บริการกองทุนรวม'...")

        # 2. กด M
        main_window.child_window(title=BUTTON_M_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] กำลังดำเนินการในหน้า 'บริการกองทุนรวม'...")

        # 3. กด 'อ่านบัตรประชาชน'
        print(f"[*] 2.1. ค้นหาและคลิกปุ่ม '{ID_CARD_BUTTON_TITLE}'...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

        # 4. กรอกเลขไปรษณีย์
        print(f"[*] 2.2.5. กำลังตรวจสอบ/กรอกเลขไปรษณีย์ ID='{POSTAL_CODE_EDIT_AUTO_ID}'")
        postal_control = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    
        if not postal_control.exists(timeout=1):
            print("[!] ช่องไปรษณีย์ไม่ปรากฏทันที, กำลังเลื่อนหน้าจอลง...")
        
        # Scroll หาช่องไปรษณีย์
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if postal_control.exists(timeout=1):
                print("[/] ช่องไปรษณีย์พบแล้วหลังการ Scroll")
                found = True
                break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องไปรษณีย์ '{POSTAL_CODE_EDIT_AUTO_ID}' ได้หลัง Scroll")
            return False

        if not postal_control.texts()[0].strip():
            print(f" [-] -> ช่องว่าง, กรอก: {POSTAL_CODE}")
            postal_control.click_input() 
            main_window.type_keys(POSTAL_CODE)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {postal_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)
    
        # 5. กรอกเบอร์โทรศัพท์
        print(f"[*] 2.2. กำลังตรวจสอบ/กรอกเบอร์โทรศัพท์ ID='{PHONE_EDIT_AUTO_ID}'")
        phone_control = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    
        if not phone_control.exists(timeout=1):
            print("[!] ช่องเบอร์โทรศัพท์ไม่ปรากฏทันที, กำลังตรวจสอบ/เลื่อนหน้าจอซ้ำ...")
        
        # Scroll หาช่องเบอร์โทร
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if phone_control.exists(timeout=1):
                print("[/] ช่องเบอร์โทรศัพท์พบแล้วหลังการ Scroll")
                found = True
                break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องเบอร์โทรศัพท์ '{PHONE_EDIT_AUTO_ID}' ได้หลัง Scroll")
            return False
    
        if not phone_control.texts()[0].strip():
            print(f" [-] -> ช่องว่าง, กรอก: {PHONE_NUMBER}")
            phone_control.click_input()
            main_window.type_keys(PHONE_NUMBER)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {phone_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)

        # 6. กด 'ถัดไป'
        print(f"[*] 2.3. กดปุ่ม '{NEXT_TITLE}' เพื่อไปหน้าถัดไป...")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
    
        print("\n[V] SUCCESS: ดำเนินการขั้นตอน สำเร็จ!")
        return True

    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดใน : {e}")
        return False
    
# ==================== SHARED TRANSACTION FUNCTION ====================

def mutual_transaction(main_window, transaction_title, BARCODE_EDIT_AUTO_ID):
    """ฟังก์ชันที่ใช้ร่วมกันสำหรับรายการย่อย (Barcode)"""
    
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
    OK_BUTTON_TITLE = S_CFG['OK_BUTTON_TITLE']
    
    MUTUAL_1_ID = S_CFG['MUTUAL_1_TITLE']
    MUTUAL_4_ID = S_CFG['MUTUAL_4_TITLE']
    BARCODE_FLOW_TITLES = [MUTUAL_1_ID, MUTUAL_4_ID]
    BARCODE_VALUE = S_CFG['BARCODE_VALUE']
    
    try:
        # 1. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {transaction_title}")
        main_window.child_window(title=transaction_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        if transaction_title in BARCODE_FLOW_TITLES:
            print("--- [Special Step] รายการนี้ต้องการการกรอกบาร์โค้ด ---")

            # 2. กรอกบาร์โค้ด
            print(f"[*] 2.5.1. กำลังกรอกเลขบาร์โค้ด: {BARCODE_VALUE} (ID: {BARCODE_EDIT_AUTO_ID})")
            barcode_control = main_window.child_window(auto_id=BARCODE_EDIT_AUTO_ID, control_type="Edit")
            barcode_control.wait('visible', timeout=WAIT_TIME).click_input()
            main_window.type_keys(BARCODE_VALUE)
            time.sleep(0.5)

            # 3. กดปุ่ม 'ถัดไป'
            print(f"[*] 3. ถัดไป '{NEXT_TITLE}'")
            main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
            time.sleep(WAIT_TIME)
            
        # 4. คลิก 'ตกลง'
        print(f"[*] 2.5.2. กดปุ่ม '{OK_BUTTON_TITLE}'")
        main_window.child_window(title=OK_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 5. คลิก 'เสร็จสิ้น'
        print(f"[*] 4. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดในการทำรายการย่อย {transaction_title}: {e}")
        raise e

# ==================== SERVICE FUNCTIONS ====================

def mutual_services1():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการกองทุนรวม' (รายการ 1)...")
    app = None
    BARCODE_EDIT_AUTO_ID = S_CFG['BARCODE_EDIT_AUTO_ID']
    try:
        # <--- [อัปเดต] เรียก connect_main_window() ซึ่งจะใช้ ctx.connect()
        app, main_window = connect_main_window()
        
        mutual_transaction(main_window, S_CFG['MUTUAL_1_TITLE'], BARCODE_EDIT_AUTO_ID)
        
    except Exception as e:
        error_context = {
            "test_name": "Mutual Services Automation",
            "step_name": "mutual_services1",
            "error_message": str(e)
        }
        # ตรวจสอบ app ก่อน save (เผื่อ connect ไม่ติด)
        if app: save_evidence_context(app, error_context)
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def mutual_services2():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการกองทุนรวม' (รายการ 2 - กรอก 4 ฟิลด์)...")
    app = None
    try:
        if not mutual_main(): 
            return
            
        app, main_window = connect_main_window()
        
        SERVICE_TITLE = S_CFG['MUTUAL_2_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        NEXT_TITLE = B_CFG['NEXT_TITLE']
        NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']
        FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
        
        # 2. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 3. กรอกข้อมูล 4 ฟิลด์
        print("[*] 3. กำลังกรอกข้อมูลสมาชิกและบัญชี...")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID, control_type="Edit").type_keys(MEMBER_ID_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NUM_AUTO_ID, control_type="Edit").type_keys(ACCOUNT_NUM_VALUE)
        main_window.child_window(auto_id=ACCOUNT_NAME_AUTO_ID, control_type="Edit").type_keys(ACCOUNT_NAME_VALUE)
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID, control_type="Edit").type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # 4. คลิก 'ถัดไป' (1)
        print(f"[*] 4. กดปุ่ม '{NEXT_TITLE}' (1)")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 5. คลิก 'ถัดไป' (2)
        print(f"[*] 5. กดปุ่ม '{NEXT_TITLE}' (2)")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 6. คลิก 'รับเงิน'
        print(f"[*] 6. กดปุ่ม '{RECEIVE_PAYMENT_TITLE}'")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 7. จ่ายเงิน (เลือก 1 วิธี โดยการลบเครื่องหมาย # ออก)
        print("[*] 7. เข้าสู่หน้าจอการชำระเงินและดำเนินการ...")
        
        # --- [PAYMENT SELECTION] ---
        # payment.pay_cash()                      # 1. เงินสด (ระบุจำนวน)
        main_window.type_keys(T_CFG['PAYMENT_FAST']) # 2. เงินสด (ด่วน/เต็มจำนวน - Hotkey F)
        # payment.pay_qr()                      # 3. QR PromptPay
        # payment.pay_credit()                  # 4. บัตรเครดิต
        # payment.pay_debit()                   # 5. บัตรเดบิต
        # payment.pay_check()                   # 6. เช็คธนาคาร
        # payment.pay_alipay()                  # 7. Alipay
        # payment.pay_wechat()                  # 8. WeChat Pay
        # payment.pay_thp()                     # 9. Wallet@Post
        # payment.pay_truemoney()               # 10. TrueMoney Wallet
        # payment.pay_qr_credit()               # 11. QR Credit
        # ---------------------------
        
        time.sleep(WAIT_TIME)
        
        # 8. คลิก 'เสร็จสิ้น'
        print(f"[*] 8. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"\n[V] SUCCESS: ดำเนินการรายการย่อย {SERVICE_TITLE} สำเร็จ!")
        
    except Exception as e:
        error_context = {
            "test_name": "Mutual Services Automation",
            "step_name": "mutual_services2",
            "error_message": str(e)
        }
        if app: save_evidence_context(app, error_context)
        print(f"\n[X] FAILED: ไม่สามารถทำรายการย่อย {SERVICE_TITLE}: {e}")

def mutual_services3():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการกองทุนรวม' (รายการ 3 - Loan Type)...")
    app = None
    try:
        if not mutual_main(): 
            return
            
        app, main_window = connect_main_window()
        
        SERVICE_TITLE = S_CFG['MUTUAL_3_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        NEXT_TITLE = B_CFG['NEXT_TITLE']
        NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']
        FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
        
        # 2. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 3. กรอกข้อมูลและเลือก Dropdown
        print("[*] 3. กำลังกรอกข้อมูลสมาชิก, เลือกประเภทเงินกู้ และกรอกจำนวนเงิน...")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID, control_type="Edit").type_keys(MEMBER_ID_VALUE)
        time.sleep(0.5)

        select_combobox_item(
            main_window, 
            combo_auto_id=LOAN_TYPE_COMBO_ID, 
            item_title=LOAN_TYPE_SELECT, 
            sleep=WAIT_TIME,
        )
        time.sleep(WAIT_TIME)

        main_window.child_window(auto_id=ACCOUNT_NUM_AUTO_ID, control_type="Edit").type_keys(ACCOUNT_NAME_VALUE)
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID, control_type="Edit").type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)

        # 4. คลิก 'ถัดไป' (1)
        print(f"[*] 4. กดปุ่ม '{NEXT_TITLE}' (1)")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 5. คลิก 'ถัดไป' (2)
        print(f"[*] 5. กดปุ่ม '{NEXT_TITLE}' (2)")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 6. คลิก 'รับเงิน'
        print(f"[*] 6. กดปุ่ม '{RECEIVE_PAYMENT_TITLE}'")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 7. จ่ายเงิน (เลือก 1 วิธี)
        print("[*] 7. เข้าสู่หน้าจอการชำระเงินและดำเนินการ...")
        
        # --- [PAYMENT SELECTION] ---
        # payment.pay_cash()                      # 1. เงินสด (ระบุจำนวน)
        main_window.type_keys(T_CFG['PAYMENT_FAST']) # 2. เงินสด (ด่วน/เต็มจำนวน - Hotkey F)
        # payment.pay_qr()                      # 3. QR PromptPay
        # payment.pay_credit()                  # 4. บัตรเครดิต
        # payment.pay_debit()                   # 5. บัตรเดบิต
        # payment.pay_check()                   # 6. เช็คธนาคาร
        # payment.pay_alipay()                  # 7. Alipay
        # payment.pay_wechat()                  # 8. WeChat Pay
        # payment.pay_thp()                     # 9. Wallet@Post
        # payment.pay_truemoney()               # 10. TrueMoney Wallet
        # payment.pay_qr_credit()               # 11. QR Credit
        
        # 8. คลิก 'เสร็จสิ้น'
        print(f"[*] 8. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"\n[V] SUCCESS: ดำเนินการรายการย่อย {SERVICE_TITLE} สำเร็จ!")
        
    except Exception as e:
        error_context = {
            "test_name": "Mutual Services Automation",
            "step_name": "mutual_services3",
            "error_message": str(e)
        }
        if app: save_evidence_context(app, error_context)
        print(f"\n[X] FAILED: ไม่สามารถทำรายการย่อย {SERVICE_TITLE}: {e}")

def mutual_services4():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการกองทุนรวม' (รายการ 4)...") 
    BARCODE2_EDIT_AUTO_ID = S_CFG['BARCODE2_EDIT_AUTO_ID']
    try:
        if not mutual_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        SERVICE_TITLE = S_CFG['MUTUAL_4_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        
        # 1. ตรวจสอบรายการ
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        # 2. Scroll หากไม่พบ
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        # 3. หากยังไม่พบ
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll")
            return
        
        # 4. เรียก Transaction
        mutual_transaction(main_window, SERVICE_TITLE, BARCODE2_EDIT_AUTO_ID)
        
    except Exception as e:
        error_context = {
            "test_name": "Mutual Services Automation",
            "step_name": "mutual_services4",
            "error_message": str(e)
        }
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    mutual_main()
    mutual_services1()
    mutual_services2()
    mutual_services3()
    mutual_services4()