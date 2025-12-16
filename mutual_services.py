import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys
from payment_flow import PaymentFlow
from app_context import AppContext

# ชื่อไฟล์ Config
CONFIG_FILE = "config.ini"

# ==================== CONFIG & HELPER FUNCTIONS ====================

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
    exit() # ใช้ exit() ตามโค้ดเดิม

# ดึงค่า Global ที่ใช้ร่วมกัน
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

# ดึง Section หลัก
B_CFG = CONFIG['MUTUAL_MAIN']
S_CFG = CONFIG['MUTUAL_SERVICES']
T_CFG = CONFIG['PAYMENT']
I_CFG = CONFIG['INFORMATION']

# =======================================================================
# >>>>> ตำแหน่งที่ถูกต้องในการดึงค่า [INFORMATION] เข้าสู่ Global Scope <<<<<
# --- [ใหม่] ดึงค่าทั้งหมดจาก Section [INFORMATION] ---
RECEIVE_PAYMENT_TITLE = I_CFG['RECEIVE_PAYMENT_TITLE']

MEMBER_ID_VALUE = I_CFG['MEMBER_ID_VALUE']
MEMBER_ID_AUTO_ID = I_CFG['MEMBER_ID_AUTO_ID'] 

ACCOUNT_NUM_VALUE = I_CFG['ACCOUNT_NUM_VALUE']
ACCOUNT_NUM_AUTO_ID = I_CFG['ACCOUNT_NUM_AUTO_ID'] 

ACCOUNT_NAME_VALUE = I_CFG['ACCOUNT_NAME_VALUE']
ACCOUNT_NAME_AUTO_ID = I_CFG['ACCOUNT_NAME_AUTO_ID']

AMOUNT_TO_PAY_VALUE = I_CFG['AMOUNT_TO_PAY_VALUE']
AMOUNT_TO_PAY_AUTO_ID = I_CFG['AMOUNT_TO_PAY_AUTO_ID']

# ==================== SCROLL HELPERS mouse ====================

ctx = AppContext(window_title_regex=WINDOW_TITLE)
payment = PaymentFlow(CONFIG, ctx)


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

# ==================== MAIN TEST FUNCTION ====================

def mutual_main():
    # 1. กำหนดตัวแปรจาก Config
    BUTTON_A_TITLE = B_CFG['BUTTON_A_TITLE']
    BUTTON_M_TITLE = B_CFG['BUTTON_M_TITLE']
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE'] # ไม่ได้ใช้ใน main แต่ดึงมา
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID'] # ไม่ได้ใช้ใน main แต่ดึงมา
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']

    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการประกันภัย' โดยการกดปุ่ม '{BUTTON_A_TITLE}'...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        print("[/] เชื่อมต่อหน้าจอสำเร็จ ")

        # 2. กด A
        main_window.child_window(title=BUTTON_A_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] เข้าสู่หน้า 'บริการประกันภัย'...")

        # 3. กด M
        main_window.child_window(title=BUTTON_M_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] กำลังดำเนินการในหน้า 'บริการประกันภัย'...")

        # --- กด 'อ่านบัตรประชาชน' ---
        print(f"[*] 2.1. ค้นหาและคลิกปุ่ม '{ID_CARD_BUTTON_TITLE}'...")
        main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()

       # --- ค้นหาช่องเลขไปรษณีย์และกรอกข้อมูล ---
        print(f"[*] 2.2.5. กำลังตรวจสอบ/กรอกเลขไปรษณีย์ ID='{POSTAL_CODE_EDIT_AUTO_ID}'")
        postal_control = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    
        #  [จุดที่ 1] ตรวจสอบว่าช่องปรากฏหรือไม่ ก่อน Scroll
        if not postal_control.exists(timeout=1):
            print("[!] ช่องไปรษณีย์ไม่ปรากฏทันที, กำลังเลื่อนหน้าจอลง...")
        
        # ใช้การวนลูป Scroll & Check เพื่อความแม่นยำสูงสุด
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if postal_control.exists(timeout=1):
                print("[/] ช่องไปรษณีย์พบแล้วหลังการ Scroll")
                found = True
                break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องไปรษณีย์ '{POSTAL_CODE_EDIT_AUTO_ID}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return False # ยกเลิกการทำงานหากหาไม่พบ

        # [จุดที่ 2] ดำเนินการกรอกข้อมูล (เมื่อแน่ใจว่าพบแล้ว)
        if not postal_control.texts()[0].strip():
            # ถ้าช่องว่าง (Empty) ให้ทำการกรอก
            print(f" [-] -> ช่องว่าง, กรอก: {POSTAL_CODE}")
            postal_control.click_input() 
            main_window.type_keys(POSTAL_CODE)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {postal_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)
    
        # --- ค้นหาช่องหมายเลขโทรศัพท์และกรอกข้อมูล ---
        print(f"[*] 2.2. กำลังตรวจสอบ/กรอกเบอร์โทรศัพท์ ID='{PHONE_EDIT_AUTO_ID}'")
        phone_control = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    
        # [จุดที่ 2] ตรวจสอบ/Scroll ซ้ำเพื่อหาช่องเบอร์โทรศัพท์
        if not phone_control.exists(timeout=1):
            print("[!] ช่องเบอร์โทรศัพท์ไม่ปรากฏทันที, กำลังตรวจสอบ/เลื่อนหน้าจอซ้ำ...")
        
        max_scrolls = 3
        found = False
        for i in range(max_scrolls):
            force_scroll_down(main_window, CONFIG)
            if phone_control.exists(timeout=1):
                print("[/] ช่องเบอร์โทรศัพท์พบแล้วหลังการ Scroll")
                found = True
                break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถหาช่องเบอร์โทรศัพท์ '{PHONE_EDIT_AUTO_ID}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return False # ยกเลิกการทำงานหากหาไม่พบ
    
        #  [จุดที่ 3] ดำเนินการกรอกข้อมูล (เมื่อแน่ใจว่าพบแล้ว)
        if not phone_control.texts()[0].strip():
            print(f" [-] -> ช่องว่าง, กรอก: {PHONE_NUMBER}")
            phone_control.click_input()
            main_window.type_keys(PHONE_NUMBER)
        else:
            print(f" [-] -> ช่องมีค่าอยู่แล้ว: {phone_control.texts()[0].strip()}, ข้ามการกรอก")
        time.sleep(0.5)

    # --- กด 'ถัดไป' เพื่อยืนยัน ---
        print(f"[*] 2.3. กดปุ่ม '{NEXT_TITLE}' เพื่อไปหน้าถัดไป...")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
    
        print("\n[V] SUCCESS: ดำเนินการขั้นตอน สำเร็จ!")
        return True
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดใน : {e}")
        return False
    
