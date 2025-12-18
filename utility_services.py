import configparser
from pywinauto.application import Application
from pywinauto import mouse 
import time
import os
import sys
from evidence import save_evidence_context

# ชื่อไฟล์ Config
CONFIG_FILE = "config.ini"

# ==================== 1. CONFIGURATION LOADING ====================

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

# ดึงค่า Global
WINDOW_TITLE = CONFIG['GLOBAL']['WINDOW_TITLE']
WAIT_TIME = CONFIG.getint('GLOBAL', 'WAIT_TIME_SEC')
PHONE_NUMBER = CONFIG['GLOBAL']['PHONE_NUMBER']
ID_CARD_BUTTON_TITLE = CONFIG['GLOBAL']['ID_CARD_BUTTON_TITLE']
PHONE_EDIT_AUTO_ID = CONFIG['GLOBAL']['PHONE_EDIT_AUTO_ID']
POSTAL_CODE = CONFIG['GLOBAL']['POSTAL_CODE'] 
POSTAL_CODE_EDIT_AUTO_ID = CONFIG['GLOBAL']['POSTAL_CODE_EDIT_AUTO_ID']

# ดึง Section ของ Utility
B_CFG = CONFIG['UTILITY_MAIN']
S_CFG = CONFIG['UTILITY_SERVICES']

# ==================== 2. MOUSE & SCROLL HELPERS ====================

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
    except Exception:
        window.type_keys("{PGDN}")

# ==================== 3. TRANSACTION LOGIC ====================

