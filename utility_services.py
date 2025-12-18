import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys
from evidence import save_evidence_context

# ชื่อไฟล์ Config
CONFIG_FILE = "config.ini"

# ==================== 1. CONFIG & SETUP ====================

def read_config(filename=CONFIG_FILE):
    """อ่านและโหลดค่าจากไฟล์ config.ini"""
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(filename):
            print(f"[X] ไม่พบไฟล์ config ที่: {os.path.abspath(filename)}")
            return None
        config.read(filename, encoding='utf-8')
        return config
    except Exception as e:
        print(f"[X] FAILED: ไม่สามารถอ่านไฟล์ {filename} ได้: {e}")
        return None

# โหลด Config เข้าสู่ตัวแปรกลาง
CONFIG = read_config()
if not CONFIG or not CONFIG.sections():
    print("ไม่สามารถโหลด config.ini ได้ โปรดตรวจสอบไฟล์")
    sys.exit(1)

# ดึงค่า Global ที่ใช้ร่วมกัน
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

# ดึง Section หลักของ Utility
B_CFG = CONFIG['UTILITY_MAIN']
S_CFG = CONFIG['UTILITY_SERVICES']

# ==================== 2. HELPERS ====================

def force_scroll_down(window, config):
    """เลื่อนหน้าจอลงโดยใช้ Mouse wheel"""
    try:
        center_x_offset = config.getint('MOUSE_SCROLL', 'CENTER_X_OFFSET', fallback=300)
        center_y_offset = config.getint('MOUSE_SCROLL', 'CENTER_Y_OFFSET', fallback=300)
        wheel_dist = config.getint('MOUSE_SCROLL', 'WHEEL_DIST', fallback=-20)
        focus_delay = config.getfloat('MOUSE_SCROLL', 'FOCUS_DELAY', fallback=0.5)
        scroll_delay = config.getfloat('MOUSE_SCROLL', 'SCROLL_DELAY', fallback=1.0)
        
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

# ==================== 3. TEMPLATES & ENGINE ====================

def utility_services_transaction_logic(main_window, transaction_title, mode=1):
    """ฟังก์ชันจัดการ Flow การกดปุ่มในหน้า Transaction (Mode 1: Next, Mode 2: Enter)"""
    # 1. คลิกรายการย่อย
    print(f"[*] ค้นหาและคลิกรายการ: {transaction_title}")
    main_window.child_window(title=transaction_title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)
    
    # 2. การดำเนินการ (ถัดไป หรือ Enter)
    if mode == 1:
        print(f"[*] กดปุ่ม '{B_CFG['NEXT_TITLE']}'")
        main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['ID_AUTO_ID'], control_type="Text").click_input()
    else:
        print("[*] ดำเนินการ: กดปุ่ม ENTER")
        main_window.type_keys("{ENTER}")
    
    time.sleep(WAIT_TIME)
    
    # 3. กดเสร็จสิ้น
    print(f"[*] กดปุ่ม '{B_CFG['FINISH_BUTTON_TITLE']}'")
    main_window.child_window(title=B_CFG['FINISH_BUTTON_TITLE'], control_type="Text").click_input()
    time.sleep(WAIT_TIME)