# ----------------- ฟังก์ชันแม่แบบสำหรับรายการย่อย -----------------

def mutual_transaction(main_window, transaction_title):
    """ฟังก์ชันที่ใช้ร่วมกันสำหรับรายการย่อยทั้งหมด"""
    
    # 1. กำหนดตัวแปรจาก Config
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
    MUTUAL_1_TITLE = S_CFG['MUTUAL_1_TITLE']
    BARCODE_VALUE = S_CFG['BARCODE_VALUE']
    BARCODE_EDIT_ID = S_CFG['BARCODE_EDIT_AUTO_ID']
    OK_BUTTON_TITLE = S_CFG['OK_BUTTON_TITLE']
    
    try:
        # 2. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {transaction_title}")
        main_window.child_window(title=transaction_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        if transaction_title == MUTUAL_1_TITLE:
            print("--- [Special Step] รายการนี้ต้องการการกรอกบาร์โค้ด ---")

            # 2.5.1 กรอกบาร์โค้ด
            print(f"[*] 2.5.1. กำลังกรอกเลขบาร์โค้ด: {BARCODE_VALUE} (ID: {BARCODE_EDIT_ID})")
            barcode_control = main_window.child_window(auto_id=BARCODE_EDIT_ID, control_type="Edit")
            barcode_control.wait('visible', timeout=WAIT_TIME).click_input()
            main_window.type_keys(BARCODE_VALUE)
            time.sleep(0.5)

            # 2.5.2 กดปุ่ม 'ถัดไป'
            print(f"[*] 3. ถัดไป '{NEXT_TITLE}'")
            main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
            time.sleep(WAIT_TIME)
            
        # 3. คลิก 'ตกลง'
        print(f"[*] 2.5.2. กดปุ่ม '{OK_BUTTON_TITLE}'")
        main_window.child_window(title=OK_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 4. คลิก 'เสร็จสิ้น'
        print(f"[*] 4. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดในการทำรายการย่อย {transaction_title}: {e}")

# ----------------- ฟังก์ชันย่อยตามโครงสร้างเดิม (เรียกใช้ Config) -----------------

def mutual_services1():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการประกันภัย' (รายการ 1)...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        mutual_transaction(main_window, S_CFG['MUTUAL_1_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

# ----------------- ฟังก์ชันย่อยตามโครงสร้างเดิม (แก้ไข mutual_services2) -----------------

def mutual_services2():
    """
    [CUSTOM FLOW] สำหรับ MUTUAL_2_TITLE (50412):
    1. คลิกรายการ
    2. กรอก 4 ฟิลด์
    3. ถัดไป (1) -> ถัดไป (2)
    4. กด 'รับเงิน' -> เรียก Payment Flow -> เสร็จสิ้น
    """
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการประกันภัย' (รายการ 2 - กรอก 4 ฟิลด์)...")
    try:
        # 1.1 นำทางเข้าสู่หน้า Mutual Services (A -> M)
        if not mutual_main(): 
            return
            
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        # 1.2 กำหนดตัวแปรจาก Config (ใช้ B_CFG สำหรับปุ่มหลัก)
        SERVICE_TITLE = S_CFG['MUTUAL_2_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        NEXT_TITLE = B_CFG['NEXT_TITLE']
        NEXT_AUTO_ID = B_CFG['NEXT_AUTO_ID']
        FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
        
        # 2. คลิกรายการย่อย (Service 2)
        print(f"[*] 2. ค้นหาและคลิกรายการ: {SERVICE_TITLE}")
        main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # =========================================================================
        # >>>>> ขั้นตอนที่ 3: กรอกข้อมูล 4 ฟิลด์ (ใช้ Auto ID จาก Global) <<<<<
        print("[*] 3. กำลังกรอกข้อมูลสมาชิกและบัญชี...")

        # 3.1 กรอกเลขสมาชิก
        print(f" [-] กรอกเลขสมาชิก: {MEMBER_ID_VALUE}")
        main_window.child_window(auto_id=MEMBER_ID_AUTO_ID, control_type="Edit").type_keys(MEMBER_ID_VALUE)
        time.sleep(0.5)

        # 3.2 กรอกเลขบัญชี
        print(f" [-] กรอกเลขบัญชี: {ACCOUNT_NUM_VALUE}")
        main_window.child_window(auto_id=ACCOUNT_NUM_AUTO_ID, control_type="Edit").type_keys(ACCOUNT_NUM_VALUE)
        time.sleep(0.5)

        # 3.3 กรอกชื่อเจ้าของบัญชี
        print(f" [-] กรอกชื่อเจ้าของบัญชี: {ACCOUNT_NAME_VALUE}")
        main_window.child_window(auto_id=ACCOUNT_NAME_AUTO_ID, control_type="Edit").type_keys(ACCOUNT_NAME_VALUE)
        time.sleep(0.5)

        # 3.4 กรอกจำนวนเงินที่ชำระ
        print(f" [-] กรอกจำนวนเงิน: {AMOUNT_TO_PAY_VALUE}")
        main_window.child_window(auto_id=AMOUNT_TO_PAY_AUTO_ID, control_type="Edit").type_keys(AMOUNT_TO_PAY_VALUE)
        time.sleep(WAIT_TIME)
        # =========================================================================

        # 4. คลิก 'ถัดไป' ครั้งที่ 1 (ไปหน้ายืนยัน/สรุป)
        print(f"[*] 4. กดปุ่ม '{NEXT_TITLE}' (ครั้งที่ 1)")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 5. คลิก 'ถัดไป' ครั้งที่ 2 (นำไปสู่หน้าชำระเงิน)
        print(f"[*] 5. กดปุ่ม '{NEXT_TITLE}' (ครั้งที่ 2)")
        main_window.child_window(title=NEXT_TITLE, auto_id=NEXT_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 6. คลิก 'รับเงิน' (ปุ่มที่นำไปสู่ Payment Flow)
        print(f"[*] 6. กดปุ่ม '{RECEIVE_PAYMENT_TITLE}'")
        main_window.child_window(title=RECEIVE_PAYMENT_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # =========================================================================
        # >>>>> ขั้นตอนที่ 7: การเรียก Flow การชำระเงิน (เลือกวิธี) <<<<<
        print("[*] 7. เข้าสู่หน้าจอการชำระเงินและดำเนินการ...")
        
        # ** ณ จุดนี้ หน้าจอเลือกวิธีการชำระเงินควรจะเด้งขึ้นมา **
        # ตัวอย่าง: ชำระด้วยเงินสด (Cash) โดยเรียกใช้ handler ที่ส่งมา
        payment.pay_cash() 
        
        # =========================================================================
        
        # 8. คลิก 'เสร็จสิ้น'
        print(f"[*] 8. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"\n[V] SUCCESS: ดำเนินการรายการย่อย {SERVICE_TITLE} สำเร็จ!")
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถทำรายการย่อย {SERVICE_TITLE}: {e}")

def mutual_services3():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการประกันภัย' (รายการ 3)...")
    try:
        if not mutual_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        mutual_transaction(main_window, S_CFG['MUTUAL_3_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def mutual_services4():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการประกันภัย' (รายการ 4)...") 
    try:
        if not mutual_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

       # เพิ่มการตรวจสอบหลัง Scroll
        SERVICE_TITLE = S_CFG['MUTUAL_4_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        
        # 1. ตรวจสอบก่อนว่ารายการปรากฏขึ้นแล้วหรือไม่ (ในกรณีที่หน้าจอไม่เต็ม)
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        # 2. ถ้าไม่พบ ให้วนลูป Scroll และตรวจสอบซ้ำ
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                # ตรวจสอบหลัง Scroll
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        # 3. หากยังไม่พบ ให้ยกเลิกการทำงาน
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
        
        # 4. หากพบแล้ว จึงเรียก Transaction ต่อไป
        mutual_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

# ----------------- Main Execution -----------------

if __name__ == "__main__":
    #mutual_main()
    #mutual_services1()
    #mutual_services2()
    #mutual_services3()
    #mutual_services4()
    payment.pay_cash()
