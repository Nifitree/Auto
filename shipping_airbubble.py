import configparser
from pywinauto.application import Application
from pywinauto import mouse
import time
import os
import sys
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
NEXT_TITLE = "ถัดไป" 

# Shipping Config (ดึงค่า WEIGHT_EDIT_ID ที่แก้แล้วมาจากไฟล์นี้)
S_CFG = CONFIG["SHIPPING_AIRBUBBLE"]

# ==================== 2. HELPERS ====================

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

def press_next(main_window):
    """ฟังก์ชันกดถัดไป"""
    print(f"[*] กดปุ่ม '{NEXT_TITLE}'")
    try:
        main_window.child_window(title=NEXT_TITLE, control_type="Text").click_input()
    except:
        main_window.type_keys("{ENTER}") 
    time.sleep(WAIT_TIME)

# ==================== 3. SHIPPING LOGIC ====================

def execute_shipping_flow(main_window):
    # --- Phase 1: เริ่มต้น (S -> ข้อมูลผู้ส่ง) ---
    print("[*] 1. กด S เข้าเมนู")
    main_window.type_keys(S_CFG['HOTKEY_S'])
    time.sleep(WAIT_TIME)

    print("[*] 2. อ่านบัตรประชาชน")
    main_window.child_window(title=ID_CARD_BUTTON_TITLE, control_type="Text").click_input()
    
    print("[*] 3. กรอกรหัสไปรษณีย์และเบอร์โทร")
    postal = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(postal, main_window): raise Exception("ไม่พบช่องไปรษณีย์")
    fill_if_empty(main_window, postal, POSTAL_CODE)

    phone = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(phone, main_window): raise Exception("ไม่พบช่องเบอร์โทร")
    fill_if_empty(main_window, phone, PHONE_NUMBER)

    press_next(main_window) # กดถัดไป (1)

    # --- Phase 2: เลือกเมนู (W -> A -> A) ---
    print("[*] 4. เลือกเมนู W -> A -> A")
    main_window.type_keys(S_CFG['HOTKEY_W'])
    time.sleep(1)
    main_window.type_keys(S_CFG['HOTKEY_A'])
    time.sleep(1)
    main_window.type_keys(S_CFG['HOTKEY_A'])
    time.sleep(1)

    press_next(main_window) # กดถัดไป (2)

    # --- Phase 3: กรอกน้ำหนัก ---
    # ใช้ ID: EG_WEIGHT_INPUT_ELEMENT จาก Config
    print(f"[*] 5. กรอกน้ำหนัก: {S_CFG['WEIGHT_VALUE']} (ID: {S_CFG['WEIGHT_EDIT_ID']})")
    weight_input = main_window.child_window(auto_id=S_CFG['WEIGHT_EDIT_ID'], control_type="Edit")
    
    if not scroll_until_found(weight_input, main_window): 
        raise Exception(f"ไม่พบช่องกรอกน้ำหนัก (ID: {S_CFG['WEIGHT_EDIT_ID']})")
        
    weight_input.click_input()
    main_window.type_keys(S_CFG['WEIGHT_VALUE'])
    
    press_next(main_window) # กดถัดไป (3)

    # --- Phase 4: รหัสไปรษณีย์ปลายทาง ---
    print(f"[*] 6. กรอกรหัสไปรษณีย์ปลายทาง: {POSTAL_CODE}")
    postal_dest = main_window.child_window(auto_id=POSTAL_CODE_EDIT_AUTO_ID, control_type="Edit")
    if not scroll_until_found(postal_dest, main_window): raise Exception("ไม่พบช่องไปรษณีย์ปลายทาง")
    fill_if_empty(main_window, postal_dest, POSTAL_CODE)

    press_next(main_window) # กดถัดไป (4)

    # --- Phase 5: ดำเนินการ (ENTER) -> A ---
    print("[*] 7. กดดำเนินการ (ENTER) และกด A")
    main_window.type_keys("{ENTER}")
    time.sleep(WAIT_TIME)
    main_window.type_keys(S_CFG['HOTKEY_A'])
    time.sleep(WAIT_TIME)

    # --- Phase 6: วงเงินประกัน ---
    print(f"[*] 8. กรอกวงเงินประกัน: {S_CFG['INSURANCE_AMOUNT']}")
    coverage_btn = main_window.child_window(auto_id=S_CFG['COVERAGE_ICON_ID']) # CoverageIcon
    if not scroll_until_found(coverage_btn, main_window): raise Exception("ไม่พบปุ่ม CoverageIcon")
    coverage_btn.click_input()
    main_window.type_keys(S_CFG['INSURANCE_AMOUNT'])

    press_next(main_window) # กดถัดไป (5)
    press_next(main_window) # กดถัดไป (6)

    # --- Phase 7: เมนู A อีกรอบ ---
    print("[*] 9. กด A")
    main_window.type_keys(S_CFG['HOTKEY_A'])
    time.sleep(1)

    press_next(main_window) # กดถัดไป (7)
    press_next(main_window) # กดถัดไป (8)

    # --- Phase 8: ค้นหาที่อยู่ ---
    print(f"[*] 10. ค้นหาที่อยู่: {S_CFG['ADDRESS_SEARCH_TERM']}")
    search_field = main_window.child_window(auto_id=S_CFG['SEARCH_FIELD_ID'], control_type="Edit") # SearchField1
    if not scroll_until_found(search_field, main_window): raise Exception("ไม่พบช่องค้นหาที่อยู่")
    search_field.click_input()
    main_window.type_keys(S_CFG['ADDRESS_SEARCH_TERM'])
    
    press_next(main_window) # กดถัดไป (9)

    # --- Phase 9: เลือก Title ที่อยู่ ---
    print(f"[*] 11. เลือกที่อยู่: {S_CFG['SELECTED_ADDRESS_TITLE']}")
    # 1/18ปทุมนาราม
    addr_title = main_window.child_window(title=S_CFG['SELECTED_ADDRESS_TITLE'], control_type="Text")
    if not scroll_until_found(addr_title, main_window): raise Exception(f"ไม่พบที่อยู่ {S_CFG['SELECTED_ADDRESS_TITLE']}")
    addr_title.click_input()

    # --- Phase 10: ข้อมูลลูกค้า (ชื่อ/นามสกุล/เบอร์) ---
    print("[*] 12. กรอกข้อมูลลูกค้า (ชื่อ, นามสกุล, เบอร์)")
    
    # ชื่อ
    name_input = main_window.child_window(auto_id=S_CFG['CUST_NAME_ID'], control_type="Edit")
    if not scroll_until_found(name_input, main_window): raise Exception("ไม่พบช่องชื่อลูกค้า")
    name_input.click_input()
    main_window.type_keys(S_CFG['CUSTOMER_NAME'])

    # นามสกุล
    lastname_input = main_window.child_window(auto_id=S_CFG['CUST_LASTNAME_ID'], control_type="Edit")
    lastname_input.click_input()
    main_window.type_keys(S_CFG['CUSTOMER_LASTNAME'])

    # เบอร์โทร
    phone_cust = main_window.child_window(auto_id=PHONE_EDIT_AUTO_ID, control_type="Edit")
    phone_cust.click_input()
    main_window.type_keys(PHONE_NUMBER)

    press_next(main_window) # กดถัดไป (10)
    press_next(main_window) # กดถัดไป (11)
    press_next(main_window) # กดถัดไป (12)

    # --- Phase 11: เสร็จสิ้น (Z) ---
    print("[*] 13. กดเสร็จสิ้น (Z)")
    main_window.type_keys(S_CFG['HOTKEY_Z'])
    time.sleep(WAIT_TIME)

# ==================== 4. ENGINE (STOP ON ERROR) ====================

def run_service():
    """Wrapper หลัก: รัน -> แคปภาพ -> หยุดเมื่อ Error"""
    step_name = "Shipping Airbubble Flow"
    app = None
    print(f"\n{'='*50}\n[*] เริ่มทำรายการ: {step_name}")

    try:
        app, main_window = connect_main_window()
        
        # รัน Logic ทั้งหมด
        execute_shipping_flow(main_window)
        
        print(f"[V] SUCCESS: {step_name} สำเร็จ")

    except Exception as e:
        print(f"\n[X] FAILED: {step_name} -> {e}")
        
        # แคปภาพ
        if app:
            try:
                save_evidence_context(app, {
                    "test_name": "Shipping Automation",
                    "step_name": step_name,
                    "error_message": str(e)
                })
                print("[/] บันทึกภาพ Error เรียบร้อย")
            except: pass
        
        # หยุดการทำงานทันที
        print("!!! หยุดการทำงาน (Stop Execution) !!!")
        sys.exit(1)

# ==================== 5. ENTRY POINT ====================

if __name__ == "__main__":
    run_service()