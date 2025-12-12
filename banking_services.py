import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys

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
    exit()

# ดึงค่า Global ที่ใช้ร่วมกัน
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

# ดึง Section หลัก
B_CFG = CONFIG['BANKING_MAIN']
S_CFG = CONFIG['BANKING_SERVICES']

# ==================== SCROLL HELPERS mouse ====================

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

def banking_services_main(CONFIG):

    # 1. กำหนดตัวแปรจาก Config
    HOTKEY_AGENCY_TITLE = B_CFG['HOTKEY_AGENCY_TITLE']
    HOTKEY_BaS_TITLE = B_CFG['HOTKEY_BaS_TITLE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    ID_AUTO_ID = B_CFG['ID_AUTO_ID']

    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' โดยการกดปุ่ม '{HOTKEY_AGENCY_TITLE}'...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        print("[/] เชื่อมต่อหน้าจอสำเร็จ ")

        # 2. กด A
        main_window.child_window(title=HOTKEY_AGENCY_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] เข้าสู่หน้า 'บริการธนาคาร'...")

        # 3. กด B
        main_window.child_window(title=HOTKEY_BaS_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        print("[/] กำลังดำเนินการในหน้า 'บริการธนาคาร'...")

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
        main_window.child_window(title=NEXT_TITLE, auto_id=ID_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
 
        print("\n[V] SUCCESS: ดำเนินการขั้นตอน Bank POS (ผู้ฝากส่ง) สำเร็จ!")
        return True
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดใน bank_pos_navigate_main: {e}")
        return False
    
# ----------------- ฟังก์ชันแม่แบบสำหรับรายการย่อย -----------------

def banking_services_transaction(main_window, transaction_title):
    """ฟังก์ชันที่ใช้ร่วมกันสำหรับรายการย่อยทั้งหมด"""
    
    # 1. กำหนดตัวแปรจาก Config
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    ID_AUTO_ID = B_CFG['ID_AUTO_ID']
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
    
    try:
        # 2. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {transaction_title}")
        main_window.child_window(title=transaction_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 3. คลิก 'ถัดไป'
        print(f"[*] 3. กดปุ่ม '{NEXT_TITLE}'")
        main_window.child_window(title=NEXT_TITLE, auto_id=ID_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 4. คลิก 'เสร็จสิ้น'
        print(f"[*] 4. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดในการทำรายการย่อย {transaction_title}: {e}")
    
#------------ ฟังก์ชัน แม่แบบ 2 step -------------------

def banking_services_transaction2(main_window, transaction_title):
    """ฟังก์ชันที่ใช้ร่วมกันสำหรับรายการย่อยทั้งหมด"""
    
    # 1. กำหนดตัวแปรจาก Config
    TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
    NEXT_TITLE = B_CFG['NEXT_TITLE']
    ID_AUTO_ID = B_CFG['ID_AUTO_ID']
    FINISH_BUTTON_TITLE = B_CFG['FINISH_BUTTON_TITLE']
    
    try:
        # 2. คลิกรายการย่อย
        print(f"[*] 2. ค้นหาและคลิกรายการ: {transaction_title}")
        main_window.child_window(title=transaction_title, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 3. คลิก 'ถัดไป'
        print(f"[*] 3. กดปุ่ม '{NEXT_TITLE}'")
        main_window.child_window(title=NEXT_TITLE, auto_id=ID_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)

        # 4. คลิก 'ถัดไป'
        print(f"[*] 4. กดปุ่ม '{NEXT_TITLE}'")
        main_window.child_window(title=NEXT_TITLE, auto_id=ID_AUTO_ID, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # 5. คลิก 'เสร็จสิ้น'
        print(f"[*] 5. กดปุ่ม '{FINISH_BUTTON_TITLE}'")
        main_window.child_window(title=FINISH_BUTTON_TITLE, control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
    except Exception as e:
        print(f"\n[X] FAILED: เกิดข้อผิดพลาดในการทำรายการย่อย {transaction_title}: {e}")

# ----------------- ฟังก์ชันย่อยตามโครงสร้างเดิม (เรียกใช้ Config) -----------------

def banking_services1():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 1)...")
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        banking_services_transaction2(main_window, S_CFG['BANKING_1_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services2():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 2)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        banking_services_transaction(main_window, S_CFG['BANKING_2_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services3():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 3)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        banking_services_transaction(main_window, S_CFG['BANKING_3_TITLE'])
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services4():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 4)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        # [NEW] เพิ่มการตรวจสอบ/Scroll
        SERVICE_TITLE = S_CFG['BANKING_4_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services5():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 5)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        # [NEW] เพิ่มการตรวจสอบ/Scroll
        SERVICE_TITLE = S_CFG['BANKING_5_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services6():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 6)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        # [NEW] เพิ่มการตรวจสอบ/Scroll
        SERVICE_TITLE = S_CFG['BANKING_6_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services7():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 7)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        # [NEW] เพิ่มการตรวจสอบ/Scroll
        SERVICE_TITLE = S_CFG['BANKING_7_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}") 

def banking_services8():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 8)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()
        
        # [NEW] เพิ่มการตรวจสอบ/Scroll
        SERVICE_TITLE = S_CFG['BANKING_8_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services9():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 9)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [NEW] เพิ่มการตรวจสอบ/Scroll (แทนที่การเรียก force_scroll_down() เดิม)
        SERVICE_TITLE = S_CFG['BANKING_9_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}") 

def banking_services10():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 10)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [NEW] เพิ่มการตรวจสอบ/Scroll (แทนที่การเรียก force_scroll_down() เดิม)
        SERVICE_TITLE = S_CFG['BANKING_10_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services11():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 11)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [NEW] เพิ่มการตรวจสอบ/Scroll (แทนที่การเรียก force_scroll_down() เดิม)
        SERVICE_TITLE = S_CFG['BANKING_11_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}") 

def banking_services12():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 12)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [NEW] เพิ่มการตรวจสอบ/Scroll (แทนที่การเรียก force_scroll_down() เดิม)
        SERVICE_TITLE = S_CFG['BANKING_12_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services13():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 13)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [NEW] เพิ่มการตรวจสอบ/Scroll (แทนที่การเรียก force_scroll_down() เดิม)
        SERVICE_TITLE = S_CFG['BANKING_13_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services14():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 14)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [NEW] เพิ่มการตรวจสอบ/Scroll (แทนที่การเรียก force_scroll_down() เดิม)
        SERVICE_TITLE = S_CFG['BANKING_14_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return

        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")

def banking_services15():
    print(f"\n{'='*50}\n[*] 1. กำลังเข้าสู่หน้า 'บริการธนาคาร' (รายการ 15)...")
    try:
        if not banking_services_main(): return
        
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # [NEW] เพิ่มการตรวจสอบ/Scroll (แทนที่การเรียก force_scroll_down() เดิม)
        SERVICE_TITLE = S_CFG['BANKING_15_TITLE']
        TRANSACTION_CONTROL_TYPE = S_CFG['TRANSACTION_CONTROL_TYPE']
        target_control = main_window.child_window(title=SERVICE_TITLE, auto_id=TRANSACTION_CONTROL_TYPE, control_type="Text")
        
        max_scrolls = 3
        found = False
        
        print(f"[*] 1.5. กำลังตรวจสอบรายการ '{SERVICE_TITLE}' ก่อน Scroll...")
        if target_control.exists(timeout=1):
            print("[/] รายการย่อยพบแล้ว, ไม่จำเป็นต้อง Scroll.")
            found = True
        
        if not found:
            print(f"[*] 1.5.1. รายการย่อยไม่ปรากฏทันที, เริ่มการ Scroll ({max_scrolls} ครั้ง)...")
            for i in range(max_scrolls):
                force_scroll_down(main_window, CONFIG) 
                if target_control.exists(timeout=1):
                    print(f"[/] รายการย่อยพบแล้วในการ Scroll ครั้งที่ {i+1}.")
                    found = True
                    break
        
        if not found:
            print(f"[X] FAILED: ไม่สามารถค้นหารายการย่อย '{SERVICE_TITLE}' ได้หลัง Scroll {max_scrolls} ครั้ง")
            return
            
        banking_services_transaction(main_window, SERVICE_TITLE)
        
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")
    except Exception as e:
        print(f"\n[X] FAILED: ไม่สามารถเชื่อมต่อโปรแกรม POS ได้: {e}")                            

# ----------------- Main Execution -----------------


if __name__ == "__main__":
    banking_services_main(CONFIG)
    banking_services1()
    banking_services2()
    banking_services3()
    banking_services4()
    banking_services5()
    banking_services6()
    banking_services7()
    banking_services8()
    banking_services9()
    banking_services10()
    banking_services11()
    banking_services12()
    banking_services13()
    banking_services14()
    banking_services15()