def utility_services_transaction_logic(main_window, transaction_title, mode=1):
    """
    Mode 1: คลิกรายการแล้วกดปุ่ม 'ถัดไป'
    Mode 2: เน้นกด ENTER (สำหรับรายการที่ Search เจอแล้วเลือกให้อัตโนมัติ)
    """
    if mode == 1:
        print(f"[*] Mode 1: คลิกรายการ '{transaction_title}'")
        main_window.child_window(title=transaction_title, auto_id=S_CFG['TRANSACTION_CONTROL_TYPE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        print(f"[*] คลิกปุ่ม '{B_CFG['NEXT_TITLE']}'")
        main_window.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['ID_AUTO_ID'], control_type="Text").click_input()
    
    else:
        # สำหรับ Mode 2 (รายการที่ 7)
        print(f"[*] Mode 2: กำลังพยายาม Double Click และกด ENTER ที่รายการ...")
        
        # 1. ลองหาตัวรายการแล้ว Double Click เพื่อให้มัน Active แน่นอน
        try:
            target = main_window.child_window(title=transaction_title, control_type="Text")
            target.double_click_input() # ดับเบิลคลิกเพื่อเลือกและเข้าหน้าถัดไป
            time.sleep(1)
        except:
            print("[!] Double click ไม่สำเร็จ จะลองกด ENTER แทน")

        # 2. ส่ง Enter ไปที่หน้าต่างหลักโดยตรง (ย้ำอีกรอบ)
        main_window.set_focus() # บังคับให้หน้าต่าง POS เด้งขึ้นมาข้างหน้า
        main_window.type_keys("{ENTER}")
        time.sleep(WAIT_TIME)

# ==================== 4. CORE ENGINE ====================

def run_utility_service(service_key, mode=1, use_search=False):
    """ฟังก์ชันหลัก: รวมการนำทาง ค้นหา และจัดการ Error"""
    service_title = S_CFG[service_key]
    print(f"\n{'='*50}\n[*] รายการ: {service_title} (Key: {service_key})")
    
    app = None
    try:
        # 1. เข้าหน้าหลัก เตรียมข้อมูลผู้ฝากส่ง
        if not utility_services_main_nav(): return

        # 2. เชื่อมต่อ Application
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        main_window = app.top_window()

        # 3. ถ้าเป็นรายการที่ต้องการการ Search (6-9)
        if use_search:
            print(f"[*] ค้นหารหัสรายการ: {service_title}")
            search_input = main_window.child_window(auto_id=S_CFG['SEARCH_EDIT_ID'], control_type="Edit")
            search_input.click_input()
            # เคลียร์ค่าเก่าก่อนพิมพ์ (Ctrl+A -> Backspace)
            search_input.type_keys("^a{BACKSPACE}")
            search_input.type_keys(service_title, with_spaces=True)
            search_input.type_keys("{ENTER}")
            time.sleep(1.5)
            
            # เช็คว่าเจอรายการนั้นบนหน้าจอไหม
            if not main_window.child_window(title=service_title, control_type="Text").exists(timeout=3):
                raise Exception(f"ค้นหารหัส {service_title} แล้วแต่ไม่ปรากฏในผลลัพธ์")

        # 4. ทำ Transaction ตาม Mode ที่กำหนด
        utility_services_transaction_logic(main_window, service_title, mode=mode)
        print(f"[V] SUCCESS: {service_title} เสร็จสมบูรณ์")

    except Exception as e:
        # แคปภาพหลักฐานเมื่อเกิด Error
        error_context = {"test_name": "Utility Services", "step_name": service_key, "error_message": str(e)}
        save_evidence_context(app, error_context)
        print(f"[X] FAILED: {service_key} -> {e}")

# ==================== 5. NAVIGATION FLOW ====================

def utility_services_main_nav():
    """เตรียมความพร้อมหน้าจอ Agency -> BaS -> กรอกเบอร์/ไปรษณีย์"""
    try:
        app = Application(backend="uia").connect(title_re=WINDOW_TITLE, timeout=10)
        win = app.top_window()
        
        # เข้าเมนู
        win.child_window(title=B_CFG['HOTKEY_AGENCY_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        win.child_window(title=B_CFG['HOTKEY_BaS_TITLE'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        
        # อ่านบัตรประชาชน
        win.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
        
        # กรอก ไปรษณีย์ และ เบอร์โทร (พร้อม Scroll ถ้าหาไม่เจอ)
        for ctrl_id, val, label in [
            (POSTAL_CODE_EDIT_AUTO_ID, POSTAL_CODE, "ไปรษณีย์"),
            (PHONE_EDIT_AUTO_ID, PHONE_NUMBER, "เบอร์โทรศัพท์")
        ]:
            target = win.child_window(auto_id=ctrl_id, control_type="Edit")
            if not target.exists(timeout=1):
                for _ in range(3):
                    force_scroll_down(win, CONFIG)
                    if target.exists(timeout=1): break
            
            if not target.exists():
                print(f"[X] ไม่พบช่อง {label}"); return False
            
            if not target.texts()[0].strip():
                target.click_input()
                win.type_keys(val)
            time.sleep(0.5)

        # กดถัดไปเพื่อไปหน้าเลือกรายการ
        win.child_window(title=B_CFG['NEXT_TITLE'], auto_id=B_CFG['ID_AUTO_ID'], control_type="Text").click_input()
        time.sleep(WAIT_TIME)
        return True
    except Exception as e:
        print(f"[X] Navigation Failed: {e}")
        return False

# ==================== 6. EXECUTION SECTION ====================

if __name__ == "__main__":
    # รายการ 1-3: คลิกรายการ -> คลิกถัดไป
    run_utility_service('UTILITY_1_TITLE', mode=1)
    run_utility_service('UTILITY_2_TITLE', mode=1)
    run_utility_service('UTILITY_3_TITLE', mode=1)
    
    # รายการ 4-5: คลิกรายการ -> กด ENTER
    run_utility_service('UTILITY_4_TITLE', mode=2)
    run_utility_service('UTILITY_5_TITLE', mode=2)
    
    # รายการ 6: ค้นหารหัส -> คลิกรายการ -> คลิกถัดไป
    run_utility_service('UTILITY_6_TITLE', mode=1, use_search=True)
    
    # รายการ 7: ค้นหารหัส -> กด ENTER (ตามที่คุณต้องการ)
    run_utility_service('UTILITY_7_TITLE', mode=2, use_search=True)
    
    # รายการ 8-9: ค้นหารหัส -> คลิกรายการ -> คลิกถัดไป
    run_utility_service('UTILITY_8_TITLE', mode=1, use_search=True)
    run_utility_service('UTILITY_9_TITLE', mode=1, use_search=True)

    print(f"\n{'='*50}\n[V] จบพาร์ท Utility Services ทั้งหมดแล้ว")