def run_utility_service(service_key, mode=1, use_search=False):
    """
    หัวใจหลักในการรันรายการ: จัดการ Connect App, Search, และดัก Error แคปภาพ
    """
    service_title = S_CFG[service_key]
    print(f"\n{'='*50}\n[*] ดำเนินรายการ: {service_title}")
    
    app = None
    try:
        # 1. นำทางหน้าหลัก (Agency -> BaS -> อ่านบัตร)
        if not utility_services_main_nav(): return

        # 2. เชื่อมต่อ Application หลัง Navigation สำเร็จ
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # 3. การค้นหารายการ (ถ้าเป็นรายการที่ 6-9)
        if use_search:
            print(f"[*] ค้นหารหัส: {service_title}")
            search_input = main_window.child_window(auto_id=S_CFG['SEARCH_EDIT_ID'], control_type="Edit")
            search_input.click_input()
            search_input.type_keys(service_title, with_spaces=True)
            search_input.type_keys("{ENTER}")
            time.sleep(1.5)
            
            # ตรวจสอบหลังค้นหา
            target = main_window.child_window(title=service_title, control_type="Text")
            if not target.exists(timeout=3):
                raise Exception(f"ไม่พบรายการ {service_title} จากการ Search")

        # 4. เข้าสู่ขั้นตอนกดปุ่ม Transaction
        utility_services_transaction_logic(main_window, service_title, mode=mode)
        print(f"[V] SUCCESS: {service_title} สำเร็จ")

    except Exception as e:
        # แคปภาพหลักฐานเมื่อเกิด Error ทันที
        error_context = {"test_name": "Utility Services", "step_name": service_key, "error_message": str(e)}
        save_evidence_context(app, error_context)
        print(f"[X] FAILED: {service_key} -> {e}")

# ==================== 4. NAVIGATION FLOW ====================

def utility_services_main_nav():
    """ขั้นตอนเตรียมการหน้าหลัก (Agency -> BaS -> อ่านบัตร -> กรอกข้อมูลเบื้องต้น)"""
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        win = app.top_window()
        
        # กด Agency และ BaS
        win.child_window(title=B_CFG['HOTKEY_AGENCY_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        win.child_window(title=B_CFG['HOTKEY_BaS_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # อ่านบัตร
        win.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
        
        # ตรวจสอบ/กรอกข้อมูลเบื้องต้น (ไปรษณีย์ และ เบอร์โทร)
        for ctrl_id, val, name in [
            (POSTAL_CODE_EDIT_AUTO_ID, POSTAL_CODE, "ไปรษณีย์"),
            (PHONE_EDIT_AUTO_ID, PHONE_NUMBER, "เบอร์โทรศัพท์")
        ]:
            ctrl = win.child_window(auto_id=ctrl_id, control_type="Edit")
            # ถ้าไม่เห็นให้เลื่อนหา
            if not ctrl.exists(timeout=1):
                for _ in range(3):
                    force_scroll_down(win, CONFIG)
                    if ctrl.exists(timeout=1): break
            
            if not ctrl.exists(): 
                print(f"[X] หาช่อง {name} ไม่เจอ"); return False
            
            if not ctrl.texts()[0].strip():
                ctrl.click_input()
                win.type_keys(val)
            time.sleep(0.5)

        # กดถัดไปเพื่อเข้าหน้าเลือกรายการย่อย
        win.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['ID_AUTO_ID'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        return True
    except Exception as e:
        print(f"[X] Navigation Error: {e}")
        return False

# ==================== 5. EXECUTION ====================

if __name__ == "__main__":
    # รายการ 1-3: โหมดปกติ (Mode 1 - คลิกปุ่มถัดไป)
    run_utility_service('UTILITY_1_TITLE', mode=1)
    run_utility_service('UTILITY_2_TITLE', mode=1)
    run_utility_service('UTILITY_3_TITLE', mode=1)
    
    # รายการ 4-5: โหมดกด ENTER (Mode 2)
    run_utility_service('UTILITY_4_TITLE', mode=2)
    run_utility_service('UTILITY_5_TITLE', mode=2)
    
    # รายการ 6: โหมด Search (ใช้ Mode 1 - คลิกถัดไป)
    run_utility_service('UTILITY_6_TITLE', mode=1, use_search=True)

    # >>> รายการ 7: แก้จาก mode=1 เป็น mode=2 (เพื่อให้กด ENTER แทนคลิกถัดไป) <<<
    run_utility_service('UTILITY_7_TITLE', mode=2, use_search=True)

    # รายการ 8-9: โหมด Search (ถ้าต้องการ ENTER ให้เปลี่ยนเป็น mode=2 เช่นกัน)
    run_utility_service('UTILITY_8_TITLE', mode=1, use_search=True)
    run_utility_service('UTILITY_9_TITLE', mode=1, use_search=